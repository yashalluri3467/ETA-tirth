from datetime import datetime, timezone, timedelta
from typing import Optional

from app.utils.coordinate_validator import haversine_distance_meters


# Optimization thresholds
RECALC_DISTANCE_THRESHOLD_METERS = 25.0  # Recalculate if user moved >25m
RECALC_TIME_INTERVAL_SECONDS = 45.0  # Recalculate every 45s
ROUTE_DEVIATION_THRESHOLD_METERS = 50.0  # Recalculate if deviated >50m from route


class EtaCalculator:
    """Computes ETA from route data with optimization strategy and ML refinement."""

    def __init__(
        self,
        route_service: Optional[object] = None,
        session_manager: Optional[object] = None,
        cache_service: Optional[object] = None,
        ml_predictor: Optional[object] = None,
    ):
        self.route_service = route_service
        self.session_manager = session_manager
        self.cache_service = cache_service
        self.ml_predictor = ml_predictor

    def compute_eta(
        self,
        device_id: str,
        current_lat: float,
        current_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: Optional[list[tuple[float, float]]] = None,
        force_recalculate: bool = False,
        crowd_density_index: float = 0.2,
        is_festival: bool = False,
        weather_severity: float = 0.0,
        traffic_density: float = 0.0,
        road_closure: bool = False,
        accident_reported: bool = False,
        holiday: bool = False,
        include_queue_time: bool = True,
        travel_mode: str = "driving",
    ) -> dict:
        """
        Compute ETA for a device at its current location heading to a destination.

        Uses the optimization strategy & XGBoost ML predictions:
        - Reuse cached route if user hasn't moved significantly
        - Recalculate if user moved >25m, deviated from route, destination changed, or >45s elapsed
        - Predict real-time traffic delay multiplier and temple darshan queue waiting duration
        """
        now = datetime.now(timezone.utc)

        # Check for cached session
        session = None
        if self.session_manager:
            session = self.session_manager.get_session(device_id)

        # Determine if we need to recalculate
        needs_recalculation = force_recalculate

        if session is not None and not needs_recalculation:
            # Check distance moved from origin
            distance_moved = self.session_manager.distance_from_origin(session, current_lat, current_lng)
            if distance_moved > RECALC_DISTANCE_THRESHOLD_METERS:
                needs_recalculation = True

            # Check route deviation
            if not needs_recalculation and self.session_manager.has_deviated(session, current_lat, current_lng, ROUTE_DEVIATION_THRESHOLD_METERS):
                needs_recalculation = True

            # Check if destination changed
            dest = session.get("destination", {})
            if dest.get("lat") != dest_lat or dest.get("lng") != dest_lng:
                needs_recalculation = True

            # Check time since last route calculation
            if not needs_recalculation:
                updated_at_str = session.get("updated_at", "")
                if updated_at_str:
                    try:
                        updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                        elapsed = (now - updated_at.replace(tzinfo=timezone.utc)).total_seconds()
                        if elapsed > RECALC_TIME_INTERVAL_SECONDS:
                            needs_recalculation = True
                    except (ValueError, AttributeError):
                        needs_recalculation = True

        # Check cache for existing route
        cached_route = None
        if not needs_recalculation and self.cache_service:
            cached_route = self.cache_service.get_cached_route(current_lat, current_lng, dest_lat, dest_lng)

        if needs_recalculation or cached_route is None:
            # Compute new route
            if self.route_service is None:
                raise RuntimeError("No routing service available")

            route = self.route_service.get_best_route(
                current_lat, current_lng, dest_lat, dest_lng, waypoints
            )

            # Cache the route
            if self.cache_service:
                self.cache_service.cache_route(
                    current_lat, current_lng, dest_lat, dest_lng,
                    route,
                    ttl_seconds=300,
                )

            # Update session
            if self.session_manager:
                self.session_manager.create_or_update_session(
                    device_id, current_lat, current_lng,
                    dest_lat, dest_lng,
                    route["distance_meters"],
                    route["geometry"],
                )

            route_distance = route["distance_meters"]
            route_updated = True

            # Calibrate base travel time for realistic pilgrimage speeds
            if travel_mode.lower() == "walking":
                # Average human walking speed in pilgrimage areas: ~1.1 m/s (4.0 km/h)
                base_travel_time = max(1.0, route_distance / 1.1)
            else:
                # Pilgrimage driving speed (congested temple approach streets average 20-22 km/h ~ 6.0 m/s)
                base_travel_time = max(route["duration_seconds"], route_distance / 6.0)
        else:
            route_distance = cached_route["distance_meters"]
            if travel_mode.lower() == "walking":
                base_travel_time = max(1.0, route_distance / 1.1)
            else:
                base_travel_time = max(cached_route["duration_seconds"], route_distance / 6.0)
            route_updated = False

        # Estimate remaining distance based on how far the user has traveled
        if session and not needs_recalculation:
            total_distance = session.get("route_distance_meters", route_distance)
            distance_moved = self.session_manager.distance_from_origin(session, current_lat, current_lng)
            remaining_distance = max(0.0, total_distance - distance_moved)
        else:
            remaining_distance = route_distance

        # --- XGBoost ML Prediction Pipeline ---
        predicted_travel_time = base_travel_time
        predicted_queue_time = 0.0
        ml_model_used = False

        if self.ml_predictor:
            hour_of_day = now.hour
            day_of_week = now.weekday()

            predicted_travel_time, travel_ml_used = self.ml_predictor.predict_travel_time(
                distance_meters=route_distance,
                base_duration_seconds=base_travel_time,
                hour_of_day=hour_of_day,
                day_of_week=day_of_week,
                crowd_density_index=crowd_density_index,
                is_festival=is_festival,
                weather_severity=weather_severity,
                traffic_density=traffic_density,
                road_closure=road_closure,
                accident_reported=accident_reported,
                holiday=holiday,
            )

            if include_queue_time:
                # Estimate arrival hour at destination
                arrival_hour = (now + timedelta(seconds=predicted_travel_time)).hour
                predicted_queue_time, queue_ml_used = self.ml_predictor.predict_queue_time(
                    arrival_hour=arrival_hour,
                    day_of_week=day_of_week,
                    crowd_density_index=crowd_density_index,
                    is_festival=is_festival,
                    weather_severity=weather_severity,
                    traffic_density=traffic_density,
                    holiday=holiday,
                )
            else:
                queue_ml_used = False

            ml_model_used = travel_ml_used or queue_ml_used

        # Component breakdown calculation
        parking_time = 480.0 * (1.0 + crowd_density_index * 0.5) if travel_mode.lower() == "driving" else 0.0
        walking_time = 720.0 * (1.0 + crowd_density_index * 0.3)
        security_check_time = 300.0 * (2.0 if is_festival else 1.0)
        weather_delay_time = predicted_travel_time * (weather_severity * 0.2)
        festival_delay_time = predicted_travel_time * (0.25 if is_festival else 0.0)

        breakdown = {
            "driving_time_seconds": round(predicted_travel_time, 1),
            "parking_time_seconds": round(parking_time, 1),
            "walking_time_seconds": round(walking_time, 1),
            "queue_time_seconds": round(predicted_queue_time, 1),
            "security_check_seconds": round(security_check_time, 1),
            "weather_delay_seconds": round(weather_delay_time, 1),
            "festival_delay_seconds": round(festival_delay_time, 1),
            "total_seconds": round(predicted_travel_time + predicted_queue_time + parking_time + walking_time + security_check_time, 1),
        }

        total_travel_time = round(predicted_travel_time + predicted_queue_time, 1)
        traffic_delay_factor = round(predicted_travel_time / max(1.0, base_travel_time), 2)

        # Calculate final ETA timestamp
        eta_time = now + timedelta(seconds=total_travel_time)

        return {
            "route_distance_meters": route_distance,
            "base_travel_time_seconds": round(base_travel_time, 1),
            "predicted_travel_time_seconds": round(predicted_travel_time, 1),
            "predicted_queue_time_seconds": round(predicted_queue_time, 1),
            "travel_time_seconds": total_travel_time,
            "traffic_delay_factor": traffic_delay_factor,
            "remaining_distance_meters": round(remaining_distance, 1),
            "eta": eta_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "route_updated": route_updated,
            "ml_model_used": ml_model_used,
            "breakdown": breakdown,
        }


