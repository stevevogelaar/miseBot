"""Natural language understanding with Ollama/Gemma 4."""
import json
import requests
import time
from typing import Dict, Any
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "gemma4:e2b"
LOG_PATH = Path(__file__).parent / "data" / "gemma_monitor.log"


def _log_gemma(level: str, prompt: str, response: str, elapsed: float = 0):
    """Log Gemma interactions for monitoring."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level}] elapsed={elapsed:.2f}s\n")
        f.write(f"  PROMPT: {prompt[:200]}...\n")
        f.write(f"  RESPONSE: {response[:300]}...\n")
        f.write("-" * 60 + "\n")


def _ask_gemma(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send a prompt to local Ollama and return the text response."""
    start = time.time()
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200},
            },
            timeout=30,
        )
        data = resp.json()
        text = data.get("response", "").strip()
        elapsed = time.time() - start
        _log_gemma("OK", prompt, text, elapsed)
        return text
    except Exception as e:
        elapsed = time.time() - start
        _log_gemma("ERROR", prompt, str(e), elapsed)
        return f"ERROR: {e}"


def _is_gemma_broken(raw: str) -> bool:
    """Detect if Gemma returned garbage instead of JSON."""
    if raw.startswith("ERROR:"):
        return True
    if "{" not in raw:
        return True
    # Check for repetitive nonsense
    words = raw.split()
    if len(words) > 50 and raw.count("the") > 20:
        return True
    return False


def parse_user_input(text: str) -> Dict[str, Any]:
    """Turn natural language into a structured action."""
    prompt = f"""
You are a kitchen assistant parser. Read the user's message and return ONLY a JSON object with keys: intent, list_type, items, quantity, unit, recipient, time_ref.

intents: add, remove, done, email, query, schedule, unknown
list_type: shopping, prep, unknown
items: list of item names
quantity: string or ""
unit: string or ""
recipient: string or ""
time_ref: string or ""

Examples:
- "Add tomatoes and cream to shopping" -> {{"intent": "add", "list_type": "shopping", "items": ["tomatoes", "cream"], "quantity": "", "unit": "", "recipient": "", "time_ref": ""}}
- "I finished whipped feta and cut fries" -> {{"intent": "done", "list_type": "prep", "items": ["whipped feta", "cut fries"], "quantity": "", "unit": "", "recipient": "", "time_ref": ""}}
- "Email my prep list to Kyle" -> {{"intent": "email", "list_type": "prep", "items": [], "quantity": "", "unit": "", "recipient": "Kyle", "time_ref": ""}}
- "What's on my shopping list?" -> {{"intent": "query", "list_type": "shopping", "items": [], "quantity": "", "unit": "", "recipient": "", "time_ref": ""}}
- "Add 5 lbs of potatoes" -> {{"intent": "add", "list_type": "shopping", "items": ["potatoes"], "quantity": "5", "unit": "lbs", "recipient": "", "time_ref": ""}}
- "Set reminder to pull rice at 3pm" -> {{"intent": "schedule", "list_type": "unknown", "items": ["pull rice"], "quantity": "", "unit": "", "recipient": "", "time_ref": "3pm"}}
- "Prep till noon, lunch half hour, dinner setup at 5" -> {{"intent": "schedule", "list_type": "unknown", "items": [], "quantity": "", "unit": "", "recipient": "", "time_ref": "noon, half hour, 5"}}

User: {text}
JSON:
"""
    raw = _ask_gemma(prompt)
    parsed = None

    # Try to extract JSON
    if not _is_gemma_broken(raw):
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                parsed = json.loads(raw[start : end + 1])
                # Validate expected keys
                required = {"intent", "list_type", "items", "quantity", "unit", "recipient", "time_ref"}
                if required.issubset(set(parsed.keys())):
                    _log_gemma("PARSE_OK", text, json.dumps(parsed))
                    return parsed
        except Exception:
            pass

    # Log fallback and use rule-based parser
    _log_gemma("FALLBACK", text, raw)
    return _fallback_parse(text)


