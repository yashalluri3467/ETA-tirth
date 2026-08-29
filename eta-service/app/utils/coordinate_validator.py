import math


LAT_MIN = -90.0
LAT_MAX = 90.0
LNG_MIN = -180.0
LNG_MAX = 180.0


def validate_lat(lat: float) -> float:
    if not isinstance(lat, (int, float)):
        raise ValueError(f"Latitude must be a number, got {type(lat).__name__}")
    if lat < LAT_MIN or lat > LAT_MAX:
        raise ValueError(f"Latitude {lat} out of range [{LAT_MIN}, {LAT_MAX}]")
    return float(lat)


def validate_lng(lng: float) -> float:
    if not isinstance(lng, (int, float)):
        raise ValueError(f"Longitude must be a number, got {type(lng).__name__}")
    if lng < LNG_MIN or lng > LNG_MAX:
        raise ValueError(f"Longitude {lng} out of range [{LNG_MIN}, {LNG_MAX}]")
    return float(lng)


def validate_coordinates(lat: float, lng: float) -> tuple[float, float]:
    return validate_lat(lat), validate_lng(lng)


def haversine_distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Compute the great-circle distance between two points on Earth (meters)."""
    R = 6_371_000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def is_same_location(lat1: float, lng1: float, lat2: float, lng2: float, threshold_meters: float = 1.0) -> bool:
    """Check if two coordinates are within a threshold distance of each other."""
    return haversine_distance_meters(lat1, lng1, lat2, lng2) <= threshold_meters
