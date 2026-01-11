"""
K12 Teacher Verification Tool
SheerID K12 Teacher Verification (High School)

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
PROGRAM_ID = "68d47554aa292d20b9bec8f7"
SHEERID_BASE_URL = "https://services.sheerid.com"
MIN_DELAY = 300
MAX_DELAY = 800

# ============ K12 SCHOOLS ============
K12_SCHOOLS = [
    {"id": 155694, "name": "Stuyvesant High School", "city": "New York, NY", "weight": 100},
    {"id": 156251, "name": "Bronx High School Of Science", "city": "Bronx, NY", "weight": 98},
    {"id": 157582, "name": "Brooklyn Technical High School", "city": "Brooklyn, NY", "weight": 95},
    {"id": 3704245, "name": "Thomas Jefferson High School For Science And Technology", "city": "Alexandria, VA", "weight": 100},
    {"id": 3521141, "name": "Walter Payton College Preparatory High School", "city": "Chicago, IL", "weight": 95},
    {"id": 3521074, "name": "Whitney M Young Magnet High School", "city": "Chicago, IL", "weight": 92},
    {"id": 3539252, "name": "Gretchen Whitney High School", "city": "Cerritos, CA", "weight": 95},
    {"id": 262338, "name": "Lowell High School (San Francisco)", "city": "San Francisco, CA", "weight": 90},
    {"id": 3536914, "name": "BASIS Scottsdale", "city": "Scottsdale, AZ", "weight": 90},
    {"id": 155846, "name": "KIPP Academy Charter School (Bronx)", "city": "Bronx, NY", "weight": 85},
    {"id": 202063, "name": "Signature School Inc", "city": "Evansville, IN", "weight": 95},
    {"id": 174195, "name": "North Carolina School of Science and Mathematics", "city": "Durham, NC", "weight": 90},
    {"id": 3520767, "name": "Il Mathematics And Science Academy", "city": "Aurora, IL", "weight": 92},
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


def select_school() -> Dict:
    """Weighted random selection of K12 school"""
    weights = []
    for s in K12_SCHOOLS:
        weight = s["weight"] * (stats.get_rate(s["name"]) / 50)
        weights.append(max(1, weight))
    
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for school, weight in zip(K12_SCHOOLS, weights):
        cumulative += weight
        if r <= cumulative:
            return {"id": school["id"], "idExtended": str(school["id"]), "name": school["name"]}
    return {"id": K12_SCHOOLS[0]["id"], "idExtended": str(K12_SCHOOLS[0]["id"]), "name": K12_SCHOOLS[0]["name"]}


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


def generate_email(first: str, last: str) -> str:
    suffix = random.randint(100, 999)
    domains = ["gmail.com", "yahoo.com", "outlook.com"]
    return f"{first.lower()}.{last.lower()}{suffix}@{random.choice(domains)}"


def generate_birth_date() -> str:
    """Generate birth date (25-55 years old for teacher)"""
    year = random.randint(1970, 2000)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


# ============ IMAGE GENERATOR ============
def generate_teacher_badge(first: str, last: str, school: str) -> bytes:
    """Generate fake K12 teacher badge PNG"""
    width, height = 500, 350
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 22)
        text_font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = text_font = small_font = ImageFont.load_default()
    
    draw.rectangle([(0, 0), (width, 50)], fill=(34, 139, 34))
    draw.text((width//2, 25), "STAFF IDENTIFICATION", fill=(255, 255, 255), 
              font=title_font, anchor="mm")
    
    draw.text((width//2, 75), school, fill=(34, 139, 34), font=text_font, anchor="mm")
    
    draw.rectangle([(25, 100), (125, 220)], outline=(200, 200, 200), width=2)
    draw.text((75, 160), "PHOTO", fill=(200, 200, 200), font=text_font, anchor="mm")
    
    teacher_id = f"T{random.randint(10000, 99999)}"
    info_y = 110
    info_lines = [
        f"Name: {first} {last}",
        f"ID: {teacher_id}",
        f"Position: Teacher",
        f"Department: Education",
        f"Status: Active"
    ]
    
    for line in info_lines:
        draw.text((145, info_y), line, fill=(51, 51, 51), font=text_font)
        info_y += 22
    
    current_year = int(time.strftime("%Y"))
    draw.text((145, info_y + 10), f"Valid: {current_year}-{current_year+1} School Year", 
              fill=(100, 100, 100), font=small_font)
    
    draw.rectangle([(0, height-35), (width, height)], fill=(34, 139, 34))
    draw.text((width//2, height-18), "Property of School District", 
              fill=(255, 255, 255), font=small_font, anchor="mm")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# ============ VERIFIER ============
class SheerIDVerifier:
    """K12 Teacher Verification"""
    
    def __init__(self, url: str, proxy: str = None):
        self.url = url
        self.vid = self._parse_id(url)
        self.fingerprint = get_fingerprint()
        
        self.client, self.lib_name = create_session(proxy)
        self.org = None
    
    def __del__(self):
        if hasattr(self, "client"):
            self.client.close()
    
    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        # Handle raw ID (24 hex chars)
        if re.match(r"^[a-f0-9]{24}$", url, re.IGNORECASE):
            return url
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _request(self, method: str, endpoint: str, body: Dict = None) -> Tuple[Dict, int]:
        random_delay()
        try:
            # Get anti-detect headers
            headers = get_headers(for_sheerid=True)
            
            resp = self.client.request(method, f"{SHEERID_BASE_URL}/rest/v2{endpoint}", 
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
    
    def _upload_s3(self, url: str, data: bytes, mime_type: str = "image/png") -> bool:
        try:
            resp = self.client.put(url, content=data, headers={"Content-Type": mime_type}, timeout=60)
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
        if not self.vid:
            return {"success": False, "message": "Invalid verification URL"}
        
        email_client = None
        try:
            first, last = generate_name()
            
            if email_config and email_config.get("email_address"):
                email = email_config.get("email_address")
                email_client = EmailClient(email_config)
            else:
                email = generate_email(first, last)
            
            birth_date = generate_birth_date()
            self.org = select_school()
            
            logger.info(f"Teacher: {first} {last}")
            logger.info(f"Email: {email}")
            logger.info(f"School: {self.org['name']}")
            logger.info(f"ID: {self.vid[:20]}...")
            
            logger.info("Step 1: Generating teacher badge...")
            doc = generate_teacher_badge(first, last, self.org["name"])
            logger.info(f"Size: {len(doc)/1024:.1f} KB")
            
            logger.info("Step 2: Submitting teacher info...")
            body = {
                "firstName": first, "lastName": last, "birthDate": birth_date,
                "email": email, "phoneNumber": "",
                "organization": {"id": self.org["id"], "idExtended": self.org["idExtended"], 
                                "name": self.org["name"]},
                "deviceFingerprintHash": self.fingerprint,
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": False,
                    "verificationId": self.vid,
                    "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                }
            }
            
            data, status = self._request("POST", f"/verification/{self.vid}/step/collectTeacherPersonalInfo", body)
            
            if status != 200:
                stats.record(self.org["name"], False)
                return {"success": False, "message": f"Submit failed: {status}"}
            
            if data.get("currentStep") == "error":
                stats.record(self.org["name"], False)
                return {"success": False, "message": f"Error: {data.get('errorIds', [])}"}
            
            current_step = data.get("currentStep", "")
            logger.info(f"Current step: {current_step}")
            
            if current_step == "success":
                logger.info("AUTO-PASS! No upload needed!")
                stats.record(self.org["name"], True)
                return {
                    "success": True,
                    "pending": False,
                    "message": "Verification auto-approved!",
                    "verification_id": self.vid,
                    "redirect_url": data.get("redirectUrl"),
                }
            
            if current_step in ["sso", "collectTeacherPersonalInfo"]:
                logger.info("Step 3: Skipping SSO...")
                data, _ = self._request("DELETE", f"/verification/{self.vid}/step/sso")
                current_step = data.get("currentStep", "") if isinstance(data, dict) else ""
                
                if current_step == "success":
                    stats.record(self.org["name"], True)
                    return {
                        "success": True,
                        "pending": False,
                        "message": "Verification auto-approved after SSO skip!",
                        "verification_id": self.vid,
                    }
            
            if current_step == "emailLoop":
                logger.warning(f"emailLoop triggered for: {self.org['name']}")
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
                else:
                    stats.record(self.org["name"], False)
                    return {
                        "success": False,
                        "message": "emailLoop - need new verification link",
                        "verification_id": self.vid,
                    }
            
            logger.info("Step 4: Uploading teacher badge...")
            upload_body = {"files": [{"fileName": "teacher_badge.png", "mimeType": "image/png", "fileSize": len(doc)}]}
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
            
            stats.record(self.org["name"], True)
            
            return {
                "success": True,
                "pending": True,
                "message": "Dokumen terkirim. Tunggu review.",
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
    print("K12 Teacher Verification Tool")
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
