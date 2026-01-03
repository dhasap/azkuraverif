"""Program Utama Verifikasi Militer SheerID - Multi-Step Logic"""
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
        **kwargs
    ) -> Dict:
        try:
            # 1. Persiapan Data
            name_gen = NameGenerator.generate()
            first_name = first_name or name_gen["first_name"]
            last_name = last_name or name_gen["last_name"]
            email = email or generate_email(first_name, last_name)
            birth_date = birth_date or generate_birth_date()
            discharge_date = discharge_date or generate_discharge_date()
            branch = branch or config.DEFAULT_BRANCH
            military_status = 'VETERAN'

            async with httpx.AsyncClient(timeout=30.0) as client:
                # 2. Loop Langkah (Max 10 steps to prevent infinite loop)
                for _ in range(10):
                    v_data, v_status = await self._sheerid_request(
                        client, "GET", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}"
                    )
                    
                    if v_status != 200:
                        raise Exception("ID Verifikasi tidak ditemukan atau kadaluarsa.")

                    current_step = v_data.get("currentStep")
                    logger.info(f"Proses Langkah: {current_step}")

                    # A. Selesai
                    if current_step in ["success", "pending", "docReview"]:
                        break

                    # B. Tahap Pilih Status (Hanya kirim 'status')
                    if current_step == "collectMilitaryStatus":
                        res_data, res_status = await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus",
                            {"status": military_status}
                        )
                        if res_status != 200:
                            raise Exception(f"Gagal set status ({res_status}): {res_data}")

                    # C. Tahap Isi Data Personal
                    elif current_step == "collectMilitaryPersonalInfo":
                        payload = {
                            "firstName": first_name,
                            "lastName": last_name,
                            "birthDate": birth_date,
                            "email": email,
                            "militaryBranch": branch,
                            "dischargeDate": discharge_date,
                            "deviceFingerprintHash": self.device_fingerprint,
                            "locale": "en-US"
                        }
                        res_data, res_status = await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryPersonalInfo",
                            payload
                        )
                        if res_status != 200:
                            raise Exception(f"Gagal isi data diri ({res_status}): {res_data}")

                    # D. Tahap Skip SSO
                    elif current_step == "sso":
                        await self._sheerid_request(
                            client, "DELETE", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso"
                        )

                    # E. Tahap Upload Dokumen
                    elif current_step == "docUpload":
                        img_data = await generate_military_png(first_name, last_name, birth_date, discharge_date, branch)
                        up_res, _ = await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                            {"files": [{"fileName": "dd214.png", "mimeType": "image/png", "fileSize": len(img_data)}]}
                        )
                        upload_url = up_res["documents"][0]["uploadUrl"]
                        if await self._upload_to_s3(client, upload_url, img_data):
                            await self._sheerid_request(
                                client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload"
                            )
                        break
                    
                    else:
                        logger.warning(f"Langkah tidak dikenal: {current_step}")
                        break

            return {
                "success": True,
                "message": "Data & Dokumen DD-214 berhasil dikirim.",
                "verification_id": self.verification_id
            }

        except Exception as e:
            logger.error(f"❌ Verifikasi gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}
