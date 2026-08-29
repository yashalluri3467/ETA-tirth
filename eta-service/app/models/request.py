from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class EtaRequest(BaseModel):
    device_id: str = Field(..., min_length=1)
    timestamp: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
    current_location: Location
    destination: Location
    crowd_density_index: float = Field(default=0.2, ge=0.0, le=1.0, description="Crowd footfall congestion index from 0.0 (empty) to 1.0 (maximum gridlock)")
    is_festival: bool = Field(default=False, description="Flag indicating if a festival or special pilgrimage event is active")
    weather_severity: float = Field(default=0.0, ge=0.0, le=1.0, description="Weather severity factor from 0.0 (clear) to 1.0 (heavy rain/storm)")
    traffic_density: float = Field(default=0.0, ge=0.0, le=1.0, description="Road traffic congestion index from 0.0 (free flow) to 1.0 (jammed)")
    road_closure: bool = Field(default=False, description="Flag indicating active road closure along route")
    accident_reported: bool = Field(default=False, description="Flag indicating active accident reported along route")
    holiday: bool = Field(default=False, description="Flag indicating public holiday")
    include_queue_time: bool = Field(default=True, description="Whether to include predicted temple darshan queue wait time in ETA")
    travel_mode: str = Field(default="driving", description="Mode of transport: 'driving' or 'walking'")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_iso(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("timestamp must be a valid ISO 8601 UTC datetime")
        return v
