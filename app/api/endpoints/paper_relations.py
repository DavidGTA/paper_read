from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import schemas, models
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/", response_model=schemas.PaperRelation)
def create_paper_relation(paper_relation: schemas.PaperRelationCreate, db: Session = Depends(get_db)):
    # 验证源论文是否存在
    source_paper = db.query(models.Paper).filter(models.Paper.id == paper_relation.source_paper_id).first()
    if not source_paper:
        raise HTTPException(status_code=404, detail="源论文不存在")
    
    # 验证目标论文是否存在
    target_paper = db.query(models.Paper).filter(models.Paper.id == paper_relation.target_paper_id).first()
    if not target_paper:
        raise HTTPException(status_code=404, detail="目标论文不存在")
    
    # 验证关系类型是否存在
    relation_type = db.query(models.RelationType).filter(models.RelationType.id == paper_relation.relation_type_id).first()
    if not relation_type:
        raise HTTPException(status_code=404, detail="关系类型不存在")
    
    # 检查是否已存在相同的关系
    existing_relation = db.query(models.PaperRelation).filter(
        models.PaperRelation.source_paper_id == paper_relation.source_paper_id,
        models.PaperRelation.target_paper_id == paper_relation.target_paper_id,
        models.PaperRelation.relation_type_id == paper_relation.relation_type_id
    ).first()
    
    if existing_relation:
        raise HTTPException(status_code=400, detail="该关系已存在")
    
    db_paper_relation = models.PaperRelation(**paper_relation.dict())
    db.add(db_paper_relation)
    db.commit()
    db.refresh(db_paper_relation)
    return db_paper_relation

@router.get("/", response_model=List[schemas.PaperRelationDetail])
def read_paper_relations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    relations = db.query(models.PaperRelation).offset(skip).limit(limit).all()
    
    # 构建详细的关系信息
    detailed_relations = []
    for relation in relations:
        source_paper = db.query(models.Paper).filter(models.Paper.id == relation.source_paper_id).first()
        target_paper = db.query(models.Paper).filter(models.Paper.id == relation.target_paper_id).first()
        relation_type = db.query(models.RelationType).filter(models.RelationType.id == relation.relation_type_id).first()
        
        detailed_relation = {
            **relation.__dict__,
            'source_paper_title': source_paper.title if source_paper else "未知论文",
            'target_paper_title': target_paper.title if target_paper else "未知论文",
            'relation_type_name': relation_type.name if relation_type else "未知关系"
        }
        detailed_relations.append(detailed_relation)
    
    return detailed_relations

@router.get("/{relation_id}", response_model=schemas.PaperRelationDetail)
def read_paper_relation(relation_id: int, db: Session = Depends(get_db)):
    relation = db.query(models.PaperRelation).filter(models.PaperRelation.id == relation_id).first()
    if relation is None:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    source_paper = db.query(models.Paper).filter(models.Paper.id == relation.source_paper_id).first()
    target_paper = db.query(models.Paper).filter(models.Paper.id == relation.target_paper_id).first()
    relation_type = db.query(models.RelationType).filter(models.RelationType.id == relation.relation_type_id).first()
    
    detailed_relation = {
        **relation.__dict__,
        'source_paper_title': source_paper.title if source_paper else "未知论文",
        'target_paper_title': target_paper.title if target_paper else "未知论文",
        'relation_type_name': relation_type.name if relation_type else "未知关系"
    }
    
    return detailed_relation

@router.put("/{relation_id}", response_model=schemas.PaperRelation)
def update_paper_relation(
    relation_id: int, 
    paper_relation: schemas.PaperRelationUpdate, 
    db: Session = Depends(get_db)
):
    db_relation = db.query(models.PaperRelation).filter(models.PaperRelation.id == relation_id).first()
    if db_relation is None:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    update_data = paper_relation.dict(exclude_unset=True)
    
    # 如果更新包含新的源论文ID，验证其存在性
    if 'source_paper_id' in update_data:
        source_paper = db.query(models.Paper).filter(models.Paper.id == update_data['source_paper_id']).first()
        if not source_paper:
            raise HTTPException(status_code=404, detail="源论文不存在")
    
    # 如果更新包含新的目标论文ID，验证其存在性
    if 'target_paper_id' in update_data:
        target_paper = db.query(models.Paper).filter(models.Paper.id == update_data['target_paper_id']).first()
        if not target_paper:
            raise HTTPException(status_code=404, detail="目标论文不存在")
    
    # 如果更新包含新的关系类型ID，验证其存在性
    if 'relation_type_id' in update_data:
        relation_type = db.query(models.RelationType).filter(models.RelationType.id == update_data['relation_type_id']).first()
        if not relation_type:
            raise HTTPException(status_code=404, detail="关系类型不存在")
    
    for field, value in update_data.items():
        setattr(db_relation, field, value)
    
    try:
        db.commit()
        db.refresh(db_relation)
        return db_relation
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="更新失败，可能存在重复关系")

@router.delete("/{relation_id}")
def delete_paper_relation(relation_id: int, db: Session = Depends(get_db)):
    relation = db.query(models.PaperRelation).filter(models.PaperRelation.id == relation_id).first()
    if relation is None:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    db.delete(relation)
    db.commit()
    return {"message": "关系已删除"} 