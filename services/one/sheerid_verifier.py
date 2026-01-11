"""
Google One (Gemini) Student Verification Tool
SheerID Student Verification for Google One AI Premium

Enhanced with:
- Success rate tracking per organization
- Weighted university selection
- Rate limiting avoidance
- Transcript generation for higher success

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

from services.utils.universities import UNIVERSITIES
from services.utils.anti_detect import get_headers, get_fingerprint, random_delay, create_session
from services.utils.email_client import EmailClient

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


# ============ UTILITIES ============
FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan",
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia"
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Turner", "Phillips", "Evans", "Parker", "Edwards"
]


def generate_name() -> Tuple[str, str]:
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


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


# ============ DOCUMENT GENERATOR ============
def generate_transcript(first: str, last: str, school: str, dob: str) -> bytes:
    """Generate fake academic transcript (higher success rate)"""
    w, h = 850, 1100
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_header = ImageFont.truetype("arial.ttf", 32)
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arialbd.ttf", 16)
    except:
        font_header = font_title = font_text = font_bold = ImageFont.load_default()
    
    draw.text((w//2, 50), school.upper(), fill=(0, 0, 0), font=font_header, anchor="mm")
    draw.text((w//2, 90), "OFFICIAL ACADEMIC TRANSCRIPT", fill=(50, 50, 50), font=font_title, anchor="mm")
    draw.line([(50, 110), (w-50, 110)], fill=(0, 0, 0), width=2)
    
    y = 150
    draw.text((50, y), f"Student Name: {first} {last}", fill=(0, 0, 0), font=font_bold)
    draw.text((w-300, y), f"Student ID: {random.randint(10000000, 99999999)}", fill=(0, 0, 0), font=font_text)
    y += 30
    draw.text((50, y), f"Date of Birth: {dob}", fill=(0, 0, 0), font=font_text)
    draw.text((w-300, y), f"Date Issued: {time.strftime('%Y-%m-%d')}", fill=(0, 0, 0), font=font_text)
    y += 40
    
    draw.rectangle([(50, y), (w-50, y+40)], fill=(240, 240, 240))
    draw.text((w//2, y+20), "CURRENT STATUS: ENROLLED (SPRING 2025)", fill=(0, 100, 0), font=font_bold, anchor="mm")
    y += 70
    
    courses = [
        ("CS 101", "Intro to Computer Science", "4.0", "A"),
        ("MATH 201", "Calculus I", "3.0", "A-"),
        ("ENG 102", "Academic Writing", "3.0", "B+"),
        ("PHYS 150", "Physics for Engineers", "4.0", "A"),
        ("HIST 110", "World History", "3.0", "A")
    ]
    
    draw.text((50, y), "Course Code", font=font_bold, fill=(0,0,0))
    draw.text((200, y), "Course Title", font=font_bold, fill=(0,0,0))
    draw.text((600, y), "Credits", font=font_bold, fill=(0,0,0))
    draw.text((700, y), "Grade", font=font_bold, fill=(0,0,0))
    y += 20
    draw.line([(50, y), (w-50, y)], fill=(0, 0, 0), width=1)
    y += 20
    
    for code, title, cred, grade in courses:
        draw.text((50, y), code, font=font_text, fill=(0,0,0))
        draw.text((200, y), title, font=font_text, fill=(0,0,0))
        draw.text((600, y), cred, font=font_text, fill=(0,0,0))
        draw.text((700, y), grade, font=font_text, fill=(0,0,0))
        y += 30
    
    y += 20
    draw.line([(50, y), (w-50, y)], fill=(0, 0, 0), width=1)
    y += 30
    
    draw.text((50, y), "Cumulative GPA: 3.85", font=font_bold, fill=(0,0,0))
    draw.text((w-300, y), "Academic Standing: Good", font=font_bold, fill=(0,0,0))
    
    draw.text((w//2, h-50), "This document is electronically generated and valid without signature.", fill=(100, 100, 100), font=font_text, anchor="mm")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_student_id(first: str, last: str, school: str) -> bytes:
    """Generate fake student ID card"""
    w, h = 650, 400
    bg_color = (random.randint(240, 255), random.randint(240, 255), random.randint(240, 255))
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font_lg = ImageFont.truetype("arial.ttf", 26)
        font_md = ImageFont.truetype("arial.ttf", 18)
        font_sm = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 20)
    except:
        font_lg = font_md = font_sm = font_bold = ImageFont.load_default()
    
    header_color = (random.randint(0, 50), random.randint(0, 50), random.randint(50, 150))
    
    draw.rectangle([(0, 0), (w, 80)], fill=header_color)
    draw.text((w//2, 40), school.upper(), fill=(255, 255, 255), font=font_lg, anchor="mm")
    
    draw.rectangle([(30, 100), (160, 280)], outline=(100, 100, 100), width=2, fill=(220, 220, 220))
    draw.text((95, 190), "PHOTO", fill=(150, 150, 150), font=font_md, anchor="mm")
    
    x_info = 190
    y = 110
    draw.text((x_info, y), f"{first} {last}", fill=(0, 0, 0), font=font_bold)
    y += 40
    draw.text((x_info, y), "Student ID:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), str(random.randint(10000000, 99999999)), fill=(0, 0, 0), font=font_md)
    y += 30
    draw.text((x_info, y), "Role:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), "Student", fill=(0, 0, 0), font=font_md)
    y += 30
    draw.text((x_info, y), "Valid Thru:", fill=(100, 100, 100), font=font_sm)
    draw.text((x_info + 80, y), f"05/{int(time.strftime('%Y'))+1}", fill=(0, 0, 0), font=font_md)
    
    draw.rectangle([(0, 320), (w, 380)], fill=(255, 255, 255))
    for i in range(40):
        x = 50 + i * 14
        if random.random() > 0.3:
            draw.rectangle([(x, 330), (x+8, 370)], fill=(0, 0, 0))
            
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============ VERIFIER ============
class SheerIDVerifier:
    """Gemini Student Verification with enhanced features"""
    
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
        """Check if verification link is valid"""
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
    
    async def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
    ) -> Dict:
        """Run full verification (async wrapper for compatibility)"""
        return self._verify_sync(first_name, last_name, email, birth_date, school_id)
    
    def _verify_sync(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        school_id: str = None,
    ) -> Dict:
        """Run full verification"""
        if not self.vid:
            return {"success": False, "message": "Invalid verification URL"}
        
        try:
            check_data, check_status = self._request("GET", f"/verification/{self.vid}")
            current_step = check_data.get("currentStep", "") if check_status == 200 else ""
            
            if not first_name or not last_name:
                first_name, last_name = generate_name()
            
            if school_id:
                self.org = next((u for u in UNIVERSITIES if str(u["id"]) == school_id), None)
                if self.org:
                    self.org = {**self.org, "idExtended": str(self.org["id"])}
            
            if not self.org:
                self.org = select_university()
            
            if not email:
                email = generate_email(first_name, last_name, self.org["domain"])
            if not birth_date:
                birth_date = generate_birth_date()
            
            logger.info(f"Student: {first_name} {last_name}")
            logger.info(f"Email: {email}")
            logger.info(f"School: {self.org['name']}")
            
            doc_type = "transcript" if random.random() < 0.7 else "id_card"
            if doc_type == "transcript":
                logger.info("Step 1: Generating academic transcript...")
                doc = generate_transcript(first_name, last_name, self.org["name"], birth_date)
                filename = "transcript.png"
            else:
                logger.info("Step 1: Generating student ID...")
                doc = generate_student_id(first_name, last_name, self.org["name"])
                filename = "student_card.png"
            logger.info(f"Size: {len(doc)/1024:.1f} KB")
            
            if current_step == "collectStudentPersonalInfo":
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
            upload_body = {"files": [{"fileName": filename, "mimeType": "image/png", "fileSize": len(doc)}]}
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
                "message": "Dokumen terkirim. Tunggu 24-48 jam untuk review.",
                "verification_id": self.vid,
                "redirect_url": data.get("redirectUrl"),
                "status": data,
            }
            
        except Exception as e:
            if self.org:
                stats.record(self.org["name"], False)
            return {"success": False, "message": str(e), "verification_id": self.vid}


def main():
    import sys
    
    print("=" * 60)
    print("Google One (Gemini) Student Verification Tool")
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
