from sqlalchemy import select

from app.models.visual_intelligence import (
    CinematographyStyle,
    FailureCluster,
    PromptAST,
    ReferenceAsset,
    ReferenceSegment,
    ReferenceSelection,
    VisualDiff,
    VisualPlan,
    VisualSceneGraph,
)
from app.repositories.base import SQLAlchemyRepository


class VisualSceneGraphRepository(SQLAlchemyRepository[VisualSceneGraph]):
    model = VisualSceneGraph

    def latest_for_shot(self, shot_id: str) -> VisualSceneGraph | None:
        return self.db.scalars(
            select(VisualSceneGraph)
            .where(VisualSceneGraph.shot_id == shot_id)
            .order_by(VisualSceneGraph.created_at.desc())
        ).first()


class PromptASTRepository(SQLAlchemyRepository[PromptAST]):
    model = PromptAST

    def latest_for_shot(self, shot_id: str) -> PromptAST | None:
        return self.db.scalars(
            select(PromptAST).where(PromptAST.shot_id == shot_id).order_by(PromptAST.created_at.desc())
        ).first()


class VisualPlanRepository(SQLAlchemyRepository[VisualPlan]):
    model = VisualPlan

    def get_for_shot(self, shot_id: str) -> VisualPlan | None:
        return self.db.scalars(select(VisualPlan).where(VisualPlan.shot_id == shot_id)).first()


class ReferenceAssetRepository(SQLAlchemyRepository[ReferenceAsset]):
    model = ReferenceAsset


class ReferenceSegmentRepository(SQLAlchemyRepository[ReferenceSegment]):
    model = ReferenceSegment

    def list_by_type(self, segment_type: str) -> list[ReferenceSegment]:
        return list(
            self.db.scalars(
                select(ReferenceSegment).where(ReferenceSegment.segment_type == segment_type)
            ).all()
        )


class ReferenceSelectionRepository(SQLAlchemyRepository[ReferenceSelection]):
    model = ReferenceSelection


class VisualDiffRepository(SQLAlchemyRepository[VisualDiff]):
    model = VisualDiff


class FailureClusterRepository(SQLAlchemyRepository[FailureCluster]):
    model = FailureCluster


class CinematographyStyleRepository(SQLAlchemyRepository[CinematographyStyle]):
    model = CinematographyStyle

    def get_by_name(self, name: str) -> CinematographyStyle | None:
        return self.db.scalars(select(CinematographyStyle).where(CinematographyStyle.name == name)).first()
