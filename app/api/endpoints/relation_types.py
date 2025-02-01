from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import schemas, models
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/", response_model=schemas.RelationType)
def create_relation_type(relation_type: schemas.RelationTypeCreate, db: Session = Depends(get_db)):
    try:
        db_relation_type = models.RelationType(**relation_type.dict())
        db.add(db_relation_type)
        db.commit()
        db.refresh(db_relation_type)
        return db_relation_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该关系类型名称已存在")

@router.get("/", response_model=List[schemas.RelationType])
def read_relation_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    relation_types = db.query(models.RelationType).offset(skip).limit(limit).all()
    return relation_types

@router.get("/{relation_type_id}", response_model=schemas.RelationType)
def read_relation_type(relation_type_id: int, db: Session = Depends(get_db)):
    relation_type = db.query(models.RelationType).filter(models.RelationType.id == relation_type_id).first()
    if relation_type is None:
        raise HTTPException(status_code=404, detail="关系类型未找到")
    return relation_type

@router.put("/{relation_type_id}", response_model=schemas.RelationType)
def update_relation_type(
    relation_type_id: int, 
    relation_type: schemas.RelationTypeUpdate, 
    db: Session = Depends(get_db)
):
    db_relation_type = db.query(models.RelationType).filter(models.RelationType.id == relation_type_id).first()
    if db_relation_type is None:
        raise HTTPException(status_code=404, detail="关系类型未找到")
    
    try:
        for field, value in relation_type.dict(exclude_unset=True).items():
            setattr(db_relation_type, field, value)
        db.commit()
        db.refresh(db_relation_type)
        return db_relation_type
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该关系类型名称已存在")

@router.delete("/{relation_type_id}")
def delete_relation_type(relation_type_id: int, db: Session = Depends(get_db)):
    relation_type = db.query(models.RelationType).filter(models.RelationType.id == relation_type_id).first()
    if relation_type is None:
        raise HTTPException(status_code=404, detail="关系类型未找到")
    
    try:
        db.delete(relation_type)
        db.commit()
        return {"message": "关系类型已删除"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该关系类型正在被使用，无法删除") 