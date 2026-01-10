"""SheerID Military Verification Implementation
Based on ChatGPT Military Blueprint
Enhanced with source-code logic
"""
import re
import random
import logging
import httpx
import json
import hashlib
import time
import uuid
import base64
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_email, generate_birth_date, generate_discharge_date
from .img_generator import generate_military_png
from services.utils.anti_detect import get_headers, get_fingerprint, get_random_user_agent, random_delay, create_session
from services.utils.email_client import EmailClient
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class SheerIDVerifier:
    """SheerID Military Verifier"""

    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.device_fingerprint = self.generate_fingerprint()

    def generate_fingerprint(self):
        """Generate device fingerprint"""
        screens = ["1920x1080", "2560x1440", "1366x768"]
        screen = random.choice(screens)
        raw = f"{screen}|{time.time()}|{uuid.uuid4()}"
        return hashlib.md5(raw.encode()).hexdigest()

    def generate_newrelic_headers(self):
        """Generate NewRelic tracking headers"""
        trace_id = uuid.uuid4().hex + uuid.uuid4().hex[:8]
        trace_id = trace_id[:32]
        span_id = uuid.uuid4().hex[:16]
        timestamp = int(time.time() * 1000)

        payload = {
            "v": [0, 1],
            "d": {
                "ty": "Browser",
                "ac": "364029",
                "ap": "134291347",
                "id": span_id,
                "tr": trace_id,
                "ti": timestamp
            }
        }

        return {
            "newrelic": base64.b64encode(json.dumps(payload).encode()).decode(),
            "traceparent": f"00-{trace_id}-{span_id}-01",
            "tracestate": f"364029@nr=0-1-364029-134291347-{span_id}----{timestamp}"
        }

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    async def _sheerid_request(
        self, client: httpx.AsyncClient, method: str, url: str, body: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        # Use anti-detect headers with NewRelic headers
        nr = self.generate_newrelic_headers()
        headers = get_headers(for_sheerid=True)
        headers.update({
            "clientversion": "2.157.0",
            "clientname": "jslib",
            "newrelic": nr["newrelic"],
            "traceparent": nr["traceparent"],
            "tracestate": nr["tracestate"],
            "origin": "https://services.sheerid.com"
        })

        try:
            response = await client.request(method=method, url=url, json=body, headers=headers)
            try:
                data = response.json()
            except Exception:
                data = response.text
            return data, response.status_code
        except Exception as e:
            logger.error(f"SheerID Request Failed: {e}")
            raise

    async def _upload_to_s3(self, client: httpx.AsyncClient, upload_url: str, img_data: bytes) -> bool:
        try:
            headers = {"Content-Type": "image/png"}
            response = await client.put(upload_url, content=img_data, headers=headers, timeout=60.0)
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.error(f"S3 Upload Failed: {e}")
            return False

    async def verify(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        birth_date: str = None,
        branch: str = None,
        discharge_date: str = None,
        email_config: Dict = None,
        **kwargs
    ) -> Dict:
        email_client = None
        try:
            # 1. Prepare Data
            name_gen = NameGenerator.generate()
            first_name = first_name or name_gen["first_name"]
            last_name = last_name or name_gen["last_name"]

            # Email logic: config > argument > generated
            if email_config and email_config.get("email_address"):
                email = email_config.get("email_address")
                email_client = EmailClient(email_config)
            else:
                email = email or generate_email(first_name, last_name)

            birth_date = birth_date or generate_birth_date()
            discharge_date = discharge_date or generate_discharge_date()

            # Resolve Branch to Organization Object using Config
            input_branch = branch or config.DEFAULT_BRANCH
            # Normalize branch name using aliases
            normalized_branch = config.BRANCH_ALIASES.get(input_branch.upper(), config.DEFAULT_BRANCH)
            organization = config.ORGANIZATIONS.get(normalized_branch)

            if not organization:
                # Fallback to Army if not found
                organization = config.ORGANIZATIONS['Army']
                normalized_branch = 'Army'

            logger.info(f"Starting Military Verification for: {first_name} {last_name} ({normalized_branch})")

            # Create session with enhanced anti-detection
            session_info = create_session()
            client = session_info[0]

            # Loop to handle steps
            for _ in range(20): # Increased loop for email polling safety
                # Get Current Status
                v_data, v_status = await self._sheerid_request(
                    client, "GET", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}"
                )

                if v_status != 200:
                    raise Exception("Verification ID not found or expired.")

                current_step = v_data.get("currentStep")
                logger.info(f"Current Step: {current_step}")

                if current_step == "success":
                    return {
                        "success": True,
                        "message": "Verification Successful!",
                        "verification_id": self.verification_id,
                        "redirect_url": v_data.get("redirectUrl"),
                        "reward_code": v_data.get("rewardCode") or v_data.get("rewardData", {}).get("rewardCode")
                    }

                if current_step == "pending" or current_step == "docReview":
                     return {
                        "success": True,
                        "message": "Documents submitted. Pending review.",
                        "verification_id": self.verification_id
                    }

                # --- IMPLEMENTATION OF BLUEPRINT STEPS ---

                # STEP 1: collectMilitaryStatus
                if current_step == "collectMilitaryStatus":
                    logger.info("Step 1: Setting Military Status to VETERAN")
                    payload = {
                        "status": "VETERAN"
                    }
                    await self._sheerid_request(
                        client, "POST",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectMilitaryStatus",
                        payload
                    )

                # STEP 2: collectInactiveMilitaryPersonalInfo
                elif current_step == "collectInactiveMilitaryPersonalInfo":
                    logger.info("Step 2: Submitting Personal Info (Inactive/Veteran)")

                    # Flags specific to ChatGPT/OpenAI program
                    flags_json = json.dumps({
                        "doc-upload-considerations": "default",
                        "doc-upload-may24": "default",
                        "doc-upload-redesign-use-legacy-message-keys": False,
                        "docUpload-assertion-checklist": "default",
                        "include-cvec-field-france-student": "not-labeled-optional",
                        "org-search-overlay": "default",
                        "org-selected-display": "default"
                    })

                    # Exact opt-in text from blueprint (Crucial for OpenAI)
                    opt_in_text = (
                        'By submitting the personal information above, I acknowledge that my personal information is being collected under the '
                        '<a target="_blank" rel="noopener noreferrer" class="sid-privacy-policy sid-link" href="https://openai.com/policies/privacy-policy/">privacy policy</a> '
                        'of the business from which I am seeking a discount, and I understand that my personal information will be shared with SheerID as a processor/third-party service provider '
                        'in order for SheerID to confirm my eligibility for a special offer. Contact OpenAI Support for further assistance at support@openai.com'
                    )

                    referer = f"https://services.sheerid.com/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}"

                    payload = {
                        "firstName": first_name,
                        "lastName": last_name,
                        "birthDate": birth_date,
                        "email": email,
                        "phoneNumber": "", # Optional per blueprint
                        "organization": organization, # Using static ID from config (e.g. {id: 4070, name: "Army", ...})
                        "dischargeDate": discharge_date,
                        "deviceFingerprintHash": self.device_fingerprint,
                        "locale": "en-US",
                        "country": "US",
                        "metadata": {
                            "marketConsentValue": False,
                            "refererUrl": referer,
                            "verificationId": self.verification_id,
                            "submissionOptIn": opt_in_text
                        }
                    }

                    res_data, res_status = await self._sheerid_request(
                        client, "POST",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectInactiveMilitaryPersonalInfo",
                        payload
                    )

                    if res_status != 200:
                        err_msg = str(res_data)
                        if "errorIds" in res_data:
                            err_msg = ", ".join(res_data["errorIds"])
                        raise Exception(f"Step 2 Failed: {err_msg}")

                # Fallback for Active Duty (Just in case logic shifts)
                elif current_step == "collectActiveMilitaryPersonalInfo":
                     logger.warning("Unexpected step: collectActiveMilitaryPersonalInfo (We set status to VETERAN)")
                     # Try submitting anyway with simplified metadata
                     payload = {
                        "firstName": first_name,
                        "lastName": last_name,
                        "birthDate": birth_date,
                        "email": email,
                        "organization": organization,
                        "status": "ACTIVE_DUTY",
                        "deviceFingerprintHash": self.device_fingerprint,
                     }
                     await self._sheerid_request(
                        client, "POST",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectActiveMilitaryPersonalInfo",
                        payload
                    )

                # SSO Step (Skip)
                elif current_step == "sso":
                    logger.info("Skipping SSO...")
                    await self._sheerid_request(
                        client, "DELETE", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso"
                    )

                # Document Upload Step
                elif current_step == "docUpload":
                    logger.info("Generating and Uploading DD-214...")

                    # Generate DD-214 PNG
                    img_data = await generate_military_png(
                        first_name, last_name, birth_date, discharge_date, normalized_branch.upper().replace(' ', '_')
                    )

                    # Get Upload URL
                    up_res, _ = await self._sheerid_request(
                        client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                        {
                            "files": [
                                {"fileName": "dd214.png", "mimeType": "image/png", "fileSize": len(img_data)}
                            ]
                        }
                    )

                    if not up_res.get("documents"):
                        raise Exception("Failed to get S3 upload URL.")

                    upload_url = up_res["documents"][0]["uploadUrl"]

                    # Upload to S3
                    if await self._upload_to_s3(client, upload_url, img_data):
                        logger.info("Upload successful, completing submission...")
                        await self._sheerid_request(
                            client, "POST", f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload"
                        )
                    else:
                        raise Exception("Failed to upload document to S3.")

                # EMAIL LOOP (NEW)
                elif current_step == "emailLoop":
                    logger.info("Step: Email Loop triggered. Checking email...")

                    if not email_client:
                        return {
                            "success": False,
                            "message": "Email verification required but no email config provided.",
                            "verification_id": self.verification_id
                        }

                    # Poll for email
                    link = None
                    for i in range(10): # 10 attempts * 5s = 50s wait
                        logger.info(f"Polling email attempt {i+1}/10...")
                        link = email_client.wait_for_verification_link(self.verification_id)
                        if link:
                            break
                        await asyncio.sleep(5)

                    if not link:
                         return {
                            "success": False,
                            "message": "Verification email not found after polling.",
                            "verification_id": self.verification_id
                        }

                    # Extract token
                    match = re.search(r"emailToken=(\d+)", link)
                    if not match:
                         return {
                            "success": False,
                            "message": "Could not extract emailToken from link.",
                            "verification_id": self.verification_id
                        }

                    email_token = match.group(1)
                    logger.info(f"Found email token: {email_token}")

                    # Submit token
                    await self._sheerid_request(
                        client, "POST",
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/emailLoop",
                        {
                            "emailToken": email_token,
                            "deviceFingerprintHash": self.device_fingerprint
                        }
                    )

                elif current_step == "error":
                    raise Exception(f"SheerID returned error state: {v_data.get('errorIds')}")

                else:
                    # Unknown step, wait a bit
                    await asyncio.sleep(2)

            return {
                "success": True,
                "message": "Process completed successfully.",
                "verification_id": self.verification_id
            }

        except Exception as e:
            logger.error(f"Verification Failed: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}
        finally:
            if email_client:
                email_client.close()