import requests
from typing import Optional

from app.utils.coordinate_validator import validate_coordinates


class GoogleRoutesRoute:
    def __init__(
        self,
        distance_meters: float,
        duration_seconds: float,
        geometry: list[dict],
    ):
        self.distance_meters = distance_meters
        self.duration_seconds = duration_seconds
        self.geometry = geometry


class GoogleRoutesProvider:
    """Google Routes API provider (optional, requires API key)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.timeout = 10
        self.base_url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: list[tuple[float, float]] | None = None,
    ) -> GoogleRoutesRoute:
        """Request a driving route from Google Routes API."""
        origin_lat, origin_lng = validate_coordinates(origin_lat, origin_lng)
        dest_lat, dest_lng = validate_coordinates(dest_lat, dest_lng)

        origin = {"location": {"latLng": {"latitude": origin_lat, "longitude": origin_lng}}}
        destination = {"location": {"latLng": {"latitude": dest_lat, "longitude": dest_lng}}}

        waypoint_locations = []
        if waypoints:
            for lat, lng in waypoints:
                lat, lng = validate_coordinates(lat, lng)
                waypoint_locations.append(
                    {"location": {"latLng": {"latitude": lat, "longitude": lng}}}
                )

        body: dict[str, object] = {
            "origin": origin,
            "destination": destination,
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
        }

        if waypoint_locations:
            body["intermediates"] = waypoint_locations

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.legs.steps.path",
        }

        response = self.session.post(self.base_url, json=body, headers=headers, timeout=3.0)
        response.raise_for_status()
        data = response.json()

        routes = data.get("routes", [])
        if not routes:
            raise RuntimeError("Google Routes API returned no route")

        route = routes[0]
        distance = route.get("distanceMeters", 0)
        duration = float(route.get("duration", "0s").rstrip("s"))

        # Extract geometry from legs/steps
        geometry_list: list[dict] = []
        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                path = step.get("path", [])
                for point in path:
                    geometry_list.append(
                        {"lat": point["latLng"]["latitude"], "lng": point["latLng"]["longitude"]}
                    )

        return GoogleRoutesRoute(
            distance_meters=distance,
            duration_seconds=duration,
            geometry=geometry_list,
        )
