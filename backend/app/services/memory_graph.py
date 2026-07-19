from app.models.shot import Shot
from app.repositories.memory_graph import MemoryGraphEdgeRepository, MemoryGraphNodeRepository


class MemoryGraphService:
    def __init__(self, nodes: MemoryGraphNodeRepository, edges: MemoryGraphEdgeRepository) -> None:
        self.nodes = nodes
        self.edges = edges

    def upsert_fact(
        self,
        source_label: str,
        source_type: str,
        source_id: str | None,
        relation: str,
        target_label: str,
        target_type: str,
        target_id: str | None,
        shot: Shot,
        properties: dict | None = None,
    ):
        source = self.nodes.find(source_type, source_id, source_label) or self.nodes.create(
            {"label": source_label, "entity_type": source_type, "entity_id": source_id, "properties": {}}
        )
        target = self.nodes.find(target_type, target_id, target_label) or self.nodes.create(
            {"label": target_label, "entity_type": target_type, "entity_id": target_id, "properties": {}}
        )
        return self.edges.create(
            {
                "source_node_id": source.id,
                "relation": relation,
                "target_node_id": target.id,
                "introduced_scene_id": shot.scene_id,
                "introduced_shot_id": shot.id,
                "properties": properties or {},
            }
        )
