"""Perplexity Verifier (Groningen Strategy)
Supports Proxy via kwargs
"""
import re
import random
import logging
import httpx
import json
from typing import Dict, Optional, Tuple

from . import config
from services.Boltnew.name_generator import NameGenerator, generate_birth_date # Reuse generators
from .img_generator import generate_groningen_invoice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_email(first, last, domain):
    return f"{first[0].lower()}{last.lower()}{random.randint(10,99)}@{domain}"

class SheerIDVerifier:
    def __init__(self, verification_url: str):
        self.url = verification_url
        self.verification_id = self._parse_id(verification_url)
        self.program_id = self._parse_program_id(verification_url) or config.PROGRAM_ID
        self.fingerprint = self._generate_fingerprint()
        
    @staticmethod
    def _parse_id(url: str) -> Optional[str]:
        # Try finding verificationId param
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match: return match.group(1)
        # Try finding ID in path
        match = re.search(r"/verification/([a-f0-9]+)", url, re.IGNORECASE)
        if match: return match.group(1)
        return None

    @staticmethod
    def _parse_program_id(url: str) -> Optional[str]:
        match = re.search(r"/verify/([a-f0-9]+)/?", url, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def _generate_fingerprint() -> str:
        chars = '0123456789abcdef'
        return ''.join(random.choice(chars) for _ in range(32))

    async def verify(self, proxy: str = None, **kwargs) -> Dict:
        if not self.verification_id:
            return {"success": False, "message": "Invalid URL"}

        # Configure Client with Proxy if provided
        # Supports HTTP/HTTPS and SOCKS5 (SSH Tunnel)
        mounts = None
        transport = None
        
        if proxy:
            if proxy.startswith("socks"):
                # Handle SOCKS5 Proxy (SSH Tunnel)
                from httpx_socks import AsyncProxyTransport
                transport = AsyncProxyTransport.from_url(proxy)
            else:
                # Handle Standard HTTP Proxy
                mounts = {
                    "http://": httpx.HTTPTransport(proxy=proxy),
                    "https://": httpx.HTTPTransport(proxy=proxy)
                }
        
        # Initialize client with appropriate transport/mounts
        # Note: If using SOCKS, we use 'transport', otherwise 'mounts'
        async with httpx.AsyncClient(timeout=30.0, mounts=mounts, transport=transport) as client:
            try:
                # 1. Generate Data (Groningen specific)
                name_gen = NameGenerator.generate()
                first = name_gen['first_name']
                last = name_gen['last_name']
                school = config.get_groningen_school()
                email = generate_email(first, last, school['domain'])
                dob = "2002-05-15" # Student age approx
                
                logger.info(f"Verifying {first} {last} at {school['name']}")
                
                # 2. Check Step
                resp = await client.get(f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}")
                current_step = resp.json().get("currentStep")
                
                # 3. Submit Info
                if current_step == "collectStudentPersonalInfo":
                    logger.info("Submitting info...")
                    payload = {
                        "firstName": first, "lastName": last, "birthDate": dob,
                        "email": email, "phoneNumber": "",
                        "organization": {"id": school['id'], "name": school['name'], "idExtended": school['idExtended']},
                        "deviceFingerprintHash": self.fingerprint,
                        "metadata": {
                            "verificationId": self.verification_id,
                            "marketConsentValue": False,
                            "submissionOptIn": "By submitting..." 
                        }
                    }
                    resp = await client.post(
                        f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/collectStudentPersonalInfo",
                        json=payload
                    )
                    if resp.status_code != 200:
                        return {"success": False, "message": f"Submit failed: {resp.text}"}
                    current_step = resp.json().get("currentStep")

                # 4. Skip SSO
                if current_step in ["sso", "collectStudentPersonalInfo"]:
                    logger.info("Skipping SSO...")
                    await client.delete(f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/sso")
                
                # 5. Upload Document
                logger.info("Generating Invoice...")
                doc_bytes = generate_groningen_invoice(first, last, "15 May 2002")
                
                # Get upload URL
                upload_req = await client.post(
                    f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/docUpload",
                    json={"files": [{"fileName": "invoice.png", "mimeType": "image/png", "fileSize": len(doc_bytes)}]}
                )
                upload_data = upload_req.json()
                if not upload_data.get("documents"):
                    return {"success": False, "message": "No upload URL"}
                
                # Upload S3
                upload_url = upload_data["documents"][0]["uploadUrl"]
                await client.put(upload_url, content=doc_bytes, headers={"Content-Type": "image/png"})
                
                # Complete
                final_res = await client.post(f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/step/completeDocUpload")
                
                return {
                    "success": True,
                    "message": "Verification Submitted (Groningen Strategy)",
                    "redirect_url": final_res.json().get("redirectUrl"),
                    "verification_id": self.verification_id
                }

            except Exception as e:
                logger.error(f"Perplexity Error: {e}")
                return {"success": False, "message": str(e)}
