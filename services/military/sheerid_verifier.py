"""SheerID Military Verification Implementation
Based on ChatGPT Military Blueprint
"""
import re
import random
import logging
import httpx
import json
from typing import Dict, Optional, Tuple

from . import config
from .name_generator import NameGenerator, generate_email, generate_birth_date, generate_discharge_date
from .img_generator import generate_military_png

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
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
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
        **kwargs
    ) -> Dict:
        try:
            # 1. Prepare Data
            name_gen = NameGenerator.generate()
            first_name = first_name or name_gen["first_name"]
            last_name = last_name or name_gen["last_name"]
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

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Loop to handle steps
                for _ in range(15):
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

                        payload = {
                            "firstName": first_name,
                            "lastName": last_name,
                            "birthDate": birth_date,
                            "email": email,
                            "phoneNumber": "", # Optional per blueprint
                            "organization": organization, # Using static ID from config (e.g. {id: 4070, name: "Army", ...})
                            "dischargeDate": discharge_date,
                            "locale": "en-US",
                            "country": "US",
                            "deviceFingerprintHash": self.device_fingerprint,
                            "metadata": {
                                "marketConsentValue": False,
                                "refererUrl": "",
                                "verificationId": self.verification_id,
                                "flags": flags_json,
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
                    
                    elif current_step == "error":
                        raise Exception(f"SheerID returned error state: {v_data.get('errorIds')}")
                    
                    else:
                        # Unknown step, wait a bit
                        import asyncio
                        await asyncio.sleep(2)

            return {
                "success": True,
                "message": "Process completed successfully.",
                "verification_id": self.verification_id
            }

        except Exception as e:
            logger.error(f"Verification Failed: {e}")
            return {"success": False, "message": str(e), "verification_id": self.verification_id}