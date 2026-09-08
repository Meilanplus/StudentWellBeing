"""Agentic tool-use loop, built on DeepSeek's OpenAI-compatible API.

Subclasses define SYSTEM_PROMPT and TOOLS (Anthropic input_schema format —
kept in that shape because it maps 1-to-1 onto OpenAI function parameters;
_build_tools() below does the conversion) and register tool handlers; run()
drives the loop until the model stops requesting tools and returns its
final text (and that response's finish_reason).
"""
import json
import logging
from typing import Any, Callable

from openai import OpenAI, APIStatusError
from fastapi import HTTPException

from app.config import settings
from app.agents.json_utils import extract_json

logger = logging.getLogger(__name__)

# Budget for a single retry when a generation is truncated (finish_reason ==
# "length") at the default agent_max_tokens — mirrors report_translator.py's
# retry pattern, which hits the same reasoning-token variance problem.
RETRY_MAX_TOKENS = 32000


class BaseAgent:
    SYSTEM_PROMPT: str = ""
    TOOLS: list[dict] = []
    # Forces syntactically valid JSON output. Left off automatically when the
    # agent has tools (below) since some providers reject combining
    # response_format=json_object with tool definitions.
    JSON_MODE = True

    def __init__(self):
        self.client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
        self._tool_handlers: dict[str, Callable] = {}

    def register_tool(self, name: str, handler: Callable) -> None:
        self._tool_handlers[name] = handler

    def _build_tools(self) -> list[dict] | None:
        if not self.TOOLS:
            return None
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in self.TOOLS
        ]

    def run(self, prompt: str, context: dict | None = None, max_tokens: int | None = None) -> tuple[str, str]:
        """Drives the tool-use loop to completion. Returns (content,
        finish_reason) of the final (non-tool-call) response."""
        system = self.SYSTEM_PROMPT
        if context:
            system += f"\n\n## Provided Context\n{json.dumps(context, indent=2, default=str)}"

        messages: list[dict] = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        tools = self._build_tools()
        extra = {"response_format": {"type": "json_object"}} if (self.JSON_MODE and not tools) else {}

        while True:
            try:
                response = self.client.chat.completions.create(
                    model=settings.agent_model,
                    messages=messages,
                    tools=tools,
                    max_tokens=max_tokens or settings.agent_max_tokens,
                    **extra,
                )
            except APIStatusError as e:
                if e.status_code == 429:
                    raise HTTPException(status_code=503, detail="AI service quota exhausted. Please try again later.")
                raise HTTPException(status_code=502, detail=f"DeepSeek API error: {e}")

            choice = response.choices[0]
            message = choice.message
            if not message.tool_calls:
                return message.content or "", choice.finish_reason

            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in message.tool_calls
                    ],
                }
            )
            for tc in message.tool_calls:
                handler = self._tool_handlers.get(tc.function.name)
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = handler(**args) if handler else {"error": f"No handler registered for tool '{tc.function.name}'"}
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result, default=str)})

    def run_json(self, prompt: str, context: dict | None = None) -> dict | None:
        """run() + parse, retrying once at a larger token budget if the
        response was truncated, and logging the raw response if parsing
        still fails. Returns None (never raises) on total failure — callers
        supply their own fallback data."""
        raw, finish_reason = self.run(prompt, context=context)
        if finish_reason == "length":
            logger.warning(
                "%s: response truncated at %d tokens, retrying at %d",
                type(self).__name__, settings.agent_max_tokens, RETRY_MAX_TOKENS,
            )
            raw, finish_reason = self.run(prompt, context=context, max_tokens=RETRY_MAX_TOKENS)

        try:
            return extract_json(raw)
        except Exception:
            logger.warning(
                "%s: failed to parse JSON response (finish_reason=%s, length=%d chars). Raw response:\n%s",
                type(self).__name__, finish_reason, len(raw), raw[:4000],
            )
            return None
