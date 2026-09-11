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
@router.get("/timeline/{watershed_id}")
def get_analysis_timeline(
    watershed_id: int,
    db: Session = Depends(get_db)
):
    analyses = db.query(
        models.SatelliteAnalysis
    ).filter(
        models.SatelliteAnalysis.watershed_id == watershed_id
    ).order_by(
        models.SatelliteAnalysis.analysis_date.asc()
    ).all()

    return [
        {
            "date": str(analysis.analysis_date),
            "ndvi": analysis.ndvi,
            "water_area": analysis.water_area,
            "vegetation_area": analysis.vegetation_area,
            "soil_area": analysis.soil_area
        }
        for analysis in analyses
    ]
@router.get("/insights/{watershed_id}")
def get_watershed_insights(
    watershed_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(models.SatelliteAnalysis).filter(
        models.SatelliteAnalysis.watershed_id == watershed_id
    ).order_by(
        models.SatelliteAnalysis.analysis_date.desc()
    ).first()

    change = db.query(models.ChangeDetection).filter(
        models.ChangeDetection.watershed_id == watershed_id
    ).order_by(
        models.ChangeDetection.current_date.desc()
    ).first()

    if not analysis:
        return {
            "watershed_id": watershed_id,
            "message": "No satellite analysis available"
        }

    # Vegetation interpretation
    if analysis.ndvi >= 0.60:
        vegetation_status = "Good"
    elif analysis.ndvi >= 0.40:
        vegetation_status = "Moderate"
    else:
        vegetation_status = "Poor"

    # Water interpretation
    if change and change.water_change >= 10:
        water_status = "Strongly Improving"
    elif change and change.water_change > 0:
        water_status = "Improving"
    elif change and change.water_change < 0:
        water_status = "Declining"
    else:
        water_status = "Stable"

    # Overall interpretation
    if vegetation_status == "Good" and water_status in [
        "Good",
        "Improving",
        "Strongly Improving"
    ]:
        overall_status = "Positive"
    elif vegetation_status == "Poor" or water_status == "Declining":
        overall_status = "Needs Attention"
    else:
        overall_status = "Moderate"

    # Recommendation
    if overall_status == "Positive":
        recommendation = (
            "Watershed conditions are improving. "
            "Continue existing conservation and vegetation measures."
        )
    elif overall_status == "Needs Attention":
        recommendation = (
            "Watershed requires attention. "
            "Prioritize water conservation and vegetation restoration."
        )
    else:
        recommendation = (
            "Continue monitoring vegetation and water conditions "
            "and evaluate ongoing interventions."
        )

    return {
        "watershed_id": watershed_id,
        "analysis_date": str(analysis.analysis_date),
        "ndvi": analysis.ndvi,
        "vegetation_status": vegetation_status,
        "water_status": water_status,
        "overall_status": overall_status,
        "recommendation": recommendation
    }
@router.get("/health/{watershed_id}")
def get_watershed_health(
    watershed_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(models.SatelliteAnalysis).filter(
        models.SatelliteAnalysis.watershed_id == watershed_id
    ).order_by(
        models.SatelliteAnalysis.analysis_date.desc()
    ).first()

    change = db.query(models.ChangeDetection).filter(
        models.ChangeDetection.watershed_id == watershed_id
    ).order_by(
        models.ChangeDetection.current_date.desc()
    ).first()

    interventions = db.query(models.Intervention).filter(
        models.Intervention.watershed_id == watershed_id
    ).all()

    if not analysis:
        return {
            "watershed_id": watershed_id,
            "message": "No analysis data available"
        }

    # -----------------------------
    # 1. NDVI SCORE
    # -----------------------------
    ndvi_score = min(max(analysis.ndvi * 100, 0), 100)

    # -----------------------------
    # 2. WATER SCORE
    # -----------------------------
    if change:
        water_score = 50 + (change.water_change * 2)
        water_score = min(max(water_score, 0), 100)
    else:
        water_score = 50

    # -----------------------------
    # 3. LAND SCORE
    # -----------------------------
    if change:
        land_score = 100 - abs(change.land_change) * 2
        land_score = min(max(land_score, 0), 100)
    else:
        land_score = 50

    # -----------------------------
    # 4. INTERVENTION SCORE
    # -----------------------------
    if interventions:
        completed = sum(
            1 for i in interventions
            if i.status.lower() == "completed"
        )

        intervention_score = (
            completed / len(interventions)
        ) * 100
    else:
        intervention_score = 0

    # -----------------------------
    # FINAL HEALTH SCORE
    # -----------------------------
    health_score = (
        ndvi_score * 0.40 +
        water_score * 0.30 +
        land_score * 0.20 +
        intervention_score * 0.10
    )

    health_score = round(health_score)

    # -----------------------------
    # RATING
    # -----------------------------
    if health_score >= 80:
        rating = "Excellent"
    elif health_score >= 65:
        rating = "Good"
    elif health_score >= 50:
        rating = "Moderate"
    else:
        rating = "Needs Attention"

    return {
        "watershed_id": watershed_id,
        "health_score": health_score,
        "rating": rating,
        "ndvi_score": round(ndvi_score),
        "water_score": round(water_score),
        "land_score": round(land_score),
        "intervention_score": round(intervention_score)
    }