import json
import re

_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


def extract_json(raw: str) -> dict:
    """Pulls a JSON object out of an LLM's free-form text response — strips
    a markdown code fence if present, otherwise slices from the first `{` to
    the last `}`."""
    text = raw.strip()
    match = _FENCE_RE.search(text)
    if match:
        text = match.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)
