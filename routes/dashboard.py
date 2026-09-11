from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
import models

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):

    total_watersheds = db.query(models.Watershed).count()

    total_images = db.query(models.Image).count()

    total_interventions = db.query(models.Intervention).count()

    average_ndvi = db.query(
        func.avg(models.SatelliteAnalysis.ndvi)
    ).scalar()

    total_water_area = db.query(
        func.sum(models.SatelliteAnalysis.water_area)
    ).scalar()

    total_vegetation_area = db.query(
        func.sum(models.SatelliteAnalysis.vegetation_area)
    ).scalar()

    overall_change = db.query(
        func.avg(models.ChangeDetection.change_percentage)
    ).scalar()

    return {
        "total_watersheds": total_watersheds,
        "total_images": total_images,
        "total_interventions": total_interventions,
        "average_ndvi": round(average_ndvi or 0, 2),
        "total_water_area": round(total_water_area or 0, 2),
        "total_vegetation_area": round(total_vegetation_area or 0, 2),
        "overall_change_percentage": round(overall_change or 0, 2)
    }
@router.get("/recent-activity")
def recent_activity(db: Session = Depends(get_db)):

    activities = []

    # Recent uploaded images
    images = db.query(models.Image).order_by(
        models.Image.uploaded_at.desc()
    ).limit(5).all()

    for image in images:
        activities.append({
            "type": "image_upload",
            "title": "Geo-coded image uploaded",
            "watershed_id": image.watershed_id,
            "date": str(image.uploaded_at)
        })

    # Recent interventions
    interventions = db.query(models.Intervention).order_by(
        models.Intervention.date.desc()
    ).limit(5).all()

    for intervention in interventions:
        activities.append({
            "type": "intervention",
            "title": f"{intervention.type} - {intervention.status}",
            "watershed_id": intervention.watershed_id,
            "date": str(intervention.date)
        })

    # Recent satellite analysis
    analyses = db.query(models.SatelliteAnalysis).order_by(
        models.SatelliteAnalysis.analysis_date.desc()
    ).limit(5).all()

    for analysis in analyses:
        activities.append({
            "type": "satellite_analysis",
            "title": "Satellite analysis completed",
            "watershed_id": analysis.watershed_id,
            "ndvi": analysis.ndvi,
            "date": str(analysis.analysis_date)
        })

    # Recent change detection
    changes = db.query(models.ChangeDetection).order_by(
        models.ChangeDetection.current_date.desc()
    ).limit(5).all()

    for change in changes:
        activities.append({
            "type": "change_detection",
            "title": "Change detection updated",
            "watershed_id": change.watershed_id,
            "change_percentage": change.change_percentage,
            "date": str(change.current_date)
        })

    # Sort all activities by date
    activities.sort(
        key=lambda x: x["date"],
        reverse=True
    )

    return activities[:10]
@router.get("/watershed/{watershed_id}")
def watershed_dashboard(
    watershed_id: int,
    db: Session = Depends(get_db)
):
    # Get watershed
    watershed = db.query(models.Watershed).filter(
        models.Watershed.id == watershed_id
    ).first()

    if not watershed:
        return {
            "message": "Watershed not found"
        }

    # Latest satellite analysis
    latest_analysis = db.query(
        models.SatelliteAnalysis
    ).filter(
        models.SatelliteAnalysis.watershed_id == watershed_id
    ).order_by(
        models.SatelliteAnalysis.analysis_date.desc()
    ).first()

    # Latest change detection
    latest_change = db.query(
        models.ChangeDetection
    ).filter(
        models.ChangeDetection.watershed_id == watershed_id
    ).order_by(
        models.ChangeDetection.current_date.desc()
    ).first()

    # Interventions
    interventions = db.query(
        models.Intervention
    ).filter(
        models.Intervention.watershed_id == watershed_id
    ).all()

    # Images
    images = db.query(
        models.Image
    ).filter(
        models.Image.watershed_id == watershed_id
    ).all()

    # Analysis timeline
    timeline = db.query(
        models.SatelliteAnalysis
    ).filter(
        models.SatelliteAnalysis.watershed_id == watershed_id
    ).order_by(
        models.SatelliteAnalysis.analysis_date.asc()
    ).all()

    # Calculate simple health score
    health_score = None
    health_rating = "No Data"

    if latest_analysis:
        ndvi_score = min(
            max(latest_analysis.ndvi * 100, 0),
            100
        )

        if latest_change:
            water_score = min(
                max(50 + latest_change.water_change * 2, 0),
                100
            )

            land_score = min(
                max(100 - abs(latest_change.land_change) * 2, 0),
                100
            )
        else:
            water_score = 50
            land_score = 50

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

        health_score = round(
            ndvi_score * 0.40 +
            water_score * 0.30 +
            land_score * 0.20 +
            intervention_score * 0.10
        )

        if health_score >= 80:
            health_rating = "Excellent"
        elif health_score >= 65:
            health_rating = "Good"
        elif health_score >= 50:
            health_rating = "Moderate"
        else:
            health_rating = "Needs Attention"

    return {
        "watershed": {
            "id": watershed.id,
            "name": watershed.name,
            "district": watershed.district,
            "state": watershed.state,
            "latitude": watershed.latitude,
            "longitude": watershed.longitude,
            "area": watershed.area
        },

        "health": {
            "score": health_score,
            "rating": health_rating
        },

        "latest_analysis": (
            {
                "date": str(latest_analysis.analysis_date),
                "ndvi": latest_analysis.ndvi,
                "water_area": latest_analysis.water_area,
                "vegetation_area": latest_analysis.vegetation_area,
                "soil_area": latest_analysis.soil_area
            }
            if latest_analysis else None
        ),

        "latest_change": (
            {
                "previous_date": str(
                    latest_change.previous_date
                ),
                "current_date": str(
                    latest_change.current_date
                ),
                "vegetation_change":
                    latest_change.vegetation_change,
                "water_change":
                    latest_change.water_change,
                "land_change":
                    latest_change.land_change,
                "change_percentage":
                    latest_change.change_percentage
            }
            if latest_change else None
        ),

        "interventions": [
            {
                "id": i.id,
                "type": i.type,
                "status": i.status,
                "latitude": i.latitude,
                "longitude": i.longitude,
                "date": str(i.date),
                "description": i.description
            }
            for i in interventions
        ],

        "image_count": len(images),

        "timeline": [
            {
                "date": str(a.analysis_date),
                "ndvi": a.ndvi,
                "water_area": a.water_area,
                "vegetation_area": a.vegetation_area,
                "soil_area": a.soil_area
            }
            for a in timeline
        ]
    }
