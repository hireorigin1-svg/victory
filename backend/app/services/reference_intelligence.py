from sqlalchemy.orm import Session

from app.models.visual_intelligence import ReferenceAsset
from app.repositories.visual_intelligence import (
    ReferenceAssetRepository,
    ReferenceSegmentRepository,
    ReferenceSelectionRepository,
)
from app.services.vector_utils import cosine, vectorize_text


class ReferenceIntelligence:
    segment_types = ["face", "hair", "costume", "props", "background"]

    def __init__(self, db: Session) -> None:
        self.assets = ReferenceAssetRepository(db)
        self.segments = ReferenceSegmentRepository(db)
        self.selections = ReferenceSelectionRepository(db)

    def ingest(self, payload: dict) -> tuple[ReferenceAsset, list]:
        asset = self.assets.create(payload)
        segments = [self._create_segment(asset, segment_type) for segment_type in self.segment_types]
        return asset, segments

    def select_for_shot(self, shot_id: str, requested_continuity: dict):
        selected = []
        rationale = []
        for segment_type in ["face", "costume", "background", "props"]:
            query = str(requested_continuity.get(segment_type) or requested_continuity or segment_type)
            query_vector = vectorize_text(query)
            candidates = self.segments.list_by_type(segment_type)
            ranked = sorted(
                candidates,
                key=lambda segment: (
                    cosine(query_vector, segment.embedding),
                    segment.quality_score or 0,
                ),
                reverse=True,
            )
            if ranked:
                best = ranked[0]
                selected.append(
                    {
                        "segment_id": best.id,
                        "segment_type": best.segment_type,
                        "crop_url": best.crop_url,
                        "score": round(cosine(query_vector, best.embedding) * 100, 2),
                    }
                )
                rationale.append(
                    f"Selected {best.segment_type} reference {best.id} because it best matches requested continuity."
                )
        return self.selections.create(
            {
                "shot_id": shot_id,
                "requested_continuity": requested_continuity,
                "selected_segments": selected,
                "rationale": rationale,
            }
        )

    def _create_segment(self, asset: ReferenceAsset, segment_type: str):
        features = {
            "source_image": asset.image_url,
            "segment_type": segment_type,
            "character_id": asset.character_id,
            "environment_id": asset.environment_id,
        }
        return self.segments.create(
            {
                "reference_asset_id": asset.id,
                "segment_type": segment_type,
                "crop_url": f"{asset.image_url}#{segment_type}",
                "embedding": vectorize_text(f"{asset.image_url}|{segment_type}|{features}"),
                "features": features,
                "quality_score": asset.quality_score or 100,
            }
        )
