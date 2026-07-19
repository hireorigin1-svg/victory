from statistics import mean

from app.models.character import Character
from app.repositories.embeddings import CharacterEmbeddingRepository
from app.repositories.research import CharacterIdentityProfileRepository


class CharacterIdentityModel:
    def __init__(
        self,
        profiles: CharacterIdentityProfileRepository,
        embeddings: CharacterEmbeddingRepository,
    ) -> None:
        self.profiles = profiles
        self.embeddings = embeddings

    def rebuild(self, character: Character):
        embeddings = self.embeddings.list_for_character(character.id)
        vectors = [embedding.vector for embedding in embeddings if embedding.vector]
        canonical = self._average_vector(vectors)
        profile = {
            "name": character.name,
            "face": character.face,
            "hair": character.hair,
            "skin": character.skin,
            "body": character.body,
            "clothes": character.clothes,
            "approved_sources": [embedding.source_image for embedding in embeddings],
        }
        stability = self._stability(vectors, canonical)
        existing = self.profiles.get_for_character(character.id)
        payload = {
            "character_id": character.id,
            "approved_image_count": len(vectors),
            "canonical_vector": canonical,
            "profile": profile,
            "stability_score": stability,
        }
        return self.profiles.update(existing, payload) if existing else self.profiles.create(payload)

    def _average_vector(self, vectors: list[list[float]]) -> list[float]:
        if not vectors:
            return []
        width = min(len(vector) for vector in vectors)
        return [round(mean(vector[index] for vector in vectors), 6) for index in range(width)]

    def _stability(self, vectors: list[list[float]], canonical: list[float]) -> float:
        if not vectors or not canonical:
            return 100.0
        distances = []
        for vector in vectors:
            distances.append(sum(abs(a - b) for a, b in zip(vector, canonical)) / len(canonical))
        return round(max(0, 100 - mean(distances) * 100), 2)
