from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaperBase(BaseModel):
    title: str
    authors: str
    abstract: Optional[str] = None
    notes: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class PaperUpdate(PaperBase):
    title: Optional[str] = None
    authors: Optional[str] = None

class Paper(PaperBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 