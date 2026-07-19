import hashlib

from app.repositories.visual_intelligence import PromptASTRepository


class PromptASTCompiler:
    def __init__(self, repo: PromptASTRepository) -> None:
        self.repo = repo

    def compile(self, shot_id: str, prompt: str):
        lower = prompt.lower()
        ast = {
            "type": "ROOT",
            "children": [
                {
                    "type": "Character",
                    "children": [
                        {"type": "Face", "value": self._find(lower, ["face", "eyes", "jaw"])},
                        {"type": "Costume", "value": self._find(lower, ["costume", "robe", "armor", "clothes"])},
                        {"type": "Emotion", "value": self._find(lower, ["calm", "anger", "resolve", "joy"])},
                    ],
                },
                {
                    "type": "Camera",
                    "children": [
                        {"type": "Lens", "value": self._find(lower, ["24 mm", "35mm", "50mm", "85mm", "lens"])},
                        {"type": "Movement", "value": self._find(lower, ["push", "dolly", "pan", "tracking"])},
                        {"type": "Framing", "value": self._find(lower, ["wide", "close", "low angle", "framing"])},
                    ],
                },
                {"type": "Lighting", "value": self._find(lower, ["warm", "golden", "backlight", "shadow"])},
                {"type": "Environment", "value": self._find(lower, ["temple", "forest", "lanka", "battlefield"])},
                {"type": "Style", "value": self._find(lower, ["cinematic", "mythic", "realism"])},
                {"type": "Motion", "value": self._find(lower, ["walk", "run", "raise", "turn"])},
            ],
        }
        return self.repo.create(
            {
                "shot_id": shot_id,
                "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "ast": ast,
            }
        )

    def _find(self, text: str, terms: list[str]) -> list[str]:
        return [term for term in terms if term in text]
