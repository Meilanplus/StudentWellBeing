"""Translates a saved report's free-text fields for display. Both risk
assessment reports (Agent 1) and intervention plans (Agent 2) are always
stored in Bahasa Malaysia (see app/api/risk.py); this converts that
canonical Malay content into whatever language the viewer currently has
selected. Schema-agnostic by design — it works on the raw JSONB dict of
either report type, since both are free-form enough that hardcoding field
names per schema would need duplicating for every new report type."""
import json

from openai import OpenAI

from app.agents.json_utils import extract_json
from app.config import settings

LANGUAGE_NAMES = {"ms": "Bahasa Malaysia", "en": "English", "zh": "Mandarin Chinese", "ta": "Tamil"}


def translate_report_data(report_data: dict, target_language: str) -> dict:
    if target_language == "ms" or not report_data:
        return report_data

    lang_name = LANGUAGE_NAMES.get(target_language, target_language)
    client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    prompt = f"""Translate the human-readable free-text VALUES in the following JSON object \
from Bahasa Malaysia into {lang_name}.

Rules:
- Translate prose/sentence values: summaries, descriptions, indicators, evidence,
  recommendations, strategies, action items, rationale, and similar free text.
- Do NOT translate or modify: field names/keys, fixed enum-like values (e.g. risk levels
  such as "Low Risk"/"Moderate Risk"/"High Risk", severity/category labels), student IDs,
  names, dates, numbers, or booleans — copy those through exactly as given.
- Keep the exact same JSON structure and keys as the input.
- Respond with ONLY the translated JSON object, no prose.

Input JSON:
{json.dumps(report_data, ensure_ascii=False)}
"""
    try:
        response = client.chat.completions.create(
            model=settings.agent_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=settings.agent_max_tokens,
        )
        return extract_json(response.choices[0].message.content or "")
    except Exception:
        return report_data
