from pydantic import BaseModel


class MediaUploadRead(BaseModel):
    url: str
    filename: str
    content_type: str
    size: int
