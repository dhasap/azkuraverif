"""
Bolt.new Teacher Verification Tool
SheerID Teacher Verification for Bolt.new

Author: ThanhNguyxn
"""

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
PROGRAM_ID = "68cc6a2e64f55220de204448"
SHEERID_BASE_URL = "https://services.sheerid.com"
MY_SHEERID_URL = "https://my.sheerid.com"
MIN_DELAY = 300
MAX_DELAY = 800

# Universities 
UNIVERSITIES = [
    {"id": 2565, "name": "Pennsylvania State University-Main Campus", "domain": "psu.edu", "weight": 100},
    {"id": 3499, "name": "University of California, Los Angeles", "domain": "ucla.edu", "weight": 98},
    {"id": 3491, "name": "University of California, Berkeley", "domain": "berkeley.edu", "weight": 97},
    {"id": 1953, "name": "Massachusetts Institute of Technology", "domain": "mit.edu", "weight": 95},
    {"id": 3113, "name": "Stanford University", "domain": "stanford.edu", "weight": 95},
    {"id": 2285, "name": "New York University", "domain": "nyu.edu", "weight": 94},
    {"id": 1426, "name": "Harvard University", "domain": "harvard.edu", "weight": 92},
    {"id": 698, "name": "Columbia University", "domain": "columbia.edu", "weight": 92},
    {"id": 3568, "name": "University of Michigan", "domain": "umich.edu", "weight": 93},
    {"id": 3686, "name": "University of Texas at Austin", "domain": "utexas.edu", "weight": 92},
    {"id": 1217, "name": "Georgia Institute of Technology", "domain": "gatech.edu", "weight": 91},
    {"id": 602, "name": "Carnegie Mellon University", "domain": "cmu.edu", "weight": 90},
    {"id": 328355, "name": "University of Toronto", "domain": "utoronto.ca", "weight": 85},
    {"id": 273409, "name": "University of Oxford", "domain": "ox.ac.uk", "weight": 85},
    {"id": 273378, "name": "University of Cambridge", "domain": "cam.ac.uk", "weight": 85},
]


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


def select_university() -> Dict:
    """Weighted random selection of university"""
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
            return {"id": uni["id"], "idExtended": str(uni["id"]), "name": uni["name"], "domain": uni["domain"]}
    return {"id": UNIVERSITIES[0]["id"], "idExtended": str(UNIVERSITIES[0]["id"]), "name": UNIVERSITIES[0]["name"], "domain": UNIVERSITIES[0]["domain"]}


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
    suffix = random.randint(100, 999)
    return f"{first[0].lower()}{last.lower()}{suffix}@{domain}"


def generate_birth_date() -> str:
    year = random.randint(1970, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


# ============ IMAGE GENERATOR ============
def generate_teacher_document(first: str, last: str, school: str) -> bytes:
    """Generate fake teacher certificate PNG"""
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 32)
        text_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        title_font = text_font = small_font = ImageFont.load_default()
    
    draw.rectangle([(20, 20), (width-20, height-20)], outline=(0, 51, 102), width=3)
    
    title = "FACULTY EMPLOYMENT VERIFICATION"
    draw.text((width//2, 60), title, fill=(0, 51, 102), font=title_font, anchor="mm")
    
    draw.line([(50, 100), (width-50, 100)], fill=(0, 51, 102), width=2)
    
    draw.text((width//2, 140), school, fill=(51, 51, 51), font=text_font, anchor="mm")
    
    y = 200
    info_lines = [
        f"Employee Name: {first} {last}",
        f"Position: Faculty Member",
        f"Department: Education",
        f"Employment Status: Active",
        f"Issue Date: {time.strftime('%B %d, %Y')}"
    ]
    
    for line in info_lines:
        draw.text((100, y), line, fill=(51, 51, 51), font=text_font)
        y += 40
    
    draw.text((width//2, height-60), "This document verifies current employment status.", 
              fill=(128, 128, 128), font=small_font, anchor="mm")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# ============ VERIFIER ============
class SheerIDVerifier:
    """Bolt.new Teacher Verification"""
    
    def __init__(self, url: str, verification_id: str = None, proxy: str = None):
        self.url = url
        self.vid = verification_id or self._parse_id(url)
        self.external_user_id = self._parse_external_user_id(url)
        self.fingerprint = get_fingerprint()
        
        self.client, self.lib_name = create_session(proxy)
        self.org = None
    
    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()
    
    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    @staticmethod
    def _parse_external_user_id(url: str) -> Optional[str]:
        match = re.search(r"externalUserId=([^&]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _request(self, method: str, url: str, body: Dict = None) -> Tuple[Dict, int]:
        random_delay()
        try:
            headers = get_headers(for_sheerid=True)
            resp = self.client.request(method, url, json=body, headers=headers)
            
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
    
    def _create_verification(self) -> str:
        """Create new verification session"""
        body = {
            "programId": PROGRAM_ID,
            "installPageUrl": self.url,
        }
        data, status = self._request("POST", f"{MY_SHEERID_URL}/rest/v2/verification/", body)
        if status != 200 or not data.get("verificationId"):
            raise Exception(f"Failed to create verification: {status}")
        self.vid = data["verificationId"]
        logger.info(f"Got verificationId: {self.vid}")
        return self.vid
    
    def check_link(self) -> Dict:
        if not self.vid:
            return {"valid": False, "error": "Invalid URL - no verificationId"}
        
        data, status = self._request("GET", f"{SHEERID_BASE_URL}/rest/v2/verification/{self.vid}")
        if status != 200:
            return {"valid": False, "error": f"HTTP {status}"}
        
        step = data.get("currentStep", "")
        valid_steps = ["collectTeacherPersonalInfo", "docUpload", "sso"]
        if step in valid_steps:
            return {"valid": True, "step": step}
        elif step == "success":
            return {"valid": False, "error": "Already verified"}
        elif step == "pending":
            return {"valid": False, "error": "Already pending review"}
        return {"valid": False, "error": f"Invalid step: {step}"}
    
    async def verify(self, email_config: Dict = None, **kwargs) -> Dict:
        """Async wrapper for compatibility"""
        return await self._verify_async(email_config)
    
    async def _verify_async(self, email_config: Dict = None) -> Dict:
        email_client = None
        try:
            if not self.vid:
                self._create_verification()
            
            if not self.external_user_id:
                self.external_user_id = str(random.randint(1000000, 9999999))
            
            first, last = generate_name()
            self.org = select_university()
            
            if email_config and email_config.get("email_address"):
                email = email_config.get("email_address")
                email_client = EmailClient(email_config)
            else:
                email = generate_email(first, last, self.org["domain"])
            
            logger.info(f"Teacher: {first} {last}")
            logger.info(f"Email: {email}")
            logger.info(f"School: {self.org['name']}")
            logger.info(f"ID: {self.vid[:20]}...")
            
            logger.info("Step 1: Generating teacher document...")
            doc = generate_teacher_document(first, last, self.org["name"])
            logger.info(f"Size: {len(doc)/1024:.1f} KB")
            
            logger.info("Step 2: Submitting teacher info...")
            body = {
                "firstName": first, "lastName": last, "birthDate": "",
                "email": email, "phoneNumber": "",
                "organization": {"id": self.org["id"], "idExtended": self.org["idExtended"], 
                                "name": self.org["name"]},
                "deviceFingerprintHash": self.fingerprint,
                "externalUserId": self.external_user_id,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": True,
                    "refererUrl": self.url,
                    "externalUserId": self.external_user_id,
                    "flags": '{"doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","include-cvec-field-france-student":"not-labeled-optional","org-search-overlay":"default","org-selected-display":"default"}',
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                }
            }
            
            data, status = self._request("POST", f"{SHEERID_BASE_URL}/rest/v2/verification/{self.vid}/step/collectTeacherPersonalInfo", body)
            
            if status != 200:
                stats.record(self.org["name"], False)
                return {"success": False, "message": f"Submit failed: {status}"}
            
            if isinstance(data, dict) and data.get("currentStep") == "error":
                stats.record(self.org["name"], False)
                return {"success": False, "message": f"Error: {data.get('errorIds', [])}"}
            
            current_step = data.get("currentStep", "") if isinstance(data, dict) else ""
            logger.info(f"Current step: {current_step}")
            
            if current_step in ["sso", "collectTeacherPersonalInfo"]:
                logger.info("Step 3: Skipping SSO...")
                self._request("DELETE", f"{SHEERID_BASE_URL}/rest/v2/verification/{self.vid}/step/sso")
            
            logger.info("Step 4: Uploading document...")
            upload_body = {"files": [{"fileName": "teacher_certificate.png", "mimeType": "image/png", "fileSize": len(doc)}]}
            data, status = self._request("POST", f"{SHEERID_BASE_URL}/rest/v2/verification/{self.vid}/step/docUpload", upload_body)
            
            if not data.get("documents"):
                stats.record(self.org["name"], False)
                return {"success": False, "message": "No upload URL"}
            
            upload_url = data["documents"][0].get("uploadUrl")
            if not self._upload_s3(upload_url, doc):
                stats.record(self.org["name"], False)
                return {"success": False, "message": "Upload failed"}
            
            logger.info("Document uploaded!")
            
            logger.info("Step 5: Completing upload...")
            data, status = self._request("POST", f"{SHEERID_BASE_URL}/rest/v2/verification/{self.vid}/step/completeDocUpload")
            logger.info(f"Upload completed: {data.get('currentStep', 'pending')}")
            
            # Get final status with reward code
            final_status, _ = self._request("GET", f"{MY_SHEERID_URL}/rest/v2/verification/{self.vid}")
            reward_code = None
            if isinstance(final_status, dict):
                reward_code = final_status.get("rewardCode") or final_status.get("rewardData", {}).get("rewardCode")
            
            # Auto email loop if needed (usually Bolt gives instant reward)
            if email_client and not reward_code:
                 logger.info("No instant reward code, checking email...")
                 for i in range(10):
                    link = email_client.wait_for_verification_link(self.vid)
                    if link:
                        logger.info(f"Found link: {link}")
                        # Bolt.new usually sends a link that redirects to reward, or contains it.
                        # For now, we return the link if found as a success message
                        return {
                            "success": True,
                            "pending": False,
                            "message": "Verifikasi berhasil! Cek link di email.",
                            "verification_id": self.vid,
                            "reward_link": link
                        }
                    await asyncio.sleep(5)

            stats.record(self.org["name"], True)
            
            return {
                "success": True,
                "pending": final_status.get("currentStep") != "success" if isinstance(final_status, dict) else True,
                "message": "Dokumen terkirim. Tunggu review." if not isinstance(final_status, dict) or final_status.get("currentStep") != "success" else "Verifikasi berhasil",
                "verification_id": self.vid,
                "redirect_url": final_status.get("redirectUrl") if isinstance(final_status, dict) else None,
                "reward_code": reward_code,
                "status": final_status,
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
    print("Bolt.new Teacher Verification Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter verification URL: ").strip()
    
    if not url:
        print("URL required")
        return
    
    verification_id = SheerIDVerifier.parse_verification_id(url)
    verifier = SheerIDVerifier(url, verification_id=verification_id)
    
    result = verifier._verify_sync()
    
    print()
    print("=" * 60)
    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Message: {result['message']}")
    if result.get("reward_code"):
        print(f"Reward Code: {result['reward_code']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
