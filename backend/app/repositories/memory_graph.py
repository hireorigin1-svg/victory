from sqlalchemy import select

from app.models.memory_graph import MemoryGraphEdge, MemoryGraphNode
from app.repositories.base import SQLAlchemyRepository


class MemoryGraphNodeRepository(SQLAlchemyRepository[MemoryGraphNode]):
    model = MemoryGraphNode

    def find(self, entity_type: str, entity_id: str | None, label: str) -> MemoryGraphNode | None:
        return self.db.scalars(
            select(MemoryGraphNode).where(
                MemoryGraphNode.entity_type == entity_type,
                MemoryGraphNode.entity_id == entity_id,
                MemoryGraphNode.label == label,
            )
        ).first()


class MemoryGraphEdgeRepository(SQLAlchemyRepository[MemoryGraphEdge]):
    model = MemoryGraphEdge

    def list_edges(self) -> list[MemoryGraphEdge]:
        return self.list(limit=1000)
