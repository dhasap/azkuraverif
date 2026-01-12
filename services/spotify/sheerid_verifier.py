import re
import json
import time
import random
import logging
from pathlib import Path
from io import BytesIO
from typing import Dict, Optional, Tuple

import httpx
from PIL import Image, ImageDraw, ImageFont

from .universities import UNIVERSITIES
from services.utils.anti_detect import get_headers, get_fingerprint, random_delay, create_session
from services.utils.email_client import EmailClient
from services.utils.document_generator import create_student_id_front, create_student_id_back, create_transcript_document, create_tuition_document
from services.utils.data_generator import generate_random_data
from services.utils.names import generate_name
from services.utils.id_card_helper import generate_student_id_card
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

# ============ CONFIG ============
PROGRAM_ID = "67c8c14f5f17a83b745e3f82"
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"
MIN_DELAY = 300
MAX_DELAY = 800


# ============ STATS TRACKING ============
class Stats:
    """Track success rates by organization"""
    
    def __init__(self):
        self.file = Path(__file__).parent / "stats.json"
        self.data = self._load()
    
    def _load(self) -> Dict:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except:
                pass
        return {"total": 0, "success": 0, "failed": 0, "orgs": {}}
    
    def _save(self):
        self.file.write_text(json.dumps(self.data, indent=2))
    
    def record(self, org: str, success: bool):
        self.data["total"] += 1
        self.data["success" if success else "failed"] += 1
        
        if org not in self.data["orgs"]:
            self.data["orgs"][org] = {"success": 0, "failed": 0}
        self.data["orgs"][org]["success" if success else "failed"] += 1
        self._save()
    
    def get_rate(self, org: str = None) -> float:
        if org:
            o = self.data["orgs"].get(org, {})
            total = o.get("success", 0) + o.get("failed", 0)
            return o.get("success", 0) / total * 100 if total else 50
        return self.data["success"] / self.data["total"] * 100 if self.data["total"] else 0


stats = Stats()


def select_university() -> Dict:
    """Weighted random selection based on success rates"""
    weights = []
    for uni in UNIVERSITIES:
        weight = uni["weight"] * (stats.get_rate(uni["name"]) / 50)
        weights.append(max(1, weight))
    
    total = sum(weights)
    r = random.uniform(0, total)
    
    cumulative = 0
    for uni, weight in zip(UNIVERSITIES, weights):
        cumulative += weight
        if r <= cumulative:
            return {**uni, "idExtended": str(uni["id"])}
    return {**UNIVERSITIES[0], "idExtended": str(UNIVERSITIES[0]["id"])}


def generate_email(first: str, last: str, domain: str) -> str:
    patterns = [
        f"{first[0].lower()}{last.lower()}{random.randint(100, 999)}",
        f"{first.lower()}.{last.lower()}{random.randint(10, 99)}",
        f"{last.lower()}{first[0].lower()}{random.randint(100, 999)}"
    ]
    return f"{random.choice(patterns)}@{domain}"


def generate_birth_date() -> str:
    year = random.randint(2000, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


# ============ VERIFIER ============
class SheerIDVerifier:
    """Spotify Student Verification with enhanced features"""
    
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.vid = self._parse_id(url)
        self.fingerprint = get_fingerprint()
        
        self.client, self.lib_name = create_session(proxy)
        self.org = None
    
    def __del__(self):
        if hasattr(self, "client"):
            try:
                self.client.close()
            except:
                pass

    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        # Handle raw ID (24 hex chars)
        if re.match(r"^[a-f0-9]{24}$", url, re.IGNORECASE):
            return url
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        """Ekstrak verification ID dari URL"""
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _request(self, method: str, endpoint: str, body: Dict = None) -> Tuple[Dict, int]:
        random_delay()
        try:
            # Get anti-detect headers
            headers = get_headers(for_sheerid=True)
            
            # Use request method of the session
            resp = self.client.request(method, f"{SHEERID_API_URL}{endpoint}", 
                                       json=body, headers=headers)
            
            # Handle different response objects (curl_cffi/requests vs httpx)
            if hasattr(resp, "json"):
                try:
                    data = resp.json()
                except:
                    data = {}
            else:
                data = {}
                
            return data, resp.status_code
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def _upload_s3(self, url: str, data: bytes) -> bool:
        try:
            # Menambahkan beberapa header tambahan untuk meningkatkan kemungkinan keberhasilan upload
            headers = {
                "Content-Type": "image/png",
                "Content-Length": str(len(data)),
                "Connection": "keep-alive",
                "Accept": "*/*",
            }
            # Gunakan 'data' alih-alih 'content' untuk kompatibilitas curl_cffi/requests
            resp = self.client.put(url, data=data, headers=headers, timeout=60)
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def check_link(self) -> Dict:
        """Check if verification link is valid"""
        if not self.vid:
            return {"valid": False, "error": "Invalid URL"}
        
        data, status = self._request("GET", f"/verification/{self.vid}")
        if status != 200:
            return {"valid": False, "error": f"HTTP {status}"}
        
        step = data.get("currentStep", "")
        if step == "collectStudentPersonalInfo":
            return {"valid": True, "step": step}
        elif step == "success":
            return {"valid": False, "error": "Already verified"}
        return {"valid": False, "error": f"Invalid step: {step}"}
    
    async def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
        email_config: Dict = None,
    ) -> Dict:
        """Run full verification (async wrapper for compatibility)"""
        return await self._verify_async(first_name, last_name, email, birth_date, school_id, email_config)
    
    async def _verify_async(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
        email_config: Dict = None,
    ) -> Dict:
        """Run full verification"""
        if not self.vid:
            return {"success": False, "message": "Invalid verification URL"}
        
        email_client = None
        try:
            # Tentukan gender untuk sinkronisasi nama dan foto
            gender = random.choice(["male", "female"])
            
            if not first_name or not last_name:
                first_name, last_name = generate_name(gender)
            
            if school_id:
                self.org = next((u for u in UNIVERSITIES if str(u["id"]) == school_id), None)
                if self.org:
                    self.org = {**self.org, "idExtended": str(self.org["id"])}
            
            if not self.org:
                self.org = select_university()
            
            if email_config and email_config.get("email_address"):
                email = email_config.get("email_address")
                email_client = EmailClient(email_config)
            else:
                email = email or generate_email(first_name, last_name, self.org["domain"])
            
            if not birth_date:
                birth_date = generate_birth_date()
            
            logger.info(f"Student: {first_name} {last_name} ({gender})")
            logger.info(f"Email: {email}")
            logger.info(f"School: {self.org['name']}")
            logger.info(f"ID: {self.vid[:20]}...")
            
            logger.info("Step 1: Generating student documents...")
            # Gunakan fungsi helper yang sudah support PRESET MANUAL & GENDER SYNC
            doc = generate_student_id_card(first_name, last_name, self.org, gender=gender)
            logger.info(f"Main document size: {len(doc)/1024:.1f} KB")

            logger.info("Step 2: Submitting student info...")
            body = {
                "firstName": first_name, "lastName": last_name, "birthDate": birth_date,
                "email": email, "phoneNumber": "",
                "organization": {"id": self.org["id"], "idExtended": self.org["idExtended"],
                                "name": self.org["name"]},
                "deviceFingerprintHash": self.fingerprint,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": False,
                    "verificationId": self.vid,
                    "refererUrl": f"https://services.sheerid.com/verify/{PROGRAM_ID}/?verificationId={self.vid}",
                    "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                }
            }

            data_response, status = self._request("POST", f"/verification/{self.vid}/step/collectStudentPersonalInfo", body)

            if status != 200:
                stats.record(self.org["name"], False)
                return {"success": False, "message": f"Submit failed: {status}"}

            if data_response.get("currentStep") == "error":
                stats.record(self.org["name"], False)
                return {"success": False, "message": f"Error: {data_response.get('errorIds', [])}"}

            logger.info(f"Current step: {data_response.get('currentStep')}")
            current_step = data_response.get("currentStep", "")

            if current_step in ["sso", "collectStudentPersonalInfo"]:
                logger.info("Step 3: Skipping SSO...")
                self._request("DELETE", f"/verification/{self.vid}/step/sso")

            logger.info("Step 4: Uploading document...")
            upload_body = {"files": [{"fileName": "student_card.png", "mimeType": "image/png", "fileSize": len(doc)}]}
            data_response, status = self._request("POST", f"/verification/{self.vid}/step/docUpload", upload_body)

            if not data_response.get("documents"):
                stats.record(self.org["name"], False)
                return {"success": False, "message": "No upload URL"}

            upload_url = data_response["documents"][0].get("uploadUrl")
            if not self._upload_s3(upload_url, doc):
                stats.record(self.org["name"], False)
                return {"success": False, "message": "Upload failed"}

            logger.info("Document uploaded!")

            logger.info("Step 5: Completing upload...")
            data_response, status = self._request("POST", f"/verification/{self.vid}/step/completeDocUpload")
            logger.info(f"Upload completed: {data_response.get('currentStep', 'pending')}")
            
            # Auto email loop
            if data.get("currentStep") == "emailLoop":
                if email_client:
                    logger.info("Entering email loop...")
                    for i in range(10):
                        link = email_client.wait_for_verification_link(self.vid)
                        if link:
                            match = re.search(r"emailToken=(\d+)", link)
                            if match:
                                token = match.group(1)
                                logger.info(f"Got email token: {token}")
                                data, _ = self._request("POST", f"/verification/{self.vid}/step/emailLoop", {
                                    "emailToken": token,
                                    "deviceFingerprintHash": self.fingerprint
                                })
                                break
                        await asyncio.sleep(5)
            
            stats.record(self.org["name"], True)
            
            return {
                "success": True,
                "pending": True,
                "message": "Dokumen terkirim. Cek email Spotify dalam 24-48 jam.",
                "verification_id": self.vid,
                "redirect_url": data.get("redirectUrl"),
                "status": data,
            }
            
        except Exception as e:
            if self.org:
                stats.record(self.org["name"], False)
            return {"success": False, "message": str(e), "verification_id": self.vid}
        finally:
            if email_client:
                email_client.close()


def main():
    import sys
    
    print("=" * 60)
    print("Spotify Student Verification Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter verification URL: ").strip()
    
    if not url or "sheerid.com" not in url:
        print("Invalid URL. Must contain sheerid.com")
        return
    
    verifier = SheerIDVerifier(url)
    
    check = verifier.check_link()
    if not check.get("valid"):
        print(f"Link Error: {check.get('error')}")
        return
    
    result = verifier._verify_sync()
    
    print()
    print("=" * 60)
    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Message: {result['message']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
