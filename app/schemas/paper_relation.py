from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaperRelationBase(BaseModel):
    source_paper_id: int
    target_paper_id: int
    relation_type_id: int

class PaperRelationCreate(PaperRelationBase):
    pass

class PaperRelationUpdate(PaperRelationBase):
    source_paper_id: Optional[int] = None
    target_paper_id: Optional[int] = None
    relation_type_id: Optional[int] = None

class PaperRelation(PaperRelationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaperRelationDetail(PaperRelation):
    source_paper_title: str
    target_paper_title: str
    relation_type_name: str 