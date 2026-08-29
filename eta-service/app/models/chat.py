from typing import Optional
from pydantic import BaseModel, Field
from app.models.request import Location


class ChatRequest(BaseModel):
    device_id: str = Field(..., min_length=1, description="Pilgrim device or user identifier")
    message: str = Field(..., min_length=1, description="Natural language question or command")
    current_location: Optional[Location] = Field(default=None, description="Current GPS coordinates of the pilgrim")
    destination: Optional[Location] = Field(default=None, description="Destination temple or landmark GPS coordinates")
    crowd_density_index: float = Field(default=0.2, ge=0.0, le=1.0)
    is_festival: bool = Field(default=False)
    weather_severity: float = Field(default=0.0, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    status: str = Field(default="success", pattern=r"^(success|error)$")
    device_id: str
    reply: str = Field(..., description="AI assistant response message")
    intent: str = Field(..., description="Detected intent e.g., eta_inquiry, queue_inquiry, departure_advice, general_info")
    recommendations: Optional[dict] = Field(default=None, description="Actionable recommendations like alternate gate, departure offset")
    eta_summary: Optional[dict] = Field(default=None, description="Structured ETA metrics if applicable")
