from typing import Any

import httpx

from app.core.config import get_settings


class PromptLLMClients:
    def generate_higgsfield_prompts(
        self,
        *,
        director_instruction: str,
        compiler_prompt: str,
        context: dict[str, Any],
    ) -> tuple[str, str]:
        instruction = self._build_instruction(director_instruction, compiler_prompt, context)
        return self._generate_openai(instruction), self._generate_claude(instruction)

    def improve_higgsfield_prompts(
        self,
        *,
        director_instruction: str,
        current_gpt_prompt: str | None,
        current_claude_prompt: str | None,
        reasons: list[str],
        context: dict[str, Any],
    ) -> tuple[str, str]:
        reason_text = "; ".join(reasons) if reasons else "Director rejected the shot without a written reason."
        repair_instruction = (
            "Rewrite only what is needed to fix the rejected Higgsfield result.\n"
            f"Original director instruction: {director_instruction}\n"
            f"Rejection reasons: {reason_text}\n"
            f"Current GPT prompt: {current_gpt_prompt}\n"
            f"Current Claude prompt: {current_claude_prompt}\n"
            f"Stored DB context: {context}\n"
            "Return one improved cinematic Higgsfield prompt. Preserve all approved continuity."
        )
        return self._generate_openai(repair_instruction), self._generate_claude(repair_instruction)

    def _build_instruction(
        self,
        director_instruction: str,
        compiler_prompt: str,
        context: dict[str, Any],
    ) -> str:
        return (
            "You are generating a production-ready Higgsfield prompt.\n"
            "Use the database context as truth. Do not invent continuity changes.\n"
            f"Director instruction: {director_instruction}\n"
            f"Compiler prompt: {compiler_prompt}\n"
            f"Database context: {context}\n"
            "Return one concise cinematic prompt only."
        )

    def _generate_openai(self, instruction: str) -> str:
        settings = get_settings()
        if not settings.enable_real_llm_calls or not settings.openai_api_key:
            return self._fallback("GPT", instruction)

        try:
            response = httpx.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.openai_model, "input": instruction},
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            return body.get("output_text") or self._extract_openai_text(body) or self._fallback("GPT", instruction)
        except httpx.HTTPError:
            return self._fallback("GPT", instruction)

    def _generate_claude(self, instruction: str) -> str:
        settings = get_settings()
        if not settings.enable_real_llm_calls or not settings.anthropic_api_key:
            return self._fallback("Claude", instruction)

        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": instruction}],
                },
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            content = body.get("content", [])
            text = "\n".join(item.get("text", "") for item in content if item.get("type") == "text")
            return text.strip() or self._fallback("Claude", instruction)
        except httpx.HTTPError:
            return self._fallback("Claude", instruction)

    def _extract_openai_text(self, body: dict[str, Any]) -> str | None:
        parts: list[str] = []
        for item in body.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if text:
                    parts.append(text)
        return "\n".join(parts).strip() or None

    def _fallback(self, source: str, instruction: str) -> str:
        compact = " ".join(instruction.split())
        return (
            f"{source} local draft for Higgsfield: {compact[:900]}. "
            "Cinematic realism, locked identity, stable costume, matching environment, precise camera language."
        )
