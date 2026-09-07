from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, crud
router=APIRouter(prefix="/analysis",tags=["Satellite Analysis"])
@router.get("/")
def get_analysis(watershed_id:int|None=None,db:Session=Depends(get_db)):
    q=db.query(models.SatelliteAnalysis)
    return q.filter(models.SatelliteAnalysis.watershed_id==watershed_id).all() if watershed_id else q.all()
@router.post("/",response_model=schemas.AnalysisOut)
def add_analysis(data:schemas.AnalysisCreate,db:Session=Depends(get_db)): return crud.create_analysis(db,data)
