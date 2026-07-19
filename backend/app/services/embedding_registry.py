import hashlib
import math

from app.models.character import Character
from app.models.shot import Shot
from app.repositories.embeddings import CharacterEmbeddingRepository


class CharacterEmbeddingRegistry:
    def __init__(self, repo: CharacterEmbeddingRepository) -> None:
        self.repo = repo

    def register_from_memory(
        self, character: Character, shot: Shot, memory: dict
    ):
        vector = self._vectorize(f"{character.name}|{memory}")
        return self.repo.create(
            {
                "character_id": character.id,
                "source_shot_id": shot.id,
                "source_image": shot.approved_image or shot.generated_image,
                "vector": vector,
                "metadata_json": {"memory": memory},
            }
        )

    def similarity_to_canonical(self, character: Character, memory: dict) -> float:
        embeddings = self.repo.list_for_character(character.id)
        if not embeddings:
            return 100.0
        probe = self._vectorize(f"{character.name}|{memory}")
        return round(max(self._cosine(probe, embedding.vector) for embedding in embeddings) * 100, 2)

    def _vectorize(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [round(byte / 255, 6) for byte in digest[:32]]

    def _cosine(self, left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)
