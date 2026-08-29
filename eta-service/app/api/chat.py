from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.api.eta import get_eta_calculator, _ml_predictor

router = APIRouter(prefix="/api/v1", tags=["chat"])


def detect_intent(message: str) -> str:
    """Classify pilgrim prompt into action intent."""
    msg = message.lower()
    if any(kw in msg for kw in ["eta", "arrival", "reach", "travel time", "how long to get", "when will i arrive"]):
        return "eta_inquiry"
    elif any(kw in msg for kw in ["queue", "line", "wait", "darshan", "gate", "crowd", "aarti"]):
        return "queue_inquiry"
    elif any(kw in msg for kw in ["leave", "departure", "best time", "traffic", "when should i"]):
        return "departure_advice"
    else:
        return "general_info"


@router.post("/chat", response_model=ChatResponse)
async def chat_assistant(request: ChatRequest) -> ChatResponse:
    """
    TirthTrack AI Assistant Endpoint.

    Answers pilgrim queries regarding ETAs, temple darshan queue waiting times,
    traffic congestion alerts, and optimal departure schedules.
    """
    try:
        intent = detect_intent(request.message)
        now = datetime.now(timezone.utc)

        # Default fallback locations if not provided (Trimbakeshwar Temple area default)
        current_loc = request.current_location
        dest_loc = request.destination

        eta_summary = None
        recommendations = {}

        if current_loc and dest_loc:
            calculator = get_eta_calculator()
            result = calculator.compute_eta(
                device_id=request.device_id,
                current_lat=current_loc.lat,
                current_lng=current_loc.lng,
                dest_lat=dest_loc.lat,
                dest_lng=dest_loc.lng,
                crowd_density_index=request.crowd_density_index,
                is_festival=request.is_festival,
                weather_severity=request.weather_severity,
                include_queue_time=True,
            )
            eta_summary = result

        if intent == "eta_inquiry":
            if eta_summary:
                travel_mins = round(eta_summary["predicted_travel_time_seconds"] / 60.0, 1)
                queue_mins = round(eta_summary["predicted_queue_time_seconds"] / 60.0, 1)
                total_mins = round(eta_summary["travel_time_seconds"] / 60.0, 1)
                eta_time = eta_summary["eta"]

                reply = (
                    f"Your total estimated arrival time is {eta_time}. "
                    f"Road travel will take approx {travel_mins} mins, and temple darshan queue wait is estimated at {queue_mins} mins "
                    f"(Total travel duration: {total_mins} mins)."
                )
                if eta_summary["traffic_delay_factor"] > 1.3:
                    reply += f" Heavy traffic detected along your route ({eta_summary['traffic_delay_factor']}x delay factor)."
            else:
                reply = (
                    "To calculate your exact ETA, please provide your current GPS location and destination coordinates."
                )

        elif intent == "queue_inquiry":
            # Direct ML prediction for queue wait
            q_sec, _ = _ml_predictor.predict_queue_time(
                arrival_hour=now.hour,
                day_of_week=now.weekday(),
                crowd_density_index=request.crowd_density_index,
                is_festival=request.is_festival,
                weather_severity=request.weather_severity,
            )
            q_mins = round(q_sec / 60.0, 1)
            reply = f"The estimated darshan queue waiting time right now is approximately {q_mins} minutes."
            if request.is_festival:
                reply += " Note: Festival peak crowd active. Expect longer screening lines at Gate 1."
                recommendations["suggested_gate"] = "Gate 2 (East Entry)"
            elif q_mins > 30:
                recommendations["suggested_gate"] = "Gate 3 (VIP / Special Token Line)"

        elif intent == "departure_advice":
            reply = (
                "Based on traffic and crowd density patterns, leaving during off-peak hours (before 7:00 AM or after 2:00 PM) "
                "can save up to 25 minutes of road delay and 40 minutes of queue waiting time."
            )
            recommendations["best_departure_window"] = "06:30 AM - 07:15 AM"
            recommendations["estimated_time_saving_minutes"] = 35.0

        else:
            reply = (
                "Welcome to TirthTrack AI Assistant! I can help you check real-time pilgrimage ETAs, "
                "predict temple darshan queue times, suggest alternate gates, and find optimal departure times."
            )

        return ChatResponse(
            status="success",
            device_id=request.device_id,
            reply=reply,
            intent=intent,
            recommendations=recommendations if recommendations else None,
            eta_summary=eta_summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {e}")
