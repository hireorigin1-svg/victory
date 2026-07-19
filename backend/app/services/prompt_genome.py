import hashlib
import re

from app.repositories.research import PromptGenomeRepository


class PromptGenomeExtractor:
    gene_names = [
        "camera",
        "lighting",
        "emotion",
        "costume",
        "environment",
        "style",
        "verbs",
        "adjectives",
        "lens",
        "composition",
        "motion",
    ]

    def __init__(self, repo: PromptGenomeRepository) -> None:
        self.repo = repo

    def extract(self, shot_id: str, prompt: str, experiment_id: str | None = None):
        genes = {
            "camera": self._match(prompt, ["camera", "angle", "shot", "frame"]),
            "lighting": self._match(prompt, ["light", "lighting", "sun", "shadow", "golden"]),
            "emotion": self._match(prompt, ["calm", "angry", "sad", "joy", "fear", "resolve"]),
            "costume": self._match(prompt, ["costume", "robe", "armor", "clothes", "crown"]),
            "environment": self._match(prompt, ["temple", "forest", "lanka", "battlefield", "courtyard"]),
            "style": self._match(prompt, ["cinematic", "realism", "mythic", "dramatic"]),
            "verbs": re.findall(r"\b(walks?|runs?|raises?|turns?|looks?|stands?|moves?)\b", prompt.lower()),
            "adjectives": re.findall(r"\b(golden|warm|dark|wide|close|slow|calm|heroic)\b", prompt.lower()),
            "lens": self._match(prompt, ["35mm", "50mm", "85mm", "anamorphic", "lens"]),
            "composition": self._match(prompt, ["center", "symmetry", "foreground", "background", "close-up"]),
            "motion": self._match(prompt, ["dolly", "pan", "tilt", "tracking", "handheld", "motion"]),
        }
        return self.repo.create(
            {
                "shot_id": shot_id,
                "experiment_id": experiment_id,
                "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "genes": genes,
            }
        )

    def _match(self, prompt: str, terms: list[str]) -> list[str]:
        lower = prompt.lower()
        return [term for term in terms if term in lower]
