import json
import time
from typing import Any, Optional

from app.utils.coordinate_validator import haversine_distance_meters


class CacheService:
    """Redis-backed cache for route results and session state."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis_url = redis_url
        self._client: Any | None = None

    def _get_client(self):
        if self._client is None:
            try:
                import redis as redis_lib

                self._client = redis_lib.from_url(self._redis_url, decode_responses=True)
                self._client.ping()
            except ImportError:
                raise RuntimeError(
                    "redis package is required for CacheService. Install with: pip install redis"
                )
            except Exception as e:
                raise RuntimeError(f"Could not connect to Redis at {self._redis_url}: {e}")
        return self._client

    def get_route_key(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> str:
        """Generate a cache key for a route between two coordinates."""
        # Round to 4 decimal places (~11 meters) to group nearby requests
        key = f"route:{origin_lat:.4f}:{origin_lng:.4f}:{dest_lat:.4f}:{dest_lng:.4f}"
        return key

    def get_cached_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> Optional[dict]:
        """Retrieve a cached route if available."""
        try:
            client = self._get_client()
            key = self.get_route_key(origin_lat, origin_lng, dest_lat, dest_lng)
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def cache_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        route_data: dict,
        ttl_seconds: int = 300,
    ) -> None:
        """Cache a route result with a TTL."""
        try:
            client = self._get_client()
            key = self.get_route_key(origin_lat, origin_lng, dest_lat, dest_lng)
            client.setex(key, ttl_seconds, json.dumps(route_data))
        except Exception:
            pass  # Cache failures should not break the request

    def get_session(self, device_id: str) -> Optional[dict]:
        """Retrieve session state for a device."""
        try:
            client = self._get_client()
            key = f"session:{device_id}"
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def save_session(self, device_id: str, session_data: dict, ttl_seconds: int = 3600) -> None:
        """Save session state for a device."""
        try:
            client = self._get_client()
            key = f"session:{device_id}"
            client.setex(key, ttl_seconds, json.dumps(session_data))
        except Exception:
            pass

    def invalidate_session(self, device_id: str) -> None:
        """Remove session state for a device."""
        try:
            client = self._get_client()
            client.delete(f"session:{device_id}")
        except Exception:
            pass
