from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, crud
router=APIRouter(prefix="/change",tags=["Change Detection"])
@router.get("/")
def get_changes(watershed_id:int|None=None,db:Session=Depends(get_db)):
    q=db.query(models.ChangeDetection)
    return q.filter(models.ChangeDetection.watershed_id==watershed_id).all() if watershed_id else q.all()
@router.post("/",response_model=schemas.ChangeOut)
def add_change(data:schemas.ChangeCreate,db:Session=Depends(get_db)): return crud.create_change(db,data)
