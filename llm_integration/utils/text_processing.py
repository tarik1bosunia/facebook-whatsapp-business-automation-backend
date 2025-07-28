# apps/llm_integration/utils/text_processing.py
import re
from typing import Optional

class TextProcessor:
    @staticmethod
    def clean_input(text: str) -> Optional[str]:
        if not text:
            return None
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Basic profanity filtering
        text = re.sub(r'(?i)\b(bad|word|list)\b', '****', text)
        return text if 2 <= len(text) <= 1000 else None