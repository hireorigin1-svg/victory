from typing import Any


class ProviderTranslator:
    def translate(
        self,
        *,
        provider: str,
        blueprint: dict[str, Any],
        gpt_prompt: str,
        claude_review: dict[str, Any] | None = None,
    ) -> tuple[str, list[str]]:
        provider_key = provider.lower()
        if provider_key == "higgsfield":
            return self._higgsfield(blueprint, gpt_prompt, claude_review)
        if provider_key == "veo":
            return self._generic_video(provider, blueprint, gpt_prompt, claude_review, "natural cinematic scene language")
        if provider_key == "kling":
            return self._generic_video(provider, blueprint, gpt_prompt, claude_review, "clear subject motion and camera movement")
        if provider_key == "runway":
            return self._generic_video(provider, blueprint, gpt_prompt, claude_review, "shot-by-shot cinematic continuity")
        return self._generic_video(provider, blueprint, gpt_prompt, claude_review, "provider-neutral cinematic clarity")

    def _higgsfield(
        self,
        blueprint: dict[str, Any],
        gpt_prompt: str,
        claude_review: dict[str, Any] | None,
    ) -> tuple[str, list[str]]:
        parts = [
            gpt_prompt.strip(),
            self._line("Characters", blueprint.get("characters")),
            self._line("Environment", blueprint.get("environment")),
            self._line("Camera", blueprint.get("camera")),
            self._line("Lighting", blueprint.get("lighting")),
            self._line("Motion", blueprint.get("motion")),
            self._line("Emotion", blueprint.get("emotion")),
            self._line("Props", blueprint.get("props")),
            self._line("References", blueprint.get("references")),
            "Continuity lock: preserve approved face, costume, environment, lens language, lighting, props, and motion from the knowledge packet.",
        ]
        warnings = (claude_review or {}).get("warnings") or []
        if warnings:
            parts.append(f"Claude continuity warnings to avoid: {'; '.join(map(str, warnings))}.")
        prompt = " ".join(item for item in parts if item)
        notes = [
            "Higgsfield translator prefers direct cinematic prompt text.",
            "Reference, continuity, and motion constraints are appended explicitly.",
        ]
        return prompt[:3500], notes

    def _generic_video(
        self,
        provider: str,
        blueprint: dict[str, Any],
        gpt_prompt: str,
        claude_review: dict[str, Any] | None,
        style_note: str,
    ) -> tuple[str, list[str]]:
        prompt = (
            f"{gpt_prompt.strip()} Use {style_note}. "
            f"Blueprint: {blueprint}. "
            f"Reviewer guidance: {claude_review or {'warnings': []}}"
        )
        return prompt[:3500], [f"{provider} translator used generic video prompt structure."]

    def _line(self, label: str, value: Any) -> str:
        if value in (None, "", [], {}):
            return ""
        return f"{label}: {value}."
