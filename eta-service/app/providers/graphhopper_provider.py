import requests
from typing import Optional

from app.utils.coordinate_validator import validate_coordinates


class GraphHopperRoute:
    def __init__(
        self,
        distance_meters: float,
        duration_seconds: float,
        geometry: list[dict],
    ):
        self.distance_meters = distance_meters
        self.duration_seconds = duration_seconds
        self.geometry = geometry


class GraphHopperProvider:
    """GraphHopper routing engine provider (self-hosted)."""

    def __init__(
        self,
        base_url: str = "http://localhost:8989",
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.timeout = 10

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: list[tuple[float, float]] | None = None,
    ) -> GraphHopperRoute:
        """Request a driving route from GraphHopper."""
        origin_lat, origin_lng = validate_coordinates(origin_lat, origin_lng)
        dest_lat, dest_lng = validate_coordinates(dest_lat, dest_lng)

        point_str = f"{origin_lat},{origin_lng}|{dest_lat},{dest_lng}"
        url = f"{self.base_url}/route"

        params: dict[str, object] = {
            "point": point_str,
            "type": "json",
            "locale": "en",
            "vehicle": "car",
            "encoding": "json",
        }

        if waypoints:
            wp_str = "|".join(f"{lat},{lng}" for lat, lng in waypoints)
            params["point"] = f"{origin_lat},{origin_lng}|{wp_str}|{dest_lat},{dest_lng}"

        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.session.get(url, params=params, headers=headers, timeout=3.0)
        response.raise_for_status()
        data = response.json()

        if not data.get("paths"):
            raise RuntimeError("GraphHopper returned no route")

        path = data["paths"][0]
        distance = path.get("distance", 0)  # meters
        duration = path.get("time", 0) / 1000.0  # convert ms to seconds
        points = path.get("points", {}).get("coordinates", [])
        # GraphHopper returns [lat, lng] pairs
        geometry_list = [{"lat": lat, "lng": lng} for lat, lng in points]

        return GraphHopperRoute(
            distance_meters=distance,
            duration_seconds=duration,
            geometry=geometry_list,
        )
