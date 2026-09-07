from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
import models
import os
from datetime import date

router = APIRouter(
    prefix="/images",
    tags=["Geo-coded Images"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
def get_images(db: Session = Depends(get_db)):
    return db.query(models.Image).all()


@router.post("/")
async def upload_image(
    watershed_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    capture_date: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Create unique filename
    filename = image.filename
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save actual image
    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    # Save image information in database
    new_image = models.Image(
        watershed_id=watershed_id,
        image_path=file_path,
        latitude=latitude,
        longitude=longitude,
        capture_date=date.fromisoformat(capture_date)
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {
        "message": "Image uploaded successfully",
        "image_id": new_image.id,
        "filename": filename,
        "path": file_path,
        "latitude": latitude,
        "longitude": longitude,
        "watershed_id": watershed_id
    }