from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class Watershed(Base):
    __tablename__ = "watersheds"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district = Column(String); state = Column(String)
    latitude = Column(Float); longitude = Column(Float); area = Column(Float)

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"))
    image_path = Column(String); latitude = Column(Float); longitude = Column(Float)
    capture_date = Column(Date); uploaded_at = Column(DateTime, server_default=func.now())

class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"))
    type = Column(String, nullable=False)
    latitude = Column(Float); longitude = Column(Float); date = Column(Date)
    status = Column(String); description = Column(Text)

class SatelliteAnalysis(Base):
    __tablename__ = "satellite_analysis"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    ndvi = Column(Float); water_area = Column(Float); vegetation_area = Column(Float)
    soil_area = Column(Float); analysis_date = Column(Date)

class ChangeDetection(Base):
    __tablename__ = "change_detection"
    id = Column(Integer, primary_key=True, index=True)
    watershed_id = Column(Integer, ForeignKey("watersheds.id"), nullable=False)
    previous_date = Column(Date); current_date = Column(Date)
    vegetation_change = Column(Float); water_change = Column(Float)
    land_change = Column(Float); change_percentage = Column(Float)
