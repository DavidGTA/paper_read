from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app import schemas, models

router = APIRouter()

@router.post("/", response_model=schemas.Paper)
def create_paper(paper: schemas.PaperCreate, db: Session = Depends(get_db)):
    db_paper = models.Paper(**paper.dict())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper

@router.get("/{paper_id}", response_model=schemas.Paper)
def read_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper is None:
        raise HTTPException(status_code=404, detail="论文未找到")
    return paper

@router.get("/", response_model=List[schemas.Paper])
def read_papers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    papers = db.query(models.Paper).offset(skip).limit(limit).all()
    return papers

@router.put("/{paper_id}", response_model=schemas.Paper)
def update_paper(paper_id: int, paper: schemas.PaperUpdate, db: Session = Depends(get_db)):
    db_paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if db_paper is None:
        raise HTTPException(status_code=404, detail="论文未找到")
    
    for field, value in paper.dict(exclude_unset=True).items():
        setattr(db_paper, field, value)
    
    db.commit()
    db.refresh(db_paper)
    return db_paper

@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper is None:
        raise HTTPException(status_code=404, detail="论文未找到")
    
    db.delete(paper)
    db.commit()
    return {"message": "论文已删除"} 