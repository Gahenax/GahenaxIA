"""
Sanitization utility to prevent API Key corruption by ensuring outgoing 
payloads do not contain system-level secrets or metadata that trigger DLP.
"""
import os
import re

def sanitize_prompt(text: str) -> str:
    """
    Scrubs the input text of common system-level identifiers that 
    could trigger data leak prevention (DLP) filters.
    """
    if not text:
        return text
        
    scrubbed = text
    
    # 1. Anonymize User/Path patterns
    # (e.g., C:\Users\USUARIO\... -> [ANONYMIZED_PATH])
    scrubbed = re.sub(r'[a-zA-Z]:\\Users\\[^\\]+', r'[ANONYMIZED_USER_PATH]', scrubbed)
    
    # 2. Redact potential API Key patterns (AIza...)
    scrubbed = re.sub(r'AIza[0-9A-Za-z-_]{35}', r'[REDACTED_API_KEY]', scrubbed)
    
    # 3. Redact Hostname if it appears accidentally
    hostname = os.getenv("HOSTNAME")
    if hostname and len(hostname) > 3:
        scrubbed = scrubbed.replace(hostname, "[REDACTED_HOST]")
        
    return scrubbed
