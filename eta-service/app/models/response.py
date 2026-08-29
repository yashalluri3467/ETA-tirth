from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EtaComponentBreakdown(BaseModel):
    driving_time_seconds: float = Field(default=0.0, ge=0)
    parking_time_seconds: float = Field(default=0.0, ge=0)
    walking_time_seconds: float = Field(default=0.0, ge=0)
    queue_time_seconds: float = Field(default=0.0, ge=0)
    security_check_seconds: float = Field(default=0.0, ge=0)
    weather_delay_seconds: float = Field(default=0.0, ge=0)
    festival_delay_seconds: float = Field(default=0.0, ge=0)
    total_seconds: float = Field(default=0.0, ge=0)


class RouteOption(BaseModel):
    route_id: str
    name: str
    mode: str
    distance_meters: float
    duration_seconds: float
    crowd_level: str
    traffic_level: str
    recommended: bool
    breakdown: Optional[EtaComponentBreakdown] = None


class EtaResponse(BaseModel):
    status: str = Field(..., pattern=r"^(success|error)$")
    device_id: str
    route_distance_meters: float = Field(..., ge=0)
    travel_time_seconds: float = Field(..., ge=0, description="Final total travel + queue duration in seconds")
    base_travel_time_seconds: float = Field(default=0.0, ge=0, description="Baseline free-flow road network travel duration")
    predicted_travel_time_seconds: float = Field(default=0.0, ge=0, description="XGBoost predicted road travel duration")
    predicted_queue_time_seconds: float = Field(default=0.0, ge=0, description="XGBoost predicted temple queue wait duration")
    traffic_delay_factor: float = Field(default=1.0, ge=0, description="Ratio of XGBoost predicted duration to base duration")
    remaining_distance_meters: float = Field(..., ge=0)
    eta: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
    route_updated: bool
    ml_model_used: bool = Field(default=False, description="True if pre-trained XGBoost model artifact was executed")
    breakdown: Optional[EtaComponentBreakdown] = None
    routes: Optional[List[RouteOption]] = None

