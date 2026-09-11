from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(
    prefix="/watersheds",
    tags=["Watersheds"]
)


@router.get("/")
def get_watersheds(
    district: str = None,
    state: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Watershed)

    if district:
        query = query.filter(
            models.Watershed.district == district
        )

    if state:
        query = query.filter(
            models.Watershed.state == state
        )

    return query.all()


@router.post("/")
def create_watershed(
    name: str,
    district: str,
    state: str,
    latitude: float,
    longitude: float,
    area: float,
    db: Session = Depends(get_db)
):
    watershed = models.Watershed(
        name=name,
        district=district,
        state=state,
        latitude=latitude,
        longitude=longitude,
        area=area
    )

    db.add(watershed)
    db.commit()
    db.refresh(watershed)

    return watershed


@router.get("/{watershed_id}")
def get_watershed_details(
    watershed_id: int,
    db: Session = Depends(get_db)
):
    watershed = db.query(models.Watershed).filter(
        models.Watershed.id == watershed_id
    ).first()

    if not watershed:
        raise HTTPException(
            status_code=404,
            detail="Watershed not found"
        )

    images = db.query(models.Image).filter(
        models.Image.watershed_id == watershed_id
    ).all()

    interventions = db.query(models.Intervention).filter(
        models.Intervention.watershed_id == watershed_id
    ).all()

    analyses = db.query(models.SatelliteAnalysis).filter(
        models.SatelliteAnalysis.watershed_id == watershed_id
    ).all()

    changes = db.query(models.ChangeDetection).filter(
        models.ChangeDetection.watershed_id == watershed_id
    ).all()

    return {
        "watershed": watershed,
        "images": images,
        "interventions": interventions,
        "satellite_analysis": analyses,
        "change_detection": changes
    }