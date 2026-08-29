from datetime import datetime, timezone
from typing import Optional

from app.utils.coordinate_validator import haversine_distance_meters


class SessionManager:
    """Tracks active pilgrim sessions with route state."""

    def __init__(self, cache_service: Optional["CacheService"] = None):
        self._cache = cache_service

    def get_session(self, device_id: str) -> Optional[dict]:
        """Retrieve a cached session if available."""
        if self._cache:
            return self._cache.get_session(device_id)
        return None

    def create_or_update_session(
        self,
        device_id: str,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        route_distance_meters: float,
        route_geometry: list[dict],
    ) -> dict:
        """Create or update a session with the current route."""
        session = {
            "device_id": device_id,
            "origin": {"lat": origin_lat, "lng": origin_lng},
            "destination": {"lat": dest_lat, "lng": dest_lng},
            "route_distance_meters": route_distance_meters,
            "route_geometry": route_geometry,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if self._cache:
            self._cache.save_session(device_id, session)
        return session

    def clear_session(self, device_id: str) -> None:
        """Remove a session."""
        if self._cache:
            self._cache.invalidate_session(device_id)

    def has_deviated(
        self,
        session: dict,
        current_lat: float,
        current_lng: float,
        threshold_meters: float = 50.0,
    ) -> bool:
        """Check if the user has deviated from the planned route."""
        geometry = session.get("route_geometry", [])
        if not geometry:
            return False

        # Check distance to the nearest point on the route
        min_distance = float("inf")
        for point in geometry:
            dist = haversine_distance_meters(
                current_lat, current_lng,
                point["lat"], point["lng"],
            )
            if dist < min_distance:
                min_distance = dist

        return min_distance > threshold_meters

    def distance_from_origin(
        self,
        session: dict,
        current_lat: float,
        current_lng: float,
    ) -> float:
        """Calculate how far the user has moved from the origin."""
        origin = session.get("origin", {})
        return haversine_distance_meters(
            current_lat, current_lng,
            origin.get("lat", 0), origin.get("lng", 0),
        )
