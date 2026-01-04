"""Program Utama Verifikasi Mahasiswa SheerID"""
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
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SheerIDVerifier:
    """Verifikator Identitas Mahasiswa SheerID (Async - One)"""

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
        """Kirim request SheerID API (Async)"""
        headers = {
            "Content-Type": "application/json",
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
            logger.error(f"Upload S3 gagal: {e}")
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

            if not school_id:
                school = config.get_random_school()
                school_id = str(school['id'])
            else:
                school = config.SCHOOLS.get(school_id) or config.SCHOOLS[config.DEFAULT_SCHOOL_ID]

            if not email:
                email = generate_psu_email(first_name, last_name)
            if not birth_date:
                birth_date = generate_birth_date()

            logger.info(f"Informasi mahasiswa: {first_name} {last_name}")
            logger.info(f"Email: {email}")
            logger.info(f"Sekolah: {school['name']}")
            logger.info(f"ID Verifikasi: {self.verification_id}")

            # Buat kartu mahasiswa PNG (Async)
            logger.info("Langkah 1/4: Membuat kartu mahasiswa PNG...")
            img_data = await generate_image(first_name, last_name, school_id)
            file_size = len(img_data)
            logger.info(f"✅ Ukuran PNG: {file_size / 1024:.2f}KB")

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Kirim informasi mahasiswa
                logger.info("Langkah 2/4: Mengirim informasi mahasiswa...")
                step2_body = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "birthDate": birth_date,
                    "email": email,
                    "phoneNumber": "",
                    "organization": {
                        "id": int(school_id),
                        "idExtended": school["idExtended"],
                        "name": school["name"],
                    },
                    "deviceFingerprintHash": self.device_fingerprint,
                    "locale": "en-US",
                    "metadata": {
                        "marketConsentValue": False,
                        "verificationId": self.verification_id,
                        "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                        "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                        "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                    },
                }

                step2_data, step2_status = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectStudentPersonalInfo",
                    step2_body,
                )

                if step2_status == 400 and "invalidStep" in str(step2_data):
                    raise Exception("Link tidak valid/sudah terpakai. Pastikan Anda menyalin link SAAT FORMULIR MASIH KOSONG (belum diisi nama/email).")

                if step2_status != 200:
                    raise Exception(f"Langkah 2 gagal (kode status {step2_status}): {step2_data}")
                if step2_data.get("currentStep") == "error":
                    error_msg = ", ".join(step2_data.get("errorIds", ["Unknown error"]))
                    raise Exception(f"Langkah 2 error: {error_msg}")

                logger.info(f"✅ Langkah 2 selesai: {step2_data.get('currentStep')}")
                current_step = step2_data.get('currentStep', current_step)

                # Lewati SSO (jika diperlukan)
                if current_step in ["sso", "collectStudentPersonalInfo"]:
                    logger.info("Langkah 3/4: Melewati verifikasi SSO...")
                    step3_data, _ = await self._sheerid_request(
                        client,
                        "DELETE",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso",
                    )
                    logger.info(f"✅ Langkah 3 selesai: {step3_data.get('currentStep')}")
                    current_step = step3_data.get("currentStep", current_step)

                # Upload dokumen dan selesaikan pengiriman
                logger.info("Langkah 4/4: Request dan upload dokumen...")
                step4_body = {
                    "files": [
                        {"fileName": "student_card.png", "mimeType": "image/png", "fileSize": file_size}
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
                logger.info("✅ Berhasil mendapat URL upload")
                if not await self._upload_to_s3(client, upload_url, img_data):
                    raise Exception("Upload S3 gagal")
                logger.info("✅ Kartu mahasiswa berhasil diupload")

                step6_data, _ = await self._sheerid_request(
                    client,
                    "POST",
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload",
                )
                logger.info(f"✅ Dokumen selesai dikirim: {step6_data.get('currentStep')}")
                final_status = step6_data

            # Tidak lakukan polling status, langsung return menunggu review
            return {
                "success": True,
                "pending": True,
                "message": "Dokumen sudah dikirim, menunggu review",
                "verification_id": self.verification_id,
                "redirect_url": final_status.get("redirectUrl"),
                "status": final_status,
            }

        except Exception as e:
            logger.error(f"❌ Verifikasi gagal: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}


def main():
    """Fungsi utama - Interface command line"""
    import sys

    print("=" * 60)
    print("Tool Verifikasi Identitas Mahasiswa SheerID (Versi Python)")
    print("=" * 60)
    print()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Masukkan URL verifikasi SheerID: ").strip()

    if not url:
        print("❌ Error: URL tidak diberikan")
        sys.exit(1)

    verification_id = SheerIDVerifier.parse_verification_id(url)
    if not verification_id:
        print("❌ Error: Format ID verifikasi tidak valid")
        sys.exit(1)

    print(f"✅ Berhasil parse ID verifikasi: {verification_id}")
    print()

    verifier = SheerIDVerifier(verification_id)
    result = verifier.verify()

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
