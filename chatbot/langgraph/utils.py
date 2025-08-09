# utils.py
import re
from typing import Dict, Optional, Tuple, List
import difflib
try:
    import phonenumbers
except Exception:
    phonenumbers = None

PHONE_REGEX = re.compile(r'(\+?\d[\d\-\s]{6,}\d)')  # loose fallback

def extract_phone_from_text(text: str) -> Optional[str]:
    """Try phonenumbers first, fallback to regex. Return E.164 if possible, else raw digits."""
    if phonenumbers:
        for match in phonenumbers.PhoneNumberMatcher(text, None):
            try:
                num = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
                return num
            except Exception:
                return match.raw_string
    # fallback
    m = PHONE_REGEX.search(text)
    return m.group(1).strip() if m else None

def split_tokens(text: str) -> List[str]:
    # split by comma/semicolon/newline/pipe and strip
    parts = re.split(r'[,\n;|]+', text)
    return [p.strip() for p in parts if p.strip()]

def parse_customer_free_text(text: str) -> Dict[str, Optional[str]]:
    """
    Heuristic parser. Returns dict with keys: name, phone, city, police_station, area.
    Will try to find a phone token, then heuristically assign name/city/police_station.
    It will NOT invent values — if ambiguous it leaves fields None.
    """
    tokens = split_tokens(text)
    phone = extract_phone_from_text(text)
    # if phone is found, remove the token that contains it
    if phone:
        tokens = [t for t in tokens if phone not in t and re.sub(r'\D','',t) != re.sub(r'\D','',phone)]
    result = {'name': None, 'phone': phone, 'city': None, 'police_station': None, 'area': None}
    if not tokens:
        return result

    # Common patterns: [name, city, phone] or [name, phone, city] etc.
    # Heuristic: the token with digits (other than phone) likely not name.
    alpha_tokens = [t for t in tokens if not re.search(r'\d', t)]
    # assign first alpha token as name if looks like a name (short)
    if alpha_tokens:
        result['name'] = alpha_tokens[0]
    # if there are more alpha tokens, next is city, next is police_station
    if len(alpha_tokens) >= 2:
        result['city'] = alpha_tokens[1]
    if len(alpha_tokens) >= 3:
        result['police_station'] = alpha_tokens[2]
    # if tokens length ==2 and one looks like a known city? (optional enhancement)
    return result

def is_police_station_ambiguous(city: Optional[str], police_station: Optional[str]) -> bool:
    """If police_station is None or equals city (case-insensitive), treat as ambiguous."""
    if not police_station:
        return True
    if city and police_station.strip().lower() == city.strip().lower():
        return True
    return False

def ask_for_missing_fields_single_message(missing: List[str]) -> str:
    """
    Return a single message (Bengali) telling user to provide all missing fields in one message.
    """
    mapping = {
        'order_items': 'পণ্যের তালিকা (নাম ও পরিমাণ)',
        'name': 'নাম',
        'phone': 'ফোন নম্বর',
        'city': 'শহর',
        'police_station': 'নিকটস্থ থানা/পুলিশ স্টেশনের নাম',
        'area': 'এলাকা (ঐচ্ছিক)'
    }
    human = [mapping.get(m, m) for m in missing]
    human_list = "\n- ".join(human)
    prompt = (
        "অর্ডার কনফার্ম করার জন্য অনুগ্রহ করে একবারে নিচের তথ্যগুলো একই বার্তায় দিন:\n"
        f"- {human_list}\n\n"
        "উদাহরণ: `Tarik, Rajshahi, Patgram, +8801720198552, iPhone 14 x1`"
    )
    return prompt
