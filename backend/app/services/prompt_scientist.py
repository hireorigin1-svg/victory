from app.models.critic_review import CriticReview
from app.models.research import PromptGenome


class PromptScientist:
    drift_to_gene = {
        "face": ["lens", "camera", "lighting"],
        "hair": ["costume", "lighting", "adjectives"],
        "costume": ["costume", "adjectives", "style"],
        "lighting": ["lighting", "style"],
        "environment": ["environment", "composition"],
        "camera": ["camera", "lens", "motion", "composition"],
    }

    def diagnose(self, genome: PromptGenome, review: CriticReview) -> dict:
        drift_fields = []
        if review.face_drift and "No material" not in review.face_drift:
            drift_fields.append("face")
        if review.hair_drift and "No material" not in review.hair_drift:
            drift_fields.append("hair")
        if review.costume_drift and "No material" not in review.costume_drift:
            drift_fields.append("costume")
        if review.lighting_drift and "No material" not in review.lighting_drift:
            drift_fields.append("lighting")
        if review.environment_drift and "No material" not in review.environment_drift:
            drift_fields.append("environment")
        if review.camera_drift and "No material" not in review.camera_drift:
            drift_fields.append("camera")

        suspect_genes = {
            field: [gene for gene in self.drift_to_gene[field] if genome.genes.get(gene)]
            for field in drift_fields
        }
        rewrites = [
            {
                "gene": genes[0] if genes else field,
                "action": f"Rewrite only the {genes[0] if genes else field} gene to correct {field} drift.",
            }
            for field, genes in suspect_genes.items()
        ]
        return {"drift_fields": drift_fields, "suspect_genes": suspect_genes, "rewrites": rewrites}
