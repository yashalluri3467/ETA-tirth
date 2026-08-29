import requests
from typing import Optional

from app.utils.coordinate_validator import validate_coordinates


class OsrmRoute:
    def __init__(
        self,
        distance_meters: float,
        duration_seconds: float,
        geometry: list[dict],
    ):
        self.distance_meters = distance_meters
        self.duration_seconds = duration_seconds
        self.geometry = geometry


class OsrmProvider:
    """OSRM routing engine provider (self-hosted)."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.timeout = 10

    def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        waypoints: list[tuple[float, float]] | None = None,
    ) -> OsrmRoute:
        """Request a driving route from OSRM."""
        origin_lat, origin_lng = validate_coordinates(origin_lat, origin_lng)
        dest_lat, dest_lng = validate_coordinates(dest_lat, dest_lng)

        coords = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        url = f"{self.base_url}/route/v1/driving/{coords}"

        params: dict[str, object] = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true",
        }

        if waypoints:
            wp_coords = ";".join(
                f"{lng},{lat}" for lat, lng in waypoints
            )
            params["coordinates"] = coords + ";" + wp_coords

        try:
            response = self.session.get(url, params=params, timeout=3.0)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
                try:
                    public_url = f"https://router.project-osrm.org/route/v1/driving/{coords}"
                    response = self.session.get(public_url, params=params, timeout=3.0)
                    response.raise_for_status()
                    data = response.json()
                except Exception:
                    raise e
            else:
                raise e

        if data.get("code") != "Ok" or not data.get("routes"):
            raise RuntimeError(
                f"OSRM returned no route: {data.get('code', 'unknown error')}"
            )

        route = data["routes"][0]
        geometry = route.get("geometry", {}).get("coordinates", [])
        # OSRM returns [lng, lat] pairs
        geometry_list = [{"lat": lat, "lng": lng} for lng, lat in geometry]

        return OsrmRoute(
            distance_meters=route["distance"],
            duration_seconds=route["duration"],
            geometry=geometry_list,
        )
