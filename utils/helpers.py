"""Utility helpers for parsing, time calc, etc."""
import re
from datetime import datetime


def parse_quantity(text: str):
    """Extract quantity + unit from text like '5 lbs of tomatoes' or 'a dozen eggs'."""
    # Patterns: 5 lbs, 10kg, 2 bags, a dozen, 3x, etc.
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(lbs?|pounds?|kg|g|grams?|oz|ounces?|ml|L|liters?|gal|gallons?|bags?|ea|each|cases?|bottles?|jars?|batches?|dozens?|x)",
        r"(a\s+dozen)\s*(.*)",
        r"(\d+)\s*x\s*(.*)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            if len(groups) >= 2:
                return groups[0], groups[1]
            return groups[0], ""
    return "", ""


def normalize_item_name(name: str):
    """Lowercase, strip punctuation, singularize simple plurals."""
    name = name.lower().strip()
    name = re.sub(r"[,.!?;:]", "", name)
    # Simple plural removal
    if name.endswith("es") and len(name) > 3:
        name = name[:-2]
    elif name.endswith("s") and len(name) > 2:
        name = name[:-1]
    return name


def time_str_to_minutes(time_str: str):
    """Convert '9:00 AM', '14:30' to minutes since midnight."""
    time_str = time_str.strip().upper()
    # Try 12-hour format
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)?", time_str)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    meridiem = m.group(3)
    if meridiem == "PM" and hour != 12:
        hour += 12
    elif meridiem == "AM" and hour == 12:
        hour = 0
    return hour * 60 + minute


def minutes_to_time_str(minutes: int):
    """Convert minutes since midnight to '9:00 AM'."""
    hour = minutes // 60
    minute = minutes % 60
    meridiem = "AM" if hour < 12 else "PM"
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour -= 12
    return f"{hour}:{minute:02d} {meridiem}"


def parse_time_blocks(text: str):
    """Parse natural language time blocks.
    e.g. 'prep till noon, lunch half hour, dinner setup at 5'
    """
    blocks = []
    # Simple keyword extraction
    if "prep" in text.lower():
        end = "noon" if "noon" in text.lower() else "12:00 PM"
        blocks.append({"label": "Prep Block", "start": "9:00 AM", "end": end})
    if "lunch" in text.lower():
        blocks.append({"label": "Lunch", "start": "12:00 PM", "end": "12:30 PM"})
    if "setup" in text.lower() or "dinner" in text.lower():
        start = "4:30 PM" if "half hour" in text.lower() or "30 min" in text.lower() else "5:00 PM"
        blocks.append({"label": "Dinner Setup", "start": start, "end": "5:00 PM"})
    return blocks


def check_low_stock(current: float, min_stock: float, usage_rate: float):
    """Return days until stock runs out."""
    if usage_rate <= 0:
        return None
    days = (current - min_stock) / (usage_rate / 7)
    return round(days, 1)
