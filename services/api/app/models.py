from pydantic import BaseModel
from typing import Optional, Dict

class Coordinates(BaseModel):
    lat: float
    lon: float

class Location(BaseModel):
    site: str
    coordinates: Coordinates

class Measurements(BaseModel):
    ac_power: float
    dc_voltage: float
    dc_current: float
    temperature_module: float
    temperature_ambient: float

class Status(BaseModel):
    operational: bool
    fault_code: Optional[str]

class Metadata(BaseModel):
    firmware_version: str
    connection_type: str

class PVReading(BaseModel):
    device_id: str
    timestamp: str
    location: Location
    measurements: Measurements
    status: Status
    metadata: Metadata
