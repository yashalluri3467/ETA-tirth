from typing import Optional

from app.providers.osrm_provider import OsrmProvider, OsrmRoute
from app.providers.graphhopper_provider import GraphHopperProvider, GraphHopperRoute
from app.providers.google_routes_provider import GoogleRoutesProvider, GoogleRoutesRoute
from app.utils.coordinate_validator import validate_coordinates, haversine_distance_meters


class FallbackRoute:
    def __init__(self, distance_meters: float, duration_seconds: float, geometry: list[dict]):
        self.distance_meters = distance_meters
        self.duration_seconds = duration_seconds
        self.geometry = geometry


class FallbackProvider:
    """Fallback provider using Haversine calculation with average road speed (30 km/h)."""

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: Optional[list[tuple[float, float]]] = None,
    ) -> FallbackRoute:
        dist = haversine_distance_meters(origin_lat, origin_lng, dest_lat, dest_lng)
        road_distance = dist * 1.25
        duration = max(1.0, road_distance / 8.333)
        geometry = [
            {"lat": origin_lat, "lng": origin_lng},
            {"lat": dest_lat, "lng": dest_lng},
        ]
        return FallbackRoute(road_distance, duration, geometry)


class RouteService:
    """Orchestrates routing engine calls and selects the best available route."""

    def __init__(
        self,
        osrm_provider: Optional[OsrmProvider] = None,
        graphhopper_provider: Optional[GraphHopperProvider] = None,
        google_routes_provider: Optional[GoogleRoutesProvider] = None,
    ):
        self.providers: list[tuple[str, object]] = []

        if osrm_provider is not None:
            self.providers.append(("osrm", osrm_provider))
        if graphhopper_provider is not None:
            self.providers.append(("graphhopper", graphhopper_provider))
        if google_routes_provider is not None:
            self.providers.append(("google_routes", google_routes_provider))
        
        self.providers.append(("fallback", FallbackProvider()))

    def get_best_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: Optional[list[tuple[float, float]]] = None,
    ) -> dict:
        """Fetch a route from the first available provider and return structured data."""
        origin_lat, origin_lng = validate_coordinates(origin_lat, origin_lng)
        dest_lat, dest_lng = validate_coordinates(dest_lat, dest_lng)

        for name, provider in self.providers:
            try:
                route = provider.get_route(
                    origin_lat, origin_lng, dest_lat, dest_lng, waypoints
                )
                return {
                    "provider": name,
                    "distance_meters": route.distance_meters,
                    "duration_seconds": route.duration_seconds,
                    "geometry": route.geometry,
                }
            except Exception as e:
                # Try the next provider on failure
                continue

        raise RuntimeError("No routing provider could compute a route")

