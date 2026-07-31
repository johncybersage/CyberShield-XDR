import email
import re
from email.message import Message
from typing import Any, Dict, Tuple

from backend.config.logging_config import get_logger
from backend.models.phishing import PhishingVerdict

logger = get_logger(__name__)

class PhishingAnalysisService:
    def __init__(self):
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )

    def _extract_body(self, msg: Message) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body += part.get_payload(decode=True).decode(errors='ignore')
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            except Exception:
                pass
        return body

    def _parse_authentication_headers(self, msg: Message) -> Tuple[bool, bool, bool]:
        spf_pass = None
        dkim_pass = None
        dmarc_pass = None
        
        auth_results = msg.get_all("Authentication-Results", [])
        received_spf = msg.get_all("Received-SPF", [])
        
        auth_header_str = " ".join(auth_results + received_spf).lower()
        
        if "spf=pass" in auth_header_str:
            spf_pass = True
        elif "spf=fail" in auth_header_str or "spf=softfail" in auth_header_str:
            spf_pass = False
            
        if "dkim=pass" in auth_header_str:
            dkim_pass = True
        elif "dkim=fail" in auth_header_str:
            dkim_pass = False
            
        if "dmarc=pass" in auth_header_str:
            dmarc_pass = True
        elif "dmarc=fail" in auth_header_str:
            dmarc_pass = False
            
        return spf_pass, dkim_pass, dmarc_pass

    def _extract_urls(self, text: str) -> list:
        urls = self.url_pattern.findall(text)
        # Deduplicate
        return list(set(urls))

    def _check_anomalies(self, msg: Message, sender: str) -> Dict[str, Any]:
        anomalies = {}
        
        reply_to = str(msg.get("Reply-To", ""))
        if reply_to and sender:
            # Basic check if reply-to domain differs from sender domain
            try:
                sender_domain = sender.split("@")[-1].strip(">").lower()
                reply_to_domain = reply_to.split("@")[-1].strip(">").lower()
                if sender_domain != reply_to_domain:
                    anomalies["reply_to_mismatch"] = f"Sender domain {sender_domain} does not match Reply-To domain {reply_to_domain}"
            except Exception:
                pass
                
        # Check for suspicious subjects
        subject = str(msg.get("Subject", "")).lower()
        suspicious_keywords = ["urgent", "password", "invoice", "payment", "account suspended", "verify"]
        matched_keywords = [k for k in suspicious_keywords if k in subject]
        if matched_keywords:
            anomalies["suspicious_subject"] = f"Subject contains high-risk keywords: {', '.join(matched_keywords)}"
            
        return anomalies

    def analyze_email(self, raw_eml: bytes) -> Dict[str, Any]:
        try:
            msg = email.message_from_bytes(raw_eml)
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            raise ValueError("Invalid email format")

        sender = str(msg.get("From", ""))
        sender_domain = ""
        if "@" in sender:
            sender_domain = sender.split("@")[-1].strip(">").strip()

        recipient = str(msg.get("To", ""))
        subject = str(msg.get("Subject", ""))
        message_id = str(msg.get("Message-ID", ""))

        body = self._extract_body(msg)
        urls = self._extract_urls(body)
        
        spf_pass, dkim_pass, dmarc_pass = self._parse_authentication_headers(msg)
        anomalies = self._check_anomalies(msg, sender)
        
        # Calculate Confidence Score (0.0 to 1.0)
        score = 0.0
        
        if spf_pass is False: 
            score += 0.3
        if dkim_pass is False: 
            score += 0.2
        if dmarc_pass is False: 
            score += 0.3
        
        if "reply_to_mismatch" in anomalies: 
            score += 0.4
        if "suspicious_subject" in anomalies: 
            score += 0.2
        
        if len(urls) > 5: 
            score += 0.1
        if len(urls) > 10: 
            score += 0.2
        
        score = min(1.0, score)
        
        verdict = PhishingVerdict.CLEAN
        if score > 0.7:
            verdict = PhishingVerdict.PHISHING
        elif score > 0.3:
            verdict = PhishingVerdict.SUSPICIOUS

        # Format URL details
        url_details = [{"url": u, "is_malicious": False} for u in urls[:50]] # Limit to 50
        
        # Get raw headers string
        headers = []
        for k, v in msg.items():
            headers.append(f"{k}: {v}")
        raw_headers = "\n".join(headers)

        return {
            "subject": subject,
            "sender": sender,
            "sender_domain": sender_domain,
            "recipient": recipient,
            "message_id": message_id,
            "verdict": verdict,
            "confidence_score": score * 100, # 0-100 scale for DB and UI
            "spf_pass": spf_pass,
            "dkim_pass": dkim_pass,
            "dmarc_pass": dmarc_pass,
            "urls_found": len(urls),
            "malicious_urls": 0, # Would hook into Threat Intel module ideally
            "url_details": {"urls": url_details},
            "attachments_count": 0, # Simplified for now
            "malicious_attachments": 0,
            "header_anomalies": anomalies,
            "raw_headers": raw_headers,
            "body_text": body[:5000] # truncate
        }

phishing_service = PhishingAnalysisService()
