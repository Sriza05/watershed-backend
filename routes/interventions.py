from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, crud
router=APIRouter(prefix="/interventions",tags=["Interventions"])
@router.get("/")
def get_interventions(db:Session=Depends(get_db)): return db.query(models.Intervention).all()
@router.post("/",response_model=schemas.InterventionOut)
def add_intervention(data:schemas.InterventionCreate,db:Session=Depends(get_db)): return crud.create_intervention(db,data)
