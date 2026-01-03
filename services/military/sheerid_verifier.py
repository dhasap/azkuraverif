"""Program Utama Verifikasi Militer SheerID"""
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
    def normalize_url(url: str) -> str:
        return url

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
        status: str = None,
        branch: str = None,
        discharge_date: str = None
    ) -> Dict:
        try:
            current_step = "initial"

            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            if not email:
                email = generate_email(first_name, last_name)
            if not birth_date:
                birth_date = generate_birth_date()
            if not discharge_date:
                discharge_date = generate_discharge_date()
            
            status = status or config.DEFAULT_STATUS
            branch = branch or config.DEFAULT_BRANCH

            logger.info(f"Informasi Militer: {first_name} {last_name}")
            logger.info(f"Status: {status} | Branch: {branch}")
            logger.info(f"Discharge: {discharge_date}")
            logger.info(f"ID Verifikasi: {self.verification_id}")

            # 1. Buat Dokumen DD-214
            logger.info("Langkah 1/4: Membuat dokumen DD-214...")
            img_data = await generate_military_png(first_name, last_name, birth_date, discharge_date, branch)
            file_size = len(img_data)
            logger.info(f"✅ Ukuran PNG: {file_size / 1024:.2f}KB")

            async with httpx.AsyncClient(timeout=30.0) as client:
                # 2. Kirim Informasi Personal
                logger.info("Langkah 2/4: Mengirim informasi militer...")
                
                # Payload untuk Military biasanya sedikit berbeda
                # Perlu cek apakah endpointnya collectMilitaryPersonalInfo
                step2_body = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "birthDate": birth_date,
                    "email": email,
                    "phoneNumber": "", # Optional biasanya
                    "deviceFingerprintHash": self.device_fingerprint,
                    "locale": "en-US",
                    
                                    # Kolom khusus Military (SheerID API keys)
                                    "militaryStatus": status,  # MILITARY_VETERAN_RETIREE
                                    "militaryBranch": branch,  # ARMY
                                    "dischargeDate": discharge_date, # YYYY-MM-DD                    
                    "metadata": {
                        "marketConsentValue": False,
                        "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                        "verificationId": self.verification_id,
                        "submissionOptIn": "By submitting the personal information above, I acknowledge..."
                    },
                }

                step2_data, step2_status = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryPersonalInfo",
                    step2_body,
                )
                
                # Handle error 400 (Invalid Step / Link Basi)
                if step2_status == 400 and "invalidStep" in str(step2_data):
                     raise Exception("Link tidak valid/sudah terpakai. Pastikan link FRESH (Formulir belum diisi).")

                if step2_status != 200:
                    raise Exception(f"Langkah 2 gagal (kode status {step2_status}): {step2_data}")
                
                if step2_data.get("currentStep") == "error":
                    error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                    raise Exception(f"Langkah 2 error: {error_msg}")

                logger.info(f"✅ Langkah 2 selesai: {step2_data.get('currentStep')}")
                current_step = step2_data.get("currentStep", current_step)

                # 3. Handle SSO override (jarang di military tapi jaga-jaga)
                if current_step == "sso":
                    logger.info("Langkah 3: Skip SSO...")
                    step3_data, _ = await self._sheerid_request(
                        client, "DELETE", 
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso"
                    )
                    current_step = step3_data.get("currentStep", current_step)

                # 4. Upload Dokumen
                logger.info("Langkah 4/4: Upload dokumen...")
                step4_body = {
                    "files": [
                        {"fileName": "dd214.png", "mimeType": "image/png", "fileSize": file_size}
                    ]
                }
                step4_data, step4_status = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                    step4_body,
                )
                
                if not step4_data.get("documents"):
                    raise Exception("Tidak bisa mendapatkan URL upload")

                upload_url = step4_data["documents"][0]["uploadUrl"]
                if not await self._upload_to_s3(client, upload_url, img_data):
                    raise Exception("Upload S3 gagal")
                
                # Complete Upload
                step6_data, _ = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
                )
                final_status = step6_data

            return {
                "success": True,
                "pending": True,
                "message": "Dokumen DD-214 dikirim, menunggu review.",
                "verification_id": self.verification_id,
                "redirect_url": final_status.get("redirectUrl"),
                "status": final_status,
            }

        except Exception as e:
            logger.error(f"❌ Verifikasi gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}
