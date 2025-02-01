from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class PaperRelation(Base):
    __tablename__ = "paper_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    target_paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    relation_type_id = Column(Integer, ForeignKey("relation_types.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 