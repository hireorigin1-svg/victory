import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.api.deps import require_roles
from app.core.config import get_settings
from app.models.user import User, UserRole
from app.schemas.media import MediaUploadRead

router = APIRouter(prefix="/media", tags=["media"])
write_roles = (UserRole.admin, UserRole.director, UserRole.editor)

allowed_prefixes = ("image/", "video/")


@router.post("/uploads", response_model=MediaUploadRead, status_code=status.HTTP_201_CREATED)
def upload_media(
    request: Request,
    file: UploadFile = File(...),
    _: User = Depends(require_roles(*write_roles)),
):
    content_type = file.content_type or "application/octet-stream"
    if not content_type.startswith(allowed_prefixes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image and video uploads are allowed.",
        )

    upload_dir = Path(get_settings().upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    destination = upload_dir / filename

    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    size = destination.stat().st_size
    forwarded_proto = request.headers.get("x-forwarded-proto")
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    base_url = (
        f"{forwarded_proto}://{forwarded_host}"
        if forwarded_proto and forwarded_host
        else str(request.base_url).rstrip("/")
    )
    return MediaUploadRead(
        url=f"{base_url}/uploads/{filename}",
        filename=filename,
        content_type=content_type,
        size=size,
    )
