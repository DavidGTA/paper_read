from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class RelationType(Base):
    __tablename__ = "relation_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)  # 关系类型名称
    description = Column(String(255))  # 关系类型描述
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 