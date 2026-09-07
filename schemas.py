from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class WatershedCreate(BaseModel):
    name: str; district: Optional[str]=None; state: Optional[str]=None
    latitude: Optional[float]=None; longitude: Optional[float]=None; area: Optional[float]=None
class WatershedOut(WatershedCreate):
    id: int; model_config = ConfigDict(from_attributes=True)

class ImageCreate(BaseModel):
    watershed_id: Optional[int]=None; image_path: str
    latitude: Optional[float]=None; longitude: Optional[float]=None; capture_date: Optional[date]=None
class ImageOut(ImageCreate):
    id: int; model_config = ConfigDict(from_attributes=True)

class InterventionCreate(BaseModel):
    watershed_id: Optional[int]=None; type: str
    latitude: Optional[float]=None; longitude: Optional[float]=None
    date: Optional[date]=None; status: Optional[str]=None; description: Optional[str]=None
class InterventionOut(InterventionCreate):
    id: int; model_config = ConfigDict(from_attributes=True)

class AnalysisCreate(BaseModel):
    watershed_id: int; ndvi: Optional[float]=None; water_area: Optional[float]=None
    vegetation_area: Optional[float]=None; soil_area: Optional[float]=None; analysis_date: Optional[date]=None
class AnalysisOut(AnalysisCreate):
    id: int; model_config = ConfigDict(from_attributes=True)

class ChangeCreate(BaseModel):
    watershed_id: int; previous_date: Optional[date]=None; current_date: Optional[date]=None
    vegetation_change: Optional[float]=None; water_change: Optional[float]=None
    land_change: Optional[float]=None; change_percentage: Optional[float]=None
class ChangeOut(ChangeCreate):
    id: int; model_config = ConfigDict(from_attributes=True)
