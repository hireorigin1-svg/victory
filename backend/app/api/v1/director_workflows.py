from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.director_workflows import DirectorWorkflowRepository
from app.schemas.director_workflow import (
    DirectorWorkflowEvaluation,
    DirectorWorkflowRead,
    DirectorWorkflowReview,
    DirectorWorkflowStart,
    DirectorWorkflowUpload,
)
from app.services.director_workflow import DirectorWorkflowService

router = APIRouter(prefix="/director-workflows", tags=["director-workflows"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)


@router.get("", response_model=list[DirectorWorkflowRead])
def list_director_workflows(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return DirectorWorkflowRepository(db).list_latest()


@router.get("/{workflow_id}", response_model=DirectorWorkflowRead)
def get_director_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    workflow = DirectorWorkflowRepository(db).get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return workflow


@router.post("/start", response_model=DirectorWorkflowRead, status_code=status.HTTP_201_CREATED)
def start_director_workflow(
    payload: DirectorWorkflowStart,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    try:
        return DirectorWorkflowService(db).start(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{workflow_id}/upload-result", response_model=DirectorWorkflowRead)
def upload_director_workflow_result(
    workflow_id: str,
    payload: DirectorWorkflowUpload,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    try:
        return DirectorWorkflowService(db).upload_result(workflow_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{workflow_id}/evaluate", response_model=DirectorWorkflowEvaluation)
def evaluate_director_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    try:
        return DirectorWorkflowService(db).evaluate(workflow_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{workflow_id}/review", response_model=DirectorWorkflowRead)
def review_director_workflow(
    workflow_id: str,
    payload: DirectorWorkflowReview,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(*write_roles)),
):
    try:
        return DirectorWorkflowService(db).review(workflow_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
