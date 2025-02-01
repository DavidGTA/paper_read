from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RelationTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class RelationTypeCreate(RelationTypeBase):
    pass

class RelationTypeUpdate(RelationTypeBase):
    name: Optional[str] = None
    description: Optional[str] = None

class RelationType(RelationTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 