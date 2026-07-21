from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.shot import ShotStatus
from app.repositories.director_os import (
    KnowledgePacketRepository,
    ProviderTranslationRepository,
    ShotBlueprintRepository,
)
from app.repositories.generation_experiments import GenerationExperimentRepository
from app.repositories.llm_interactions import LLMInteractionRepository
from app.repositories.scenes import SceneRepository
from app.repositories.shots import ShotRepository
from app.schemas.director_os import DirectorOSV2RunRequest
from app.services.continuity import ContinuityChecker
from app.services.director_context import DirectorContextBuilder
from app.services.llm_prompt_clients import LLMCallResult, PromptLLMClients
from app.services.provider_translator import ProviderTranslator
from app.services.providers import GenerationProviderRegistry
from app.services.vision import VisionAnalyzer


class DirectorOSV2:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.scenes = SceneRepository(db)
        self.shots = ShotRepository(db)
        self.blueprints = ShotBlueprintRepository(db)
        self.packets = KnowledgePacketRepository(db)
        self.translations = ProviderTranslationRepository(db)
        self.interactions = LLMInteractionRepository(db)
        self.experiments = GenerationExperimentRepository(db)
        self.llms = PromptLLMClients()

    def run(self, payload: DirectorOSV2RunRequest) -> dict[str, Any]:
        scene = self._scene(payload)
        shot_number = self._next_shot_number(scene.id)
        previous = self.shots.get_previous_approved(scene.id, shot_number)
        shot = self.shots.create(
            {
                "scene_id": scene.id,
                "shot_number": shot_number,
                "user_instruction": payload.user_instruction,
                "prompt": None,
                "previous_shot_id": previous.id if previous else None,
                "environment_id": scene.environment_id,
                "lighting": self._infer_lighting(payload.user_instruction),
                "emotion": self._infer_emotion(payload.user_instruction),
                "pose": self._infer_motion(payload.user_instruction),
                "status": ShotStatus.compiled,
                "prompt_components": {},
                "director_explanation": [],
                "continuity_warnings": [],
            }
        )

        blueprint = self._blueprint(scene, shot, payload, previous)
        confidence = self._confidence(blueprint)
        blueprint_row = self.blueprints.create(
            {
                "shot_id": shot.id,
                "provider": payload.provider,
                "blueprint": blueprint,
                "confidence_score": confidence,
                "status": "ready",
            }
        )

        retrieval_query = self._retrieval_query(blueprint)
        packet = self._knowledge_packet(scene, shot, blueprint, retrieval_query)
        packet_row = self.packets.create(
            {
                "shot_id": shot.id,
                "blueprint_id": blueprint_row.id,
                "retrieval_query": retrieval_query,
                "packet": packet,
            }
        )

        gpt_result = self._gpt_reason(shot.id, blueprint_row.id, blueprint, packet)
        self._log_llm(None, shot.id, "blueprint_reasoning", packet, gpt_result)

        claude_review = None
        if confidence < payload.claude_review_below:
            claude_result = self._claude_review(shot.id, blueprint_row.id, blueprint, packet, gpt_result.response_text)
            self._log_llm(None, shot.id, "conditional_blueprint_review", packet, claude_result)
            claude_review = self._review_payload(claude_result)

        translated_prompt, translation_notes = ProviderTranslator().translate(
            provider=payload.provider,
            blueprint=blueprint,
            gpt_prompt=gpt_result.response_text,
            claude_review=claude_review,
        )
        provider = GenerationProviderRegistry().get(payload.provider)
        translation = self.translations.create(
            {
                "shot_id": shot.id,
                "blueprint_id": blueprint_row.id,
                "provider": provider.name,
                "provider_model": provider.capabilities.get("model_versions", [None])[0],
                "translated_prompt": translated_prompt,
                "translation_notes": translation_notes,
            }
        )

        generated = provider.generate(
            translated_prompt,
            {
                "blueprint_id": blueprint_row.id,
                "knowledge_packet_id": packet_row.id,
                "translator_notes": translation_notes,
            },
        )
        analyzed = self.shots.update(
            shot,
            {
                "prompt": translated_prompt,
                "generated_image": generated.generated_image,
                "generated_video": generated.generated_video,
                "vision_analysis": VisionAnalyzer().analyze(shot),
                "status": ShotStatus.generated,
            },
        )
        report = ContinuityChecker().compare(previous, analyzed)
        decision = "approve" if report.overall_continuity_score >= 95 else "needs_improvement"
        learning_record = self.experiments.create(
            {
                "shot_id": shot.id,
                "prompt_hash": str(abs(hash(translated_prompt))),
                "prompt": translated_prompt,
                "provider": provider.name,
                "provider_model": generated.provider_model,
                "generated_image": generated.generated_image,
                "generated_video": generated.generated_video,
                "face_score": report.face_similarity,
                "body_score": report.body_similarity,
                "costume_score": report.clothing_similarity,
                "environment_score": report.environment_similarity,
                "lighting_score": report.lighting_similarity,
                "camera_score": report.camera_similarity,
                "overall_score": report.overall_continuity_score,
                "accepted": decision == "approve",
                "metadata_json": {
                    "blueprint": blueprint,
                    "knowledge_packet_id": packet_row.id,
                    "translation_id": translation.id,
                    "confidence_score": confidence,
                    "decision": decision,
                    "cost": 0,
                    "latency_ms": 0,
                },
            }
        )
        final_shot = self.shots.update(
            analyzed,
            {
                "quality_score": report.overall_continuity_score,
                "continuity_score": report.overall_continuity_score,
                "status": ShotStatus.needs_director_approval if decision == "approve" else ShotStatus.rejected,
                "rejection_reason": None if decision == "approve" else "; ".join(report.notes),
            },
        )
        return {
            "scene_id": scene.id,
            "shot": final_shot,
            "blueprint_id": blueprint_row.id,
            "knowledge_packet_id": packet_row.id,
            "translation_id": translation.id,
            "blueprint": blueprint,
            "knowledge_packet": packet,
            "gpt_prompt": gpt_result.response_text,
            "claude_review": claude_review,
            "translated_prompt": translated_prompt,
            "confidence_score": confidence,
            "provider": provider.name,
            "evaluation": report,
            "decision": decision,
            "learning_record": {
                "experiment_id": learning_record.id,
                "accepted": learning_record.accepted,
                "overall_score": learning_record.overall_score,
                "provider": learning_record.provider,
            },
            "created_at": blueprint_row.created_at,
        }

    def _scene(self, payload: DirectorOSV2RunRequest) -> Scene:
        if payload.scene_id:
            scene = self.scenes.get(payload.scene_id)
            if not scene:
                raise ValueError("Scene not found")
            return scene
        return self.scenes.create(
            {
                "scene_number": self._next_scene_number(),
                "script": payload.script,
                "character_ids": [],
                "prop_ids": [],
                "timeline": "Director OS v2",
            }
        )

    def _blueprint(self, scene: Scene, shot, payload: DirectorOSV2RunRequest, previous) -> dict[str, Any]:
        context = DirectorContextBuilder(self.db).build(scene=scene, shot=shot, compiler_context={})
        characters = context["project_memory"]["characters"]
        props = context["project_memory"]["props"]
        environment = context["project_memory"]["environment"]
        camera = context["project_memory"]["camera"]
        return {
            "scene": scene.scene_number,
            "shot": shot.shot_number,
            "characters": self._relevant_names(characters, payload.user_instruction),
            "environment": environment,
            "camera": camera or self._default_camera(),
            "lighting": self._infer_lighting(payload.user_instruction) or (environment or {}).get("lighting"),
            "motion": self._infer_motion(payload.user_instruction),
            "emotion": self._infer_emotion(payload.user_instruction),
            "props": self._relevant_names(props, payload.user_instruction),
            "references": self._references(context),
            "director_notes": [
                payload.user_instruction,
                f"Keep continuity with shot {previous.shot_number}." if previous else "No previous approved shot; establish canonical continuity.",
            ],
            "continuity_rules": (context["project_memory"].get("film_bible") or {}).get("continuity_rules", []),
            "provider": payload.provider,
        }

    def _knowledge_packet(self, scene, shot, blueprint: dict[str, Any], retrieval_query: dict[str, Any]) -> dict[str, Any]:
        full = DirectorContextBuilder(self.db).build(
            scene=scene,
            shot=shot,
            compiler_context={"shot_blueprint": blueprint, "retrieval_query": retrieval_query},
        )
        return {
            "film_bible": full["project_memory"]["film_bible"],
            "characters": full["project_memory"]["characters"],
            "environment": full["project_memory"]["environment"],
            "camera": full["project_memory"]["camera"],
            "previous_shots": full["continuity_memory"]["previous_approved_shots"][:3],
            "visual_memories": full["continuity_memory"]["latest_visual_memories"][:5],
            "rejected_examples": full["continuity_memory"]["rejected_shots"][:5],
            "learning_memory": {
                "provider_behavior": full["learning_memory"]["provider_behavior"][:8],
                "prompt_genomes": full["learning_memory"]["recent_prompt_genomes"][:8],
                "human_reviews": full["learning_memory"]["human_reviews"][:8],
            },
            "operating_rules": full["operating_rules"],
        }

    def _gpt_reason(self, shot_id: str, blueprint_id: str, blueprint: dict[str, Any], packet: dict[str, Any]) -> LLMCallResult:
        instruction = (
            "You are GPT-5 acting as Victory's reasoning director. Improve the shot blueprint into one Higgsfield-ready cinematic prompt. "
            "Do not invent story facts. Use only the blueprint and knowledge packet. Explain nothing; return prompt text only.\n"
            f"Shot ID: {shot_id}\nBlueprint ID: {blueprint_id}\nBlueprint: {blueprint}\nKnowledge Packet: {packet}"
        )
        return self.llms._generate_openai(instruction)

    def _claude_review(
        self,
        shot_id: str,
        blueprint_id: str,
        blueprint: dict[str, Any],
        packet: dict[str, Any],
        gpt_prompt: str,
    ) -> LLMCallResult:
        instruction = (
            "You are Claude acting as Victory's continuity reviewer. Review the blueprint and GPT prompt for continuity, character, motion, lighting, camera, and prop risks. "
            "Return concise JSON-like text with warnings and suggested_edits. Do not rewrite the full movie.\n"
            f"Shot ID: {shot_id}\nBlueprint ID: {blueprint_id}\nBlueprint: {blueprint}\nKnowledge Packet: {packet}\nGPT Prompt: {gpt_prompt}"
        )
        return self.llms._generate_claude(instruction)

    def _log_llm(self, workflow_id: str | None, shot_id: str, purpose: str, context: dict, result: LLMCallResult) -> None:
        self.interactions.create(
            {
                "workflow_id": workflow_id,
                "shot_id": shot_id,
                "provider": result.provider,
                "model": result.model,
                "purpose": purpose,
                "request_context": context,
                "instruction": result.instruction,
                "response_text": result.response_text,
                "status": result.status,
                "error_message": result.error_message,
            }
        )

    def _review_payload(self, result: LLMCallResult) -> dict[str, Any]:
        return {
            "provider": result.provider,
            "model": result.model,
            "status": result.status,
            "warnings": [result.response_text[:1200]] if result.response_text else [],
            "suggested_edits": [],
        }

    def _retrieval_query(self, blueprint: dict[str, Any]) -> dict[str, Any]:
        return {
            "characters": blueprint.get("characters", []),
            "environment": (blueprint.get("environment") or {}).get("location") if isinstance(blueprint.get("environment"), dict) else blueprint.get("environment"),
            "lighting": blueprint.get("lighting"),
            "motion": blueprint.get("motion"),
            "props": blueprint.get("props", []),
            "provider": blueprint.get("provider"),
        }

    def _confidence(self, blueprint: dict[str, Any]) -> float:
        score = 100.0
        for key in ["characters", "environment", "lighting", "motion"]:
            if not blueprint.get(key):
                score -= 8
        if not blueprint.get("references"):
            score -= 6
        if "No previous approved shot" in " ".join(blueprint.get("director_notes", [])):
            score -= 5
        return max(0, min(100, score))

    def _references(self, context: dict[str, Any]) -> list[str]:
        refs: list[str] = []
        for character in context["project_memory"]["characters"]:
            refs.extend(character.get("reference_images") or [])
        environment = context["project_memory"].get("environment") or {}
        refs.extend(environment.get("reference_images") or [])
        for memory in context["continuity_memory"]["latest_visual_memories"]:
            if memory.get("approved_image"):
                refs.append(memory["approved_image"])
        return refs[:8]

    def _relevant_names(self, items: list[dict[str, Any]], instruction: str) -> list[dict[str, Any]]:
        lowered = instruction.lower()
        matched = [item for item in items if str(item.get("name", item.get("location", ""))).lower() in lowered]
        return matched or items[:4]

    def _infer_lighting(self, instruction: str) -> str | None:
        lowered = instruction.lower()
        for value in ["golden hour", "sunset", "sunrise", "moonlight", "firelight", "dawn", "night"]:
            if value in lowered:
                return value
        return None

    def _infer_motion(self, instruction: str) -> str | None:
        lowered = instruction.lower()
        for value in ["walks", "runs", "turns", "raises", "flies", "fights", "stands", "kneels"]:
            if value in lowered:
                return value
        return instruction[:160]

    def _infer_emotion(self, instruction: str) -> str | None:
        lowered = instruction.lower()
        for value in ["devotion", "calm", "anger", "heroic", "fear", "joy", "sadness"]:
            if value in lowered:
                return value
        return None

    def _default_camera(self) -> dict[str, str]:
        return {"lens": "50mm", "shot_size": "medium shot", "movement": "slow dolly", "style": "cinematic realism"}

    def _next_scene_number(self) -> int:
        current = self.db.scalar(select(func.max(Scene.scene_number))) or 0
        return current + 1

    def _next_shot_number(self, scene_id: str) -> int:
        current = self.db.scalar(select(func.max(self.shots.model.shot_number)).where(self.shots.model.scene_id == scene_id)) or 0
        return current + 1