@router.get("/combined")
def combined_dashboard(db: Session = Depends(get_db)):

    # Get the first available watershed
    watershed = db.query(models.Watershed).first()

    if not watershed:
        return {
            "message": "No watershed found"
        }

    # Get latest satellite analysis
    latest_analysis = db.query(
        models.SatelliteAnalysis
    ).filter(
        models.SatelliteAnalysis.watershed_id == watershed.id
    ).order_by(
        models.SatelliteAnalysis.analysis_date.desc()
    ).first()

    # Get latest change detection
    latest_change = db.query(
        models.ChangeDetection
    ).filter(
        models.ChangeDetection.watershed_id == watershed.id
    ).order_by(
        models.ChangeDetection.current_date.desc()
    ).first()

    # Get interventions
    interventions = db.query(
        models.Intervention
    ).filter(
        models.Intervention.watershed_id == watershed.id
    ).all()

    # Count images
    image_count = db.query(
        models.Image
    ).filter(
        models.Image.watershed_id == watershed.id
    ).count()

    # Calculate health score
    health_score = None
    health_rating = "No Data"

    if latest_analysis:

        ndvi_score = min(
            max(latest_analysis.ndvi * 100, 0),
            100
        )

        if latest_change:

            water_score = min(
                max(50 + latest_change.water_change * 2, 0),
                100
            )

            land_score = min(
                max(100 - abs(latest_change.land_change) * 2, 0),
                100
            )

        else:
            water_score = 50
            land_score = 50

        if interventions:

            completed = sum(
                1
                for i in interventions
                if i.status.lower() == "completed"
            )

            intervention_score = (
                completed / len(interventions)
            ) * 100

        else:
            intervention_score = 0

        health_score = round(
            ndvi_score * 0.40 +
            water_score * 0.30 +
            land_score * 0.20 +
            intervention_score * 0.10
        )

        if health_score >= 80:
            health_rating = "Excellent"
        elif health_score >= 65:
            health_rating = "Good"
        elif health_score >= 50:
            health_rating = "Moderate"
        else:
            health_rating = "Needs Attention"

    return {

        "watershed": {
            "id": watershed.id,
            "name": watershed.name,
            "district": watershed.district,
            "state": watershed.state,
            "latitude": watershed.latitude,
            "longitude": watershed.longitude,
            "area": watershed.area
        },

        "health": {
            "score": health_score,
            "rating": health_rating
        },

        "latest_analysis": (
            {
                "date": str(latest_analysis.analysis_date),
                "ndvi": latest_analysis.ndvi,
                "water_area": latest_analysis.water_area,
                "vegetation_area": latest_analysis.vegetation_area,
                "soil_area": latest_analysis.soil_area
            }
            if latest_analysis else None
        ),

        "latest_change": (
            {
                "previous_date": str(
                    latest_change.previous_date
                ),
                "current_date": str(
                    latest_change.current_date
                ),
                "vegetation_change":
                    latest_change.vegetation_change,
                "water_change":
                    latest_change.water_change,
                "land_change":
                    latest_change.land_change,
                "change_percentage":
                    latest_change.change_percentage
            }
            if latest_change else None
        ),

        "interventions": [
            {
                "id": i.id,
                "type": i.type,
                "status": i.status,
                "latitude": i.latitude,
                "longitude": i.longitude,
                "date": str(i.date),
                "description": i.description
            }
            for i in interventions
        ],

        "image_count": image_count,

        "timeline": [
            {
                "date": str(a.analysis_date),
                "ndvi": a.ndvi,
                "water_area": a.water_area,
                "vegetation_area": a.vegetation_area,
                "soil_area": a.soil_area
            }
            for a in db.query(
                models.SatelliteAnalysis
            ).filter(
                models.SatelliteAnalysis.watershed_id == watershed.id
            ).order_by(
                models.SatelliteAnalysis.analysis_date.asc()
            ).all()
        ]
    }