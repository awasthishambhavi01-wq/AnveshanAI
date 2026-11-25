from datetime import datetime

from pydantic import BaseModel, ConfigDict



class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: str
    pages: int
    created_at: datetime
    error: str | None = None


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: str
    duplicate: bool = False