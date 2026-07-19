from app.repositories.visual_intelligence import CinematographyStyleRepository


class CinematographyEngine:
    defaults = [
        {
            "name": "Rajamouli",
            "scenario": "hero_entry",
            "camera_rules": {"lens": "24mm", "angle": "low angle", "movement": "slow push"},
            "lighting_rules": {"style": "warm backlight", "atmosphere": "dust"},
            "composition_rules": {"rule_of_thirds": False, "negative_space": "heroic verticality", "depth_layers": 4},
            "notes": "Mythic hero staging with scale and impact.",
        },
        {
            "name": "Nolan",
            "scenario": "tension",
            "camera_rules": {"lens": "50mm", "angle": "controlled eye line", "movement": "measured push"},
            "lighting_rules": {"style": "natural contrast", "atmosphere": "practical motivated light"},
            "composition_rules": {"rule_of_thirds": True, "negative_space": "architectural"},
            "notes": "Precise spatial tension and grounded realism.",
        },
        {
            "name": "Mani Ratnam",
            "scenario": "emotional_dialogue",
            "camera_rules": {"lens": "85mm", "angle": "intimate portrait", "movement": "gentle drift"},
            "lighting_rules": {"style": "poetic warm naturalism"},
            "composition_rules": {"rule_of_thirds": True, "negative_space": "lyrical"},
            "notes": "Emotional intimacy with rich color and soft movement.",
        },
    ]

    def __init__(self, repo: CinematographyStyleRepository) -> None:
        self.repo = repo

    def seed_defaults(self):
        styles = []
        for item in self.defaults:
            existing = self.repo.get_by_name(item["name"])
            styles.append(existing or self.repo.create(item))
        return styles
