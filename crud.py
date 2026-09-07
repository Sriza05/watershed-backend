from sqlalchemy.orm import Session
import models

def save(db, model, data):
    obj = model(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def create_watershed(db, data): return save(db, models.Watershed, data)
def create_image(db, data): return save(db, models.Image, data)
def create_intervention(db, data): return save(db, models.Intervention, data)
def create_analysis(db, data): return save(db, models.SatelliteAnalysis, data)
def create_change(db, data): return save(db, models.ChangeDetection, data)
