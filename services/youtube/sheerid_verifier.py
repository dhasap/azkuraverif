"""Program Utama Verifikasi Mahasiswa SheerID (YouTube Support)"""
import re
import random
import logging
import httpx
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_birth_date
from .img_generator import generate_image, generate_psu_email

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """Verifikator YouTube Premium SheerID (Async)"""

    def __init__(self, url: str):
        self.original_url = self.normalize_url(url)
        self.verification_id = self.parse_verification_id(self.original_url)
        self.device_fingerprint = self._generate_device_fingerprint()
        
        # Parse parameter lain dari URL jika ada (khusus YouTube)
        self.external_user_id = self.parse_query_param(self.original_url, "euid")

    @staticmethod
    def _generate_device_fingerprint() -> str:
        chars = "0123456789abcdef"
        return "".join(random.choice(chars) for _ in range(32))

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalisasi URL"""
        return url

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    @staticmethod
    def parse_query_param(url: str, param: str) -> Optional[str]:
        match = re.search(f"{param}=([^&]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    async def _create_verification_session(self, client: httpx.AsyncClient) -> str:
        """Membuat sesi verifikasi baru jika URL tidak mengandung ID (Auto-Session)"""
        logger.info("Membuat sesi verifikasi baru untuk YouTube...")
        
        # Payload untuk inisialisasi sesi
        # Program ID YouTube biasanya statis atau ada di config
        body = {
            "programId": config.PROGRAM_ID, 
            "trackingId": None,
            "installPageUrl": self.original_url
        }
        
        # Tambahkan externalUserId jika ada di URL (euid)
        # API SheerID menolak externalUserId di root body saat init session
        # Kita masukkan ke metadata agar tersimpan
        if self.external_user_id:
            body["metadata"] = {"externalUserId": self.external_user_id}

        try:
            # Gunakan endpoint global services.sheerid.com
            # Note: Kita asumsikan config.SHEERID_BASE_URL mengarah ke sana
            url = f"{config.SHEERID_BASE_URL}/rest/v2/verification"
            
            response = await client.post(url, json=body)
            if response.status_code != 200:
                # Fallback: Mungkin butuh endpoint spesifik YouTube?
                # Biasanya endpoint general ini cukup asalkan programId benar
                raise Exception(f"Gagal init sesi: {response.text}")
                
            data = response.json()
            if "verificationId" not in data:
                raise Exception("Response tidak berisi verificationId")
                
            self.verification_id = data["verificationId"]
            logger.info(f"✅ Sesi baru dibuat otomatis: {self.verification_id}")
            return self.verification_id
            
        except Exception as e:
            logger.error(f"Gagal membuat sesi otomatis: {e}")
            raise Exception("Gagal membuat sesi otomatis. Silakan isi form YouTube dulu di browser sampai muncul link yang ada 'verificationId='-nya, lalu kirim link itu.")

    async def _sheerid_request(
        self, client: httpx.AsyncClient, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """Mengirim request SheerID API (Async)"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            response = await client.request(
                method=method, url=url, json=body, headers=headers
            )
            try:
                data = response.json()
            except Exception:
                data = response.text
            return data, response.status_code
        except Exception as e:
            logger.error(f"Request SheerID gagal: {e}")
            raise

    async def _upload_to_s3(self, client: httpx.AsyncClient, upload_url: str, img_data: bytes) -> bool:
        """Upload PNG ke S3 (Async)"""
        try:
            headers = {"Content-Type": "image/png"}
            response = await client.put(
                upload_url, content=img_data, headers=headers, timeout=60.0
            )
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"Gagal upload S3: {e}")
            return False

    async def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
    ) -> Dict:
        """Menjalankan proses verifikasi (Async)"""
        try:
            current_step = "initial"

            if not first_name or not last_name:
                name = NameGenerator.generate()
                first_name = name["first_name"]
                last_name = name["last_name"]

            school_id = school_id or config.DEFAULT_SCHOOL_ID
            school = config.SCHOOLS[school_id]

            if not email:
                email = generate_psu_email(first_name, last_name)
            if not birth_date:
                birth_date = generate_birth_date()

            # Membuat PNG dokumen (Async)
            logger.info("Langkah 1/5: Membuat dokumen mahasiswa...")
            img_data = await generate_image(first_name, last_name, school_id)
            file_size = len(img_data)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 0. Cek apakah ID sudah ada, jika belum buat baru (Auto-Session)
                if not self.verification_id:
                    await self._create_verification_session(client)

                logger.info(f"Informasi: {first_name} {last_name}")
                logger.info(f"Email: {email}")
                logger.info(f"ID verifikasi: {self.verification_id}")

                # Mengirim informasi mahasiswa
                logger.info("Langkah 2/5: Mengirim informasi personal...")
                step2_body = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "birthDate": birth_date,
                    "email": email,
                    "phoneNumber": "", # Optional
                    "organization": {
                        "id": int(school_id),
                        "idExtended": school["idExtended"],
                        "name": school["name"],
                    },
                    "deviceFingerprintHash": self.device_fingerprint,
                    "locale": "en-US",
                    "metadata": {
                        "marketConsentValue": False,
                        "refererUrl": self.original_url,
                        "verificationId": self.verification_id,
                        "submissionOptIn": "By submitting..."
                    },
                }
                
                # Tambahkan externalUserId jika ada (penting untuk YouTube agar akun terhubung)
                if self.external_user_id:
                    step2_body["externalUserId"] = self.external_user_id
                    step2_body["metadata"]["externalUserId"] = self.external_user_id

                step2_data, step2_status = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectStudentPersonalInfo",
                    step2_body,
                )

                if step2_status == 400 and "invalidStep" in str(step2_data):
                    raise Exception("Sesi kadaluarsa atau invalid. Coba refresh link YouTube Anda dan ambil link baru.")

                if step2_status != 200:
                    error_msg = str(step2_data)
                    if isinstance(step2_data, dict) and "message" in step2_data:
                         error_msg = step2_data['message']
                    raise Exception(f"Gagal langkah 2: {error_msg}")

                current_step = step2_data.get("currentStep", current_step) if isinstance(step2_data, dict) else current_step
                logger.info(f"✅ Langkah 2 selesai: {current_step}")

                # Lewati SSO (jika diperlukan)
                if current_step in ["sso", "collectStudentPersonalInfo"]:
                    logger.info("Langkah 3/5: Melewati verifikasi SSO...")
                    step3_data, _ = await self._sheerid_request(
                        client,
                        "DELETE",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                    )
                    current_step = step3_data.get("currentStep", current_step) if isinstance(step3_data, dict) else current_step

                # Request upload dan upload dokumen
                logger.info("Langkah 4/5: Meminta URL upload ...")
                
                step4_body = {
                    "files": [
                         {
                            "fileName": "student_card.png",
                            "mimeType": "image/png",
                            "fileSize": file_size
                         }
                    ]
                }
                
                step4_data, step4_status = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                    step4_body,
                )
                
                if step4_status != 200 or not step4_data.get("documents"):
                     raise Exception("Gagal mendapatkan URL Upload")

                documents = step4_data["documents"]
                upload_url = documents[0]["uploadUrl"]
                
                # Upload ke S3
                if not await self._upload_to_s3(client, upload_url, img_data):
                    raise Exception("Gagal upload file ke S3")
                logger.info("✅ File terupload")

                # Complete Upload
                step6_data, _ = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
                )
                
                final_status = step6_data
                
                # Cek status akhir
                return {
                    "success": True,
                    "pending": True, # Biasanya pending review
                    "message": "Dokumen terkirim. Cek email YouTube dalam 20 menit.",
                    "verification_id": self.verification_id,
                    "redirect_url": final_status.get("redirectUrl") if isinstance(final_status, dict) else None,
                    "status": final_status,
                }

        except Exception as e:
            logger.error(f"❌ Verifikasi gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """Fungsi utama - Interface command line"""
    import sys
    import asyncio

    print("=" * 60)
    print("Tool Verifikasi Identitas Mahasiswa SheerID (YouTube Support)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan URL YouTube/SheerID: ").strip()

    if not url:
        print("❌ Error: URL tidak diberikan")
        sys.exit(1)

    verifier = SheerIDVerifier(url)
    
    # Run async verify
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(verifier.verify())
    finally:
        loop.close()

    print()
    print("=" * 60)
    print("Hasil Verifikasi:")
    print("=" * 60)
    print(f"Status: {'✅ Berhasil' if result['success'] else '❌ Gagal'}")
    print(f"Pesan: {result['message']}")
    if result.get("redirect_url"):
        print(f"Redirect URL: {result['redirect_url']}")
    print("=" * 60)

    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())