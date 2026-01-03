"""Program Utama Verifikasi Militer SheerID - Smart Step Discovery"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_email, generate_birth_date, generate_discharge_date
from .img_generator import generate_military_png

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class SheerIDVerifier:
    """Verifikator Identitas Militer SheerID (Async)"""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self._generate_device_fingerprint()

    @staticmethod
    def _generate_device_fingerprint() -> str:
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    async def _sheerid_request(
        self, client: httpx.AsyncClient, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        headers = {"Content-Type": "application/json"}
        try:
            response = await client.request(method=method, url=url, json=body, headers=headers)
            try:
                data = response.json()
            except Exception:
                data = response.text
            return data, response.status_code
        except Exception as e:
            logger.error(f"Request SheerID gagal: {e}")
            raise

    async def _upload_to_s3(self, client: httpx.AsyncClient, upload_url: str, img_data: bytes) -> bool:
        try:
            headers = {"Content-Type": "image/png"}
            response = await client.put(upload_url, content=img_data, headers=headers, timeout=60.0)
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"Upload S3 gagal: {e}")
            return False

    async def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        branch: str = None,
        discharge_date: str = None,
        **kwargs # Menampung data lain dari database
    ) -> Dict:
        try:
            # 1. Siapkan Data
            name_gen = NameGenerator.generate()
            first_name = first_name or name_gen["first_name"]
            last_name = last_name or name_gen["last_name"]
            email = email or generate_email(first_name, last_name)
            birth_date = birth_date or generate_birth_date()
            discharge_date = discharge_date or generate_discharge_date()
            branch = branch or config.DEFAULT_BRANCH
            # Military Status sesuai list ChatGPT tadi
            military_status = 'MILITARY_VETERAN_RETIREE'

            logger.info(f"ID Verifikasi: {self.verification_id}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                # 2. DISCOVERY: Cek langkah saat ini dan langkah yang tersedia
                logger.info("Mengecek status verifikasi...")
                v_data, v_status = await self._sheerid_request(
                    client, "GET", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}"
                )
                
                if v_status != 200:
                    raise Exception(f"Gagal mengambil info verifikasi (404/Basi). Gunakan LINK FRESH.")

                current_step = v_data.get("currentStep")
                logger.info(f"Langkah saat ini: {current_step}")

                # Jika sudah di tahap upload dokumen, kita bisa langsung upload
                # Tapi biasanya kita mulai dari collectPersonalInfo
                
                # Nama endpoint dinamis berdasarkan currentStep
                # ChatGPT Veteran biasanya: collectMilitaryPersonalInfo
                step_endpoint = current_step
                
                # Payload data personal
                step_body = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "birthDate": birth_date,
                    "email": email,
                    "deviceFingerprintHash": self.device_fingerprint,
                    "locale": "en-US",
                    "militaryStatus": military_status,
                    "militaryBranch": branch,
                    "dischargeDate": discharge_date,
                    "metadata": {
                        "verificationId": self.verification_id,
                    },
                }

                # 3. Kirim Data Personal (Submit Form)
                logger.info(f"Mengirim data ke langkah: {step_endpoint}...")
                res_data, res_status = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/{step_endpoint}",
                    step_body,
                )

                if res_status != 200:
                    # Cek jika errornya karena step salah
                    if res_status == 404:
                         raise Exception(f"Langkah '{step_endpoint}' tidak ditemukan. SheerID mungkin mengubah strukturnya.")
                    raise Exception(f"Submit data gagal ({res_status}): {res_data}")

                current_step = res_data.get("currentStep")
                logger.info(f"Langkah selanjutnya: {current_step}")

                # 4. Skip SSO jika muncul
                if current_step == "sso":
                    logger.info("Melewati SSO...")
                    res_data, _ = await self._sheerid_request(
                        client, "DELETE", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso"
                    )
                    current_step = res_data.get("currentStep")

                # 5. Generate & Upload Dokumen
                if current_step == "docUpload":
                    logger.info("Membuat dokumen DD-214...")
                    img_data = await generate_military_png(first_name, last_name, birth_date, discharge_date, branch)
                    
                    logger.info("Meminta URL upload...")
                    up_data, up_status = await self._sheerid_request(
                        client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                        {"files": [{"fileName": "dd214.png", "mimeType": "image/png", "fileSize": len(img_data)}]}
                    )
                    
                    if not up_data.get("documents"):
                        raise Exception("Gagal mendapatkan URL upload dokumen.")

                    upload_url = up_data["documents"][0]["uploadUrl"]
                    if await self._upload_to_s3(client, upload_url, img_data):
                        logger.info("Upload dokumen berhasil.")
                        # Selesaikan upload
                        await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload"
                        )
                    else:
                        raise Exception("Gagal upload dokumen ke S3.")

            return {
                "success": True,
                "pending": True,
                "message": "Data & Dokumen DD-214 berhasil dikirim. Menunggu review.",
                "verification_id": self.verification_id
            }

        except Exception as e:
            logger.error(f"❌ Verifikasi gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}