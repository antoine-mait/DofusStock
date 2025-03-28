import unicodedata
import re

def sanitize_filename(filename):
    # Normalize Unicode characters
    normalized = unicodedata.normalize('NFD', filename)
    
    # Remove accent marks
    no_accents = normalized.encode('ascii', 'ignore').decode('utf-8')
    
    # Remove invalid characters and replace spaces
    sanitized = re.sub(r'[<>:"/\\|?*\'°œ]', '', no_accents)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    return sanitized