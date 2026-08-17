"""Agentic tool-use loop, built on DeepSeek's OpenAI-compatible API.

Subclasses define SYSTEM_PROMPT and TOOLS (Anthropic input_schema format —
kept in that shape because it maps 1-to-1 onto OpenAI function parameters;
_build_tools() below does the conversion) and register tool handlers; run()
drives the loop until the model stops requesting tools and returns its
final text.
"""
import json
from typing import Any, Callable

from openai import OpenAI, APIStatusError
from fastapi import HTTPException

from app.config import settings


class BaseAgent:
    SYSTEM_PROMPT: str = ""
    TOOLS: list[dict] = []

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

    def run(self, prompt: str, context: dict | None = None) -> Any:
        system = self.SYSTEM_PROMPT
        if context:
            system += f"\n\n## Provided Context\n{json.dumps(context, indent=2, default=str)}"

        messages: list[dict] = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        tools = self._build_tools()

        while True:
            try:
                response = self.client.chat.completions.create(
                    model=settings.agent_model,
                    messages=messages,
                    tools=tools,
                    max_tokens=settings.agent_max_tokens,
                )
            except APIStatusError as e:
                if e.status_code == 429:
                    raise HTTPException(status_code=503, detail="AI service quota exhausted. Please try again later.")
                raise HTTPException(status_code=502, detail=f"DeepSeek API error: {e}")

            message = response.choices[0].message
            if not message.tool_calls:
                return message.content or ""

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
