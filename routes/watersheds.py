from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, crud
router=APIRouter(prefix="/watersheds",tags=["Watersheds"])
@router.get("/")
def get_watersheds(db:Session=Depends(get_db)): return db.query(models.Watershed).all()
@router.post("/",response_model=schemas.WatershedOut)
def add_watershed(data:schemas.WatershedCreate,db:Session=Depends(get_db)): return crud.create_watershed(db,data)
