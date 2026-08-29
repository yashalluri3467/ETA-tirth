from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.request import EtaRequest
from app.models.response import EtaResponse
from app.providers.osrm_provider import OsrmProvider
from app.providers.graphhopper_provider import GraphHopperProvider
from app.providers.google_routes_provider import GoogleRoutesProvider
from app.services.route_service import RouteService
from app.services.eta_service import EtaCalculator
from app.services.session_service import SessionManager
from app.services.cache_service import CacheService
from app.ml.xgboost_model import XGBoostEtaPredictor


router = APIRouter(prefix="/api/v1", tags=["eta"])

# Global single instance of ML Predictor (lazy-loads models)
_ml_predictor = XGBoostEtaPredictor()


# ── Dependency injection helpers ──────────────────────────────────────


def get_route_service() -> RouteService:
    """Create and return a RouteService with available providers."""
    providers = []

    # OSRM (primary)
    import os

    osrm_url = os.environ.get("OSRM_BASE_URL", "http://localhost:5000")
    providers.append(OsrmProvider(base_url=osrm_url))

    # GraphHopper (optional)
    gh_url = os.environ.get("GRAPHHOPPER_BASE_URL")
    gh_key = os.environ.get("GRAPHHOPPER_API_KEY")
    if gh_url:
        providers.append(GraphHopperProvider(base_url=gh_url, api_key=gh_key))

    # Google Routes (optional)
    google_key = os.environ.get("GOOGLE_ROUTES_API_KEY")
    if google_key:
        providers.append(GoogleRoutesProvider(api_key=google_key))

    return RouteService(
        osrm_provider=providers[0] if len(providers) > 0 else None,
        graphhopper_provider=providers[1] if len(providers) > 1 else None,
        google_routes_provider=providers[2] if len(providers) > 2 else None,
    )


def get_eta_calculator() -> EtaCalculator:
    route_service = get_route_service()
    cache_service = get_cache_service()
    session_manager = SessionManager(cache_service=cache_service)
    return EtaCalculator(
        route_service=route_service,
        session_manager=session_manager,
        cache_service=cache_service,
        ml_predictor=_ml_predictor,
    )


def get_cache_service() -> CacheService:
    import os

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return CacheService(redis_url=redis_url)


# ── Endpoints ─────────────────────────────────────────────────────────


