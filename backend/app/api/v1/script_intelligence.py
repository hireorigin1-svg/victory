from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.shot import ShotStatus
from app.models.user import User, UserRole
from app.repositories.scenes import SceneRepository
from app.repositories.shots import ShotRepository
from app.schemas.script_intelligence import (
    ScriptAnalysisRequest,
    ScriptAnalysisResponse,
    StoryboardRequest,
    StoryboardResponse,
)
from app.services.prompt_compiler import PromptCompiler
from app.services.script_intelligence import ScriptIntelligenceService

router = APIRouter(prefix="/script-intelligence", tags=["script-intelligence"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.post("/analyze", response_model=ScriptAnalysisResponse)
def analyze_script(
    payload: ScriptAnalysisRequest,
    _: User = Depends(require_roles(*write_roles)),
):
    return ScriptIntelligenceService().analyze(payload.title, payload.script_text)


@router.post("/analyze-upload", response_model=ScriptAnalysisResponse)
async def analyze_script_upload(
    title: str = Form("Uploaded Script"),
    file: UploadFile = File(...),
    _: User = Depends(require_roles(*write_roles)),
):
    script_text = await _extract_upload_text(file)
    return ScriptIntelligenceService().analyze(title, script_text)


@router.post("/storyboards", response_model=StoryboardResponse)
def create_storyboards(
    payload: StoryboardRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    response = ScriptIntelligenceService().storyboards(
        payload.title,
        payload.script_text,
        payload.style,
        payload.max_panels,
    )
    if payload.create_project_records:
        _create_project_records(db, response)
    return response


@router.post("/storyboards-upload", response_model=StoryboardResponse)
async def create_storyboards_upload(
    title: str = Form("Uploaded Script"),
    style: str = Form("devotional cinematic realism"),
    max_panels: int = Form(12),
    create_project_records: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    script_text = await _extract_upload_text(file)
    response = ScriptIntelligenceService().storyboards(title, script_text, style, max_panels)
    if create_project_records:
        _create_project_records(db, response)
    return response


async def _extract_upload_text(file: UploadFile) -> str:
    content_type = file.content_type or "application/octet-stream"
    data = await file.read()
    if content_type == "application/pdf" or (file.filename or "").lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PDF extraction is unavailable because pypdf is not installed.",
            ) from exc
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = data.decode("utf-8", errors="replace")
    cleaned = text.strip()
    if len(cleaned) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract enough screenplay text from the uploaded file.",
        )
    return cleaned


def _create_project_records(db: Session, response: StoryboardResponse) -> None:
    scenes = SceneRepository(db)
    shots = ShotRepository(db)
    compiler = PromptCompiler(db)
    for panel in response.panels:
        scene = scenes.create(
            {
                "scene_number": panel.scene_number,
                "script": f"{panel.heading}\n\n{panel.action}",
                "environment_id": None,
                "character_ids": [],
                "prop_ids": [],
                "timeline": panel.heading.split(" - ")[-1].title() if " - " in panel.heading else None,
            }
        )
        prompt, components, explanation, warnings = compiler.compile(
            scene_id=scene.id,
            user_instruction=panel.image_prompt,
        )
        shot = shots.create(
            {
                "scene_id": scene.id,
                "shot_number": panel.panel_number,
                "user_instruction": panel.image_prompt,
                "prompt": prompt,
                "lighting": panel.lighting,
                "emotion": "storyboard beat",
                "pose": panel.shot_type,
                "status": ShotStatus.compiled,
                "prompt_components": components,
                "director_explanation": explanation,
                "continuity_warnings": warnings,
            }
        )
        panel.created_scene_id = scene.id
        panel.created_shot_id = shot.id
