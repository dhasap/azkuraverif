"""
YouTube Student Verification Tool
SheerID Student Verification for YouTube Premium

Enhanced with:
- Success rate tracking per organization
- Weighted university selection
- Retry with exponential backoff
- Rate limiting avoidance

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

from .universities import UNIVERSITIES
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
def generate_student_id(first: str, last: str, school: str) -> bytes:
    """Generate fake student ID card"""
    w, h = 650, 400
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_lg = ImageFont.truetype("arial.ttf", 24)
        font_md = ImageFont.truetype("arial.ttf", 18)
        font_sm = ImageFont.truetype("arial.ttf", 14)
    except:
        font_lg = font_md = font_sm = ImageFont.load_default()
    
    draw.rectangle([(0, 0), (w, 60)], fill=(0, 51, 102))
    draw.text((w//2, 30), "STUDENT IDENTIFICATION CARD", fill=(255, 255, 255), font=font_lg, anchor="mm")
    draw.text((w//2, 90), school[:50], fill=(0, 51, 102), font=font_md, anchor="mm")
    draw.rectangle([(30, 120), (150, 280)], outline=(180, 180, 180), width=2)
    draw.text((90, 200), "PHOTO", fill=(180, 180, 180), font=font_md, anchor="mm")
    
    student_id = f"STU{random.randint(100000, 999999)}"
    y = 130
    for line in [f"Name: {first} {last}", f"ID: {student_id}", "Status: Full-time Student",
                 "Major: Computer Science", f"Valid: {time.strftime('%Y')}-{int(time.strftime('%Y'))+1}"]:
        draw.text((175, y), line, fill=(51, 51, 51), font=font_md)
        y += 28
    
    draw.rectangle([(0, h-40), (w, h)], fill=(0, 51, 102))
    draw.text((w//2, h-20), "Property of University", fill=(255, 255, 255), font=font_sm, anchor="mm")
    
    for i in range(20):
        x = 480 + i * 7
        draw.rectangle([(x, 280), (x+3, 280+random.randint(30, 50))], fill=(0, 0, 0))
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============ VERIFIER ============
class SheerIDVerifier:
    """YouTube Student Verification with enhanced features"""
    
    def __init__(self, url: str, verification_id: str = None, proxy: str = None):
        self.url = url
        # Jika verification_id diberikan secara eksplisit, gunakan itu
        # Jika tidak, coba ekstrak dari URL
        self.vid = verification_id or self._parse_id(url)
        self.fingerprint = get_fingerprint()
        self.client, self.lib_name = create_session(proxy)
        self.org = None
        self.external_user_id = self._parse_query_param(url, "euid")
    
    def __del__(self):
        if hasattr(self, "client"):
            try:
                self.client.close()
            except:
                pass

    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        # Coba ekstrak dari verificationId terlebih dahulu
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        # Jika tidak ditemukan, coba ekstrak dari oid (untuk URL kompleks YouTube)
        match = re.search(r'oid=([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        """Ekstrak verification ID dari URL"""
        # Coba ekstrak dari verificationId terlebih dahulu
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        # Jika tidak ditemukan, coba ekstrak dari oid (untuk URL kompleks YouTube)
        match = re.search(r'oid=([A-Za-z0-9_-]+)', url)
        return match.group(1) if match else None

    @staticmethod
    def _parse_query_param(url: str, param: str) -> Optional[str]:
        match = re.search(f"{param}=([^&]+)", url, re.IGNORECASE)
        return match.group(1) if match else None

    async def _create_verification_session(self) -> Optional[str]:
        """Membuat sesi verifikasi baru dari URL penawaran"""
        try:
            # Membuat sesi verifikasi baru dari URL penawaran
            headers = get_headers(for_sheerid=True)
            body = {
                "programId": PROGRAM_ID,
                "installPageUrl": self.url,
            }

            # Karena ini fungsi async, kita perlu membuat request async
            # Tapi karena kita menggunakan httpx client sync, kita panggil sync
            response = self.client.post(
                "https://services.sheerid.com/rest/v2/verification/",
                json=body,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("verificationId")
            else:
                logger.error(f"Failed to create verification session: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Exception while creating verification session: {e}")
            return None

    def _verify_sync(self, *args, **kwargs):
        """Sync wrapper for async verification"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self._verify_async(*args, **kwargs))
    
    def _request(self, method: str, endpoint: str, body: Dict = None) -> Tuple[Dict, int]:
        random_delay()
        try:
            # Get anti-detect headers
            headers = get_headers(for_sheerid=True)
            
            # Use request method of the session
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
        # Jika tidak ada vid atau jika vid yang diekstrak tidak valid (menghasilkan 404),
        # buat sesi verifikasi baru dari URL penawaran
        if self.vid:
            # Cek apakah ID verifikasi yang diekstrak valid
            check_data, check_status = self._request("GET", f"/verification/{self.vid}")
            if check_status == 404:
                # ID tidak valid, buat sesi baru dari URL
                logger.info("Verification ID not found, creating new session from URL")
                verification_id = await self._create_verification_session()
                if not verification_id:
                    return {"success": False, "message": "Could not create verification session from URL"}
                self.vid = verification_id
        else:
            # Tidak ada ID, buat sesi baru dari URL
            verification_id = await self._create_verification_session()
            if not verification_id:
                return {"success": False, "message": "Could not create verification session from URL"}
            self.vid = verification_id

        email_client = None
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
            
            if email_config and email_config.get("email_address"):
                email = email_config.get("email_address")
                email_client = EmailClient(email_config)
            else:
                email = email or generate_email(first_name, last_name, self.org["domain"])
            
            if not birth_date:
                birth_date = generate_birth_date()
            
            logger.info(f"Student: {first_name} {last_name}")
            logger.info(f"Email: {email}")
            logger.info(f"School: {self.org['name']}")
            logger.info(f"DOB: {birth_date}")
            logger.info(f"ID: {self.vid[:20]}...")
            logger.info(f"Starting step: {current_step}")
            
            logger.info("Step 1: Generating student ID...")
            doc = generate_student_id(first_name, last_name, self.org["name"])
            logger.info(f"Size: {len(doc)/1024:.1f} KB")
            
            if current_step == "collectStudentPersonalInfo":
                logger.info("Step 2: Submitting student info...")

                # Gunakan URL asli sebagai referer daripada URL SheerID standar
                referer_url = self.url if self.url else f"https://services.sheerid.com/verify/{PROGRAM_ID}/?verificationId={self.vid}"

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
                        "refererUrl": referer_url,
                        "flags": '{"collect-info-step-email-first":"default","doc-upload-considerations":"default","doc-upload-may24":"default","doc-upload-redesign-use-legacy-message-keys":false,"docUpload-assertion-checklist":"default","font-size":"default","include-cvec-field-france-student":"not-labeled-optional"}',
                        "submissionOptIn": "By submitting the personal information above, I acknowledge that my personal information is being collected under the privacy policy of the business from which I am seeking a discount"
                    }
                }
                
                # Add externalUserId if present
                if self.external_user_id:
                    body["externalUserId"] = self.external_user_id
                    body["metadata"]["externalUserId"] = self.external_user_id

                data, status = self._request("POST", f"/verification/{self.vid}/step/collectStudentPersonalInfo", body)

                if status != 200:
                    # Jika gagal dengan 400, coba tanpa beberapa field yang mungkin tidak diperlukan
                    if status == 400:
                        logger.info("Retrying with simplified metadata...")

                        # Coba kirim tanpa beberapa field yang mungkin menyebabkan masalah
                        body_retry = {
                            "firstName": first_name, "lastName": last_name, "birthDate": birth_date,
                            "email": email, "phoneNumber": "",
                            "organization": {"id": self.org["id"], "idExtended": self.org["idExtended"],
                                            "name": self.org["name"]},
                            "deviceFingerprintHash": self.fingerprint,
                            "locale": "en-US"
                        }
                        
                        if self.external_user_id:
                            body_retry["externalUserId"] = self.external_user_id

                        data, status = self._request("POST", f"/verification/{self.vid}/step/collectStudentPersonalInfo", body_retry)

                        if status != 200:
                            stats.record(self.org["name"], False)
                            return {"success": False, "message": f"Submit failed: {status}"}
                    else:
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
            upload_body = {"files": [{"fileName": "student_card.png", "mimeType": "image/png", "fileSize": len(doc)}]}
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
                "message": "Dokumen terkirim. Cek email YouTube dalam 20 menit.",
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
    print("YouTube Student Verification Tool")
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
    if result.get("redirect_url"):
        print(f"Redirect URL: {result['redirect_url']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