def _fallback_parse(text: str) -> Dict[str, Any]:
    text_lower = text.lower().strip()

    # Intent detection
    intent = "unknown"
    if any(w in text_lower for w in ["add", "put", "need", "get", "buy"]):
        intent = "add"
    elif any(w in text_lower for w in ["remove", "delete", "take off", "drop"]):
        intent = "remove"
    elif any(w in text_lower for w in ["done", "finished", "complete", "did", "marked off"]):
        intent = "done"
    elif any(w in text_lower for w in ["email", "send", "mail", "text", "message"]):
        intent = "email"
    elif any(w in text_lower for w in ["what", "show", "list", "on my", "whats"]):
        intent = "query"
    elif any(w in text_lower for w in ["remind", "reminder", "schedule", "prep till", "lunch", "setup"]):
        intent = "schedule"

    # List type
    list_type = "unknown"
    if "shopping" in text_lower or "buy" in text_lower or "order" in text_lower:
        list_type = "shopping"
    elif "prep" in text_lower or "make" in text_lower or "cook" in text_lower or "form" in text_lower:
        list_type = "prep"

    # Extract items (simple noun extraction)
    items = []
    # Remove common words
    stop_words = {"add", "to", "my", "the", "and", "or", "a", "an", "of", "for", "on", "in", "list", "shopping", "prep", "done", "finished", "i", "have", "need", "get", "buy", "put", "remove", "delete", "email", "send", "mail"}
    words = [w.strip(",.;!?") for w in text_lower.split()]
    # Simple heuristic: consecutive non-stop words after intent keywords are items
    capturing = False
    current_item = []
    for w in words:
        if w in {"add", "put", "need", "get", "done", "finished", "complete"}:
            capturing = True
            continue
        if w in stop_words:
            if current_item:
                items.append(" ".join(current_item))
                current_item = []
            continue
        if capturing:
            current_item.append(w)
    if current_item:
        items.append(" ".join(current_item))

    # Quantity
    quantity = ""
    unit = ""
    import re
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lbs?|pounds?|kg|g|ea|each|bags?|bottles?|jars?|batches?|ml|L|oz)", text, re.I)
    if m:
        quantity = m.group(1)
        unit = m.group(2).lower()

    # Recipient
    recipient = ""
    m = re.search(r"to\s+(\w+)", text, re.I)
    if m:
        candidate = m.group(1).capitalize()
        if candidate.lower() not in stop_words and len(candidate) > 2:
            recipient = candidate

    # Time ref
    time_ref = ""
    if "noon" in text_lower:
        time_ref += "noon "
    if re.search(r"\d\s*pm", text_lower):
        time_ref += re.search(r"(\d\s*pm)", text_lower).group(1)

    return {
        "intent": intent,
        "list_type": list_type,
        "items": items,
        "quantity": quantity,
        "unit": unit,
        "recipient": recipient,
        "time_ref": time_ref.strip(),
    }


def generate_reply(action: Dict[str, Any], context: str = "") -> str:
    """Generate a friendly assistant reply for an action."""
    intent = action.get("intent", "unknown")
    items = action.get("items", [])
    list_type = action.get("list_type", "unknown")

    if intent == "add":
        item_str = ", ".join(items) if items else "that"
        lt = list_type if list_type != "unknown" else "list"
        return f"Added {item_str} to your {lt} list."

    if intent == "done":
        item_str = ", ".join(items) if items else "those items"
        return f"Marked {item_str} as done. Great work!"

    if intent == "email":
        recipient = action.get("recipient", "")
        lt = list_type if list_type != "unknown" else "list"
        if recipient:
            return f"Emailing your {lt} list to {recipient}. One moment..."
        return f"Ready to email your {lt} list. Who should I send it to?"

    if intent == "query":
        lt = list_type if list_type != "unknown" else "list"
        return f"Here's your {lt} list:"

    if intent == "schedule":
        return "Got it. I've updated your day schedule."

    if intent == "remove":
        item_str = ", ".join(items) if items else "that"
        return f"Removed {item_str} from your list."

    return "I'm not sure I understood that. Try: 'Add tomatoes to shopping' or 'Show me my prep list'."
