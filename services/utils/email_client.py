import imaplib
import email
import re
from email.header import decode_header

class EmailClient:
    """Simple IMAP email client"""
    
    def __init__(self, config):
        self.server = config.get("imap_server", "imap.gmail.com")
        self.port = config.get("imap_port", 993)
        self.email = config.get("email_address", "")
        self.password = config.get("email_password", "")
        self.use_ssl = config.get("use_ssl", True)
        self.conn = None
    
    def connect(self):
        try:
            if self.use_ssl:
                self.conn = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.conn = imaplib.IMAP4(self.server, self.port)
            self.conn.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"   [ERROR] Email connection failed: {e}")
            self.conn = None  # Reset connection on failure
            if "LOGIN failed" in str(e):
                print("   [TIP] Check your email/password.")
                print("         - If using Gmail/Outlook/Yahoo with 2FA, use an App Password.")
                print("         - Check if IMAP is enabled in your email settings.")
            return False
    
    def get_latest_emails(self, count=5):
        if not self.conn:
            if not self.connect():
                return []
        
        try:
            self.conn.select("INBOX")
            _, messages = self.conn.search(None, "ALL")
            email_ids = messages[0].split()
            
            if not email_ids:
                return []
            
            latest_ids = email_ids[-count:] if len(email_ids) >= count else email_ids
            latest_ids = latest_ids[::-1]
            
            emails = []
            for eid in latest_ids:
                _, msg_data = self.conn.fetch(eid, "(RFC822)")
                for part in msg_data:
                    if isinstance(part, tuple):
                        msg = email.message_from_bytes(part[1])
                        content = self._get_content(msg)
                        emails.append({"content": content})
            return emails
        except Exception as e:
            print(f"   [WARN] Email fetch error: {e}")
            self.conn = None
            return []
    
    def _get_content(self, msg):
        content = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        content = payload.decode(charset, errors="ignore")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                content = payload.decode(charset, errors="ignore")
        return content
    
    def close(self):
        if self.conn:
            try:
                self.conn.logout()
            except:
                pass
    
    def wait_for_verification_link(self, verification_id):
        """Helper to scan emails for SheerID link with verification_id"""
        emails = self.get_latest_emails(10)
        for e in emails:
            content = e.get("content", "")
            if "SheerID" in content or "verification" in content or "Verify" in content:
                # Look for link containing verificationId and emailToken
                # Regex matches: https://services.sheerid.com/verify/...emailToken=...
                # It should also match the verification_id
                match = re.search(r"https://services\.sheerid\.com/verify/[^\s<>\"']+emailToken=\d+", content)
                if match:
                    link = match.group(0).replace("&amp;", "&")
                    if verification_id in link:
                        return link
        return None