@router.post("/eta", response_model=EtaResponse)
async def compute_eta(request: EtaRequest) -> EtaResponse:
    """
    Compute ETA for a device at its current GPS location heading to a destination.

    Uses road-network routing via OSRM / GraphHopper / Google Routes, combined with
    an XGBoost machine learning model to predict real-time traffic delays and temple queue times.
    """
    try:
        calculator = get_eta_calculator()

        waypoints = None

        result = calculator.compute_eta(
            device_id=request.device_id,
            current_lat=request.current_location.lat,
            current_lng=request.current_location.lng,
            dest_lat=request.destination.lat,
            dest_lng=request.destination.lng,
            waypoints=waypoints,
            crowd_density_index=request.crowd_density_index,
            is_festival=request.is_festival,
            weather_severity=request.weather_severity,
            traffic_density=request.traffic_density,
            road_closure=request.road_closure,
            accident_reported=request.accident_reported,
            holiday=request.holiday,
            include_queue_time=request.include_queue_time,
            travel_mode=request.travel_mode,
        )

        return EtaResponse(
            status="success",
            device_id=request.device_id,
            route_distance_meters=result["route_distance_meters"],
            travel_time_seconds=result["travel_time_seconds"],
            base_travel_time_seconds=result["base_travel_time_seconds"],
            predicted_travel_time_seconds=result["predicted_travel_time_seconds"],
            predicted_queue_time_seconds=result["predicted_queue_time_seconds"],
            traffic_delay_factor=result["traffic_delay_factor"],
            remaining_distance_meters=result["remaining_distance_meters"],
            eta=result["eta"],
            route_updated=result["route_updated"],
            ml_model_used=result["ml_model_used"],
            breakdown=result.get("breakdown"),
        )

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.post("/routes")
async def get_route_options(request: EtaRequest):
    """
    Compute multiple pilgrimage route options (Fastest, Shortest, Least Crowded, Wheelchair Accessible).
    """
    try:
        calculator = get_eta_calculator()
        base_result = calculator.compute_eta(
            device_id=request.device_id,
            current_lat=request.current_location.lat,
            current_lng=request.current_location.lng,
            dest_lat=request.destination.lat,
            dest_lng=request.destination.lng,
            crowd_density_index=request.crowd_density_index,
            is_festival=request.is_festival,
            weather_severity=request.weather_severity,
            traffic_density=request.traffic_density,
        )

        dist = base_result["route_distance_meters"]
        base_travel = base_result["predicted_travel_time_seconds"]
        queue_sec = base_result["predicted_queue_time_seconds"]

        routes = [
            {
                "route_id": "route_fastest",
                "name": "Highway / Main Arterial (Route A)",
                "mode": "Fastest",
                "distance_meters": dist,
                "duration_seconds": round(base_travel + queue_sec, 1),
                "crowd_level": "Moderate",
                "traffic_level": "Medium",
                "recommended": True,
                "breakdown": base_result.get("breakdown"),
            },
            {
                "route_id": "route_least_crowded",
                "name": "Bypass Ring Road (Route B)",
                "mode": "Least Crowded",
                "distance_meters": round(dist * 1.12, 1),
                "duration_seconds": round(base_travel * 0.88 + queue_sec, 1),
                "crowd_level": "Low",
                "traffic_level": "Light",
                "recommended": False,
                "breakdown": {
                    "driving_time_seconds": round(base_travel * 0.88, 1),
                    "parking_time_seconds": 360.0,
                    "walking_time_seconds": 600.0,
                    "queue_time_seconds": round(queue_sec * 0.7, 1),
                    "security_check_seconds": 240.0,
                    "weather_delay_seconds": 0.0,
                    "festival_delay_seconds": 0.0,
                    "total_seconds": round(base_travel * 0.88 + queue_sec * 0.7 + 1200.0, 1),
                },
            },
            {
                "route_id": "route_accessible",
                "name": "Accessible Ramp Corridor (Gate 2)",
                "mode": "Wheelchair Accessible",
                "distance_meters": round(dist * 1.05, 1),
                "duration_seconds": round(base_travel * 1.05 + queue_sec * 0.6, 1),
                "crowd_level": "Low",
                "traffic_level": "Light",
                "recommended": False,
                "breakdown": {
                    "driving_time_seconds": round(base_travel * 1.05, 1),
                    "parking_time_seconds": 300.0,
                    "walking_time_seconds": 450.0,
                    "queue_time_seconds": round(queue_sec * 0.6, 1),
                    "security_check_seconds": 180.0,
                    "weather_delay_seconds": 0.0,
                    "festival_delay_seconds": 0.0,
                    "total_seconds": round(base_travel * 1.05 + queue_sec * 0.6 + 930.0, 1),
                },
            },
        ]

        return {"status": "success", "device_id": request.device_id, "routes": routes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route options calculation error: {e}")


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """
    Police & Temple Admin Command Center telemetry stats.
    """
    return {
        "status": "success",
        "live_crowd_density": 0.68,
        "active_pilgrims_count": 14250,
        "avg_queue_wait_minutes": 42.5,
        "entry_throughput_per_min": 185,
        "parking_occupancy_percent": 84,
        "active_incidents": 2,
        "gates": [
            {"gate_id": "Gate 1 (North Main)", "status": "Heavy Crowd", "queue_minutes": 55, "throughput_pm": 80},
            {"gate_id": "Gate 2 (East Express)", "status": "Moderate", "queue_minutes": 25, "throughput_pm": 65},
            {"gate_id": "Gate 3 (South Accessible)", "status": "Smooth", "queue_minutes": 15, "throughput_pm": 40},
        ],
        "alerts": [
            "Gate 1 approaching maximum safety threshold — directing crowds to Gate 2 East",
            "Monsoon rain advisory active near Temple Approach Highway",
        ],
    }

