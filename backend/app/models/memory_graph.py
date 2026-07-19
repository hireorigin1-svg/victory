from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class MemoryGraphNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "memory_graph_nodes"

    label: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), index=True)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)


class MemoryGraphEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "memory_graph_edges"

    source_node_id: Mapped[str] = mapped_column(ForeignKey("memory_graph_nodes.id"), index=True)
    relation: Mapped[str] = mapped_column(String(120), index=True)
    target_node_id: Mapped[str] = mapped_column(ForeignKey("memory_graph_nodes.id"), index=True)
    introduced_scene_id: Mapped[str | None] = mapped_column(ForeignKey("scenes.id"))
    introduced_shot_id: Mapped[str | None] = mapped_column(ForeignKey("shots.id"))
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
