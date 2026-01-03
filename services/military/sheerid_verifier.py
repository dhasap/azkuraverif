"""Program Utama Verifikasi Militer SheerID - Multi-Step with Search logic"""
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

    async def _search_organization(self, client: httpx.AsyncClient, search_term: str) -> Dict:
        """Mencari Organisasi Militer dan mengembalikan objek lengkapnya"""
        try:
            url = f"{config.SHEERID_BASE_URL}/rest/v2/organization/search"
            params = {'searchTerm': search_term, 'type': 'MILITARY'} 
            
            response = await client.get(url, params=params)
            if response.status_code == 200:
                results = response.json()
                if results and isinstance(results, list) and len(results) > 0:
                    return results[0]
            
            # Fallback
            params.pop('type', None)
            response = await client.get(url, params=params)
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    return results[0]

            raise Exception(f"Organisasi '{search_term}' tidak ditemukan.")
        except Exception as e:
            logger.error(f"Error search org: {e}")
            raise

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
            
            branch_key = branch or config.DEFAULT_BRANCH
            military_status = 'VETERAN'

            async with httpx.AsyncClient(timeout=30.0) as client:
                # 2. Loop Langkah
                for _ in range(10):
                    v_data, v_status = await self._sheerid_request(
                        client, "GET", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}"
                    )
                    
                    if v_status != 200:
                        raise Exception("ID Verifikasi tidak ditemukan atau kadaluarsa.")

                    current_step = v_data.get("currentStep")
                    logger.info(f"Proses Langkah: {current_step}")

                    if current_step in ["success", "pending", "docReview"]:
                        break

                    # A. Pilih Status
                    if current_step == "collectMilitaryStatus":
                        await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus",
                            {"status": military_status}
                        )

                    # B. Isi Data Personal
                    elif current_step in ["collectMilitaryPersonalInfo", "collectInactiveMilitaryPersonalInfo", "collectActiveMilitaryPersonalInfo"]:
                        search_keyword = branch_key
                        if "Army" in branch_key: search_keyword = "Army"
                        elif "Navy" in branch_key: search_keyword = "Navy"
                        elif "Air Force" in branch_key: search_keyword = "Air Force"
                        elif "Marines" in branch_key: search_keyword = "Marine Corps"
                        
                        logger.info(f"Mencari organisasi: {search_keyword}...")
                        org_object = await self._search_organization(client, search_keyword)

                        payload = {
                            "firstName": first_name,
                            "lastName": last_name,
                            "birthDate": birth_date,
                            "email": email,
                            "organization": org_object,
                            "status": military_status,
                            "dischargeDate": discharge_date,
                            "deviceFingerprintHash": self.device_fingerprint,
                            "locale": "en-US"
                        }
                        
                        res_data, res_status = await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/{current_step}",
                            payload
                        )
                        if res_status != 200:
                            raise Exception(f"Gagal isi data diri ({res_status}): {res_data}")

                    # C. Skip SSO
                    elif current_step == "sso":
                        await self._sheerid_request(
                            client, "DELETE", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso"
                        )

                    # D. Upload Dokumen
                    elif current_step == "docUpload":
                        img_data = await generate_military_png(first_name, last_name, birth_date, discharge_date, branch_key.upper().replace(' ', '_'))
                        
                        up_res, _ = await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                            {"files": [{"fileName": "dd214.png", "mimeType": "image/png", "fileSize": len(img_data)}]}
                        )
                        
                        if not up_res.get("documents"):
                            raise Exception("Gagal mendapatkan URL upload dokumen.")

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
                "message": "Data & Dokumen DD-214 berhasil dikirim. Menunggu review.",
                "verification_id": self.verification_id
            }

        except Exception as e:
            logger.error(f"❌ Verifikasi gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}