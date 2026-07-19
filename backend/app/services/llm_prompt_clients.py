from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import get_settings


class LLMCallResult(BaseModel):
    provider: str
    model: str | None
    instruction: str
    response_text: str
    status: str = "success"
    error_message: str | None = None


class PromptLLMClients:
    def generate_higgsfield_prompts(
        self,
        *,
        director_instruction: str,
        compiler_prompt: str,
        context: dict[str, Any],
    ) -> tuple[LLMCallResult, LLMCallResult]:
        instruction = self._build_instruction(
            purpose="generate",
            director_instruction=director_instruction,
            compiler_prompt=compiler_prompt,
            context=context,
        )
        return self._generate_openai(instruction), self._generate_claude(instruction)

    def improve_higgsfield_prompts(
        self,
        *,
        director_instruction: str,
        current_gpt_prompt: str | None,
        current_claude_prompt: str | None,
        reasons: list[str],
        context: dict[str, Any],
    ) -> tuple[LLMCallResult, LLMCallResult]:
        reason_text = "; ".join(reasons) if reasons else "Director rejected the shot without a written reason."
        repair_instruction = (
            "You are repairing a Higgsfield prompt using Victory's production database memory.\n"
            "Rewrite only the prompt genes needed to fix the rejected result.\n"
            "Never remove approved continuity, film bible rules, visual memory, character identity, or environment truth.\n"
            f"Original director instruction: {director_instruction}\n"
            f"Rejection reasons: {reason_text}\n"
            f"Current GPT prompt: {current_gpt_prompt}\n"
            f"Current Claude prompt: {current_claude_prompt}\n"
            f"Victory DB knowledge packet: {context}\n"
            "Return one improved cinematic Higgsfield prompt only. No markdown. No explanation."
        )
        return self._generate_openai(repair_instruction), self._generate_claude(repair_instruction)

    def _build_instruction(
        self,
        purpose: str,
        director_instruction: str,
        compiler_prompt: str,
        context: dict[str, Any],
    ) -> str:
        return (
            "You are Victory's AI Director prompt specialist.\n"
            f"Task: {purpose} one production-ready Higgsfield prompt.\n"
            "Use the Victory database knowledge packet as truth.\n"
            "Continuity priority order: previous approved shot, visual memory, film bible, character database, environment database, director instruction.\n"
            "Do not invent continuity changes. Do not contradict approved memory.\n"
            "Use rejected shots and review reasons as negative examples.\n"
            "Optimize for character identity, costume stability, environment stability, camera clarity, and Higgsfield-friendly cinematic language.\n"
            f"Director instruction: {director_instruction}\n"
            f"Compiler prompt: {compiler_prompt}\n"
            f"Victory DB knowledge packet: {context}\n"
            "Return one concise cinematic Higgsfield prompt only. No markdown. No explanation."
        )

    def _generate_openai(self, instruction: str) -> LLMCallResult:
        settings = get_settings()
        model = settings.openai_model
        if not settings.enable_real_llm_calls or not settings.openai_api_key:
            return LLMCallResult(
                provider="openai",
                model=model,
                instruction=instruction,
                response_text=self._fallback("GPT", instruction),
                status="fallback",
                error_message="Real OpenAI calls are disabled or OPENAI_API_KEY is missing.",
            )

        try:
            response = httpx.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": model, "input": instruction},
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            text = body.get("output_text") or self._extract_openai_text(body)
            return LLMCallResult(
                provider="openai",
                model=model,
                instruction=instruction,
                response_text=(text or self._fallback("GPT", instruction)).strip(),
                status="success" if text else "fallback",
                error_message=None if text else "OpenAI response did not include output text.",
            )
        except Exception as exc:
            return LLMCallResult(
                provider="openai",
                model=model,
                instruction=instruction,
                response_text=self._fallback("GPT", instruction),
                status="fallback",
                error_message=str(exc),
            )

    def _generate_claude(self, instruction: str) -> LLMCallResult:
        settings = get_settings()
        model = settings.anthropic_model
        if not settings.enable_real_llm_calls or not settings.anthropic_api_key:
            return LLMCallResult(
                provider="anthropic",
                model=model,
                instruction=instruction,
                response_text=self._fallback("Claude", instruction),
                status="fallback",
                error_message="Real Claude calls are disabled or ANTHROPIC_API_KEY is missing.",
            )

        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": model,
                    "max_tokens": 1200,
                    "messages": [{"role": "user", "content": instruction}],
                },
                timeout=60,
            )
            response.raise_for_status()
            body = response.json()
            content = body.get("content", [])
            text = "\n".join(item.get("text", "") for item in content if item.get("type") == "text")
            return LLMCallResult(
                provider="anthropic",
                model=model,
                instruction=instruction,
                response_text=(text.strip() or self._fallback("Claude", instruction)),
                status="success" if text.strip() else "fallback",
                error_message=None if text.strip() else "Claude response did not include text content.",
            )
        except Exception as exc:
            return LLMCallResult(
                provider="anthropic",
                model=model,
                instruction=instruction,
                response_text=self._fallback("Claude", instruction),
                status="fallback",
                error_message=str(exc),
            )

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
