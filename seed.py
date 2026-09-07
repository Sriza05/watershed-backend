from datetime import date
from database import SessionLocal, engine, Base
import models
Base.metadata.create_all(bind=engine)
db=SessionLocal()
if db.query(models.Watershed).count()==0:
    w=models.Watershed(name="Demo Watershed",district="Howrah",state="West Bengal",
                       latitude=22.5958,longitude=88.2636,area=125.5)
    db.add(w); db.commit(); db.refresh(w)
    db.add_all([
        models.Image(watershed_id=w.id,image_path="demo/watershed.jpg",latitude=w.latitude,longitude=w.longitude,capture_date=date.today()),
        models.Intervention(watershed_id=w.id,type="Farm Pond",latitude=22.596,longitude=88.264,date=date.today(),status="Completed",description="Demo intervention"),
        models.SatelliteAnalysis(watershed_id=w.id,ndvi=.67,water_area=18.4,vegetation_area=72.5,soil_area=9.1,analysis_date=date.today()),
        models.ChangeDetection(watershed_id=w.id,previous_date=date(2025,6,1),current_date=date.today(),vegetation_change=12.5,water_change=8.2,land_change=-5.4,change_percentage=10.2)
    ])
    db.commit()
db.close()
print("Demo data inserted successfully.")
