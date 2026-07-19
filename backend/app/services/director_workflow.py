from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.scene import Scene
from app.models.shot import ShotStatus
from app.repositories.llm_interactions import LLMInteractionRepository
from app.repositories.director_workflows import DirectorWorkflowRepository
from app.repositories.scenes import SceneRepository
from app.repositories.shots import ShotRepository
from app.schemas.director_workflow import (
    DirectorWorkflowEvaluation,
    DirectorWorkflowReview,
    DirectorWorkflowStart,
    DirectorWorkflowUpload,
)
from app.services.continuity import ContinuityChecker
from app.services.director_context import DirectorContextBuilder
from app.services.llm_prompt_clients import LLMCallResult
from app.services.llm_prompt_clients import PromptLLMClients
from app.services.prompt_compiler import PromptCompiler
from app.services.vision import VisionAnalyzer
from app.services.visual_memory import VisualMemoryService


class DirectorWorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.workflows = DirectorWorkflowRepository(db)
        self.interactions = LLMInteractionRepository(db)
        self.shots = ShotRepository(db)
        self.scenes = SceneRepository(db)
        self.llms = PromptLLMClients()

    def start(self, payload: DirectorWorkflowStart):
        scene = self._scene(payload)
        shot_number = payload.shot_number or self._next_shot_number(scene.id)
        previous = self.shots.get_previous_approved(scene.id, shot_number)
        prompt, components, explanation, warnings = PromptCompiler(self.db).compile(
            scene_id=scene.id,
            user_instruction=payload.director_instruction,
            camera_id=payload.camera_id,
        )
        shot = self.shots.create(
            {
                "scene_id": scene.id,
                "shot_number": shot_number,
                "user_instruction": payload.director_instruction,
                "camera_id": payload.camera_id,
                "environment_id": payload.environment_id or scene.environment_id,
                "previous_shot_id": previous.id if previous else None,
                "lighting": payload.lighting,
                "emotion": payload.emotion,
                "pose": payload.pose,
                "prompt": prompt,
                "prompt_components": components,
                "director_explanation": explanation,
                "continuity_warnings": warnings,
                "status": ShotStatus.compiled,
            }
        )
        compiler_context = {
            "shot_id": shot.id,
            "scene_id": scene.id,
            "compiler_prompt": prompt,
            "components": components,
            "explanation": explanation,
            "warnings": warnings,
        }
        context = DirectorContextBuilder(self.db).build(scene=scene, shot=shot, compiler_context=compiler_context)
        gpt_result, claude_result = self.llms.generate_higgsfield_prompts(
            director_instruction=payload.director_instruction,
            compiler_prompt=prompt,
            context=context,
        )
        workflow = self.workflows.create(
            {
                "shot_id": shot.id,
                "director_instruction": payload.director_instruction,
                "gpt_prompt": gpt_result.response_text,
                "claude_prompt": claude_result.response_text,
                "higgsfield_prompt": gpt_result.response_text,
                "approval_status": "prompt_generated",
                "llm_context": context,
                "workflow_events": [
                    self._event("director_instruction_saved"),
                    self._event("director_knowledge_packet_loaded"),
                    self._event("gpt_prompt_generated", {"status": gpt_result.status, "model": gpt_result.model}),
                    self._event("claude_prompt_generated", {"status": claude_result.status, "model": claude_result.model}),
                    self._event("higgsfield_prompt_ready"),
                ],
            }
        )
        self._log_llm_result(workflow.id, shot.id, "initial_prompt", context, gpt_result)
        self._log_llm_result(workflow.id, shot.id, "initial_prompt", context, claude_result)
        return workflow

    def upload_result(self, workflow_id: str, payload: DirectorWorkflowUpload):
        workflow = self._workflow(workflow_id)
        shot = self._shot(workflow.shot_id)
        self.shots.update(
            shot,
            {
                "generated_image": payload.image_url,
                "generated_video": payload.video_url,
                "status": ShotStatus.generated,
            },
        )
        return self.workflows.update(
            workflow,
            {
                "uploaded_image_url": payload.image_url,
                "uploaded_video_url": payload.video_url,
                "approval_status": "result_uploaded",
                "workflow_events": [*workflow.workflow_events, self._event("higgsfield_result_uploaded")],
            },
        )

    def evaluate(self, workflow_id: str) -> DirectorWorkflowEvaluation:
        workflow = self._workflow(workflow_id)
        shot = self._shot(workflow.shot_id)
        analysis = VisionAnalyzer().analyze(shot)
        updated = self.shots.update(shot, {"vision_analysis": analysis})
        previous = self.shots.get(updated.previous_shot_id) if updated.previous_shot_id else self.shots.get_previous_approved(updated.scene_id, updated.shot_number)
        report = ContinuityChecker().compare(previous, updated)
        self.shots.update(
            updated,
            {
                "continuity_score": report.overall_continuity_score,
                "quality_score": report.overall_continuity_score,
            },
        )
        self.workflows.update(
            workflow,
            {"workflow_events": [*workflow.workflow_events, self._event("ai_evaluation_completed")]},
        )
        return DirectorWorkflowEvaluation(
            face=report.face_similarity,
            costume=report.clothing_similarity,
            environment=report.environment_similarity,
            lighting=report.lighting_similarity,
            camera=report.camera_similarity,
            overall=report.overall_continuity_score,
            decision=report.decision,
            notes=report.notes,
        )

    def review(self, workflow_id: str, payload: DirectorWorkflowReview):
        workflow = self._workflow(workflow_id)
        shot = self._shot(workflow.shot_id)
        image_url = payload.image_url or workflow.uploaded_image_url
        video_url = payload.video_url or workflow.uploaded_video_url
        if payload.approved:
            approved = self.shots.update(
                shot,
                {
                    "approved_image": image_url,
                    "approved_video": video_url,
                    "generated_image": image_url,
                    "generated_video": video_url,
                    "prompt": workflow.higgsfield_prompt,
                    "status": ShotStatus.approved,
                    "rejection_reason": None,
                },
            )
            VisualMemoryService(self.db).capture_approved_shot(approved)
            return self.workflows.update(
                workflow,
                {
                    "uploaded_image_url": image_url,
                    "uploaded_video_url": video_url,
                    "approval_status": "approved",
                    "review_reasons": payload.reasons,
                    "workflow_events": [*workflow.workflow_events, self._event("approved_shot_saved")],
                },
            )

        reasons = payload.reasons or ["Rejected by director review."]
        rejected = self.shots.update(
            shot,
            {
                "generated_image": image_url,
                "generated_video": video_url,
                "status": ShotStatus.rejected,
                "rejection_reason": "; ".join(reasons),
                "generation_attempts": shot.generation_attempts + 1,
            },
        )
        context = DirectorContextBuilder(self.db).build(
            scene=self._shot_scene(rejected),
            shot=rejected,
            compiler_context={
                **(workflow.llm_context or {}).get("current", {}).get("compiler", {}),
                "review_reasons": reasons,
                "rejected_shot_id": rejected.id,
                "rejected_image_url": image_url,
                "rejected_video_url": video_url,
            },
        )
        improved_gpt, improved_claude = self.llms.improve_higgsfield_prompts(
            director_instruction=workflow.director_instruction,
            current_gpt_prompt=workflow.gpt_prompt,
            current_claude_prompt=workflow.claude_prompt,
            reasons=reasons,
            context=context,
        )
        updated_workflow = self.workflows.update(
            workflow,
            {
                "uploaded_image_url": image_url,
                "uploaded_video_url": video_url,
                "approval_status": "rejected",
                "review_reasons": reasons,
                "improved_gpt_prompt": improved_gpt.response_text,
                "improved_claude_prompt": improved_claude.response_text,
                "higgsfield_prompt": improved_gpt.response_text,
                "llm_context": context,
                "workflow_events": [
                    *workflow.workflow_events,
                    self._event("rejection_review_saved"),
                    self._event("director_knowledge_packet_reloaded"),
                    self._event("gpt_improved_prompt_generated", {"status": improved_gpt.status, "model": improved_gpt.model}),
                    self._event("claude_improved_prompt_generated", {"status": improved_claude.status, "model": improved_claude.model}),
                ],
            },
        )
        self._log_llm_result(workflow.id, rejected.id, "rejection_repair", context, improved_gpt)
        self._log_llm_result(workflow.id, rejected.id, "rejection_repair", context, improved_claude)
        return updated_workflow

    def _scene(self, payload: DirectorWorkflowStart) -> Scene:
        if payload.scene_id:
            scene = self.scenes.get(payload.scene_id)
            if not scene:
                raise ValueError("Scene not found")
            return scene
        return self.scenes.create(
            {
                "scene_number": self._next_scene_number(),
                "script": payload.director_instruction,
                "environment_id": payload.environment_id,
                "character_ids": [],
                "prop_ids": [],
                "timeline": "Director workflow",
            }
        )

    def _workflow(self, workflow_id: str):
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError("Director workflow not found")
        return workflow

    def _shot(self, shot_id: str):
        shot = self.shots.get(shot_id)
        if not shot:
            raise ValueError("Shot not found")
        return shot

    def _shot_scene(self, shot):
        scene = self.scenes.get(shot.scene_id)
        if not scene:
            raise ValueError("Scene not found")
        return scene

    def _next_scene_number(self) -> int:
        current = self.db.scalar(select(func.max(Scene.scene_number))) or 0
        return current + 1

    def _next_shot_number(self, scene_id: str) -> int:
        current = self.db.scalar(select(func.max(self.shots.model.shot_number)).where(self.shots.model.scene_id == scene_id)) or 0
        return current + 1

    def _event(self, name: str, metadata: dict | None = None) -> dict:
        return {"event": name, **(metadata or {})}

    def _log_llm_result(
        self,
        workflow_id: str,
        shot_id: str,
        purpose: str,
        context: dict,
        result: LLMCallResult,
    ) -> None:
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
