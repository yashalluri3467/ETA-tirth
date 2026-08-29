import pytest

from app.utils.coordinate_validator import (
    validate_lat,
    validate_lng,
    validate_coordinates,
    haversine_distance_meters,
    is_same_location,
)


class TestValidateLat:
    def test_valid_latitude(self):
        assert validate_lat(0.0) == 0.0
        assert validate_lat(90.0) == 90.0
        assert validate_lat(-90.0) == -90.0
        assert validate_lat(45.5) == 45.5

    def test_invalid_latitude_too_high(self):
        with pytest.raises(ValueError):
            validate_lat(91.0)

    def test_invalid_latitude_too_low(self):
        with pytest.raises(ValueError):
            validate_lat(-91.0)

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            validate_lat("not_a_number")  # type: ignore[arg-type]


class TestValidateLng:
    def test_valid_longitude(self):
        assert validate_lng(0.0) == 0.0
        assert validate_lng(180.0) == 180.0
        assert validate_lng(-180.0) == -180.0
        assert validate_lng(73.7898) == 73.7898

    def test_invalid_longitude_too_high(self):
        with pytest.raises(ValueError):
            validate_lng(181.0)

    def test_invalid_longitude_too_low(self):
        with pytest.raises(ValueError):
            validate_lng(-181.0)


class TestValidateCoordinates:
    def test_valid_coordinates(self):
        lat, lng = validate_coordinates(19.9975, 73.7898)
        assert lat == 19.9975
        assert lng == 73.7898

    def test_invalid_latitude_raises(self):
        with pytest.raises(ValueError):
            validate_coordinates(95.0, 73.0)


class TestHaversineDistance:
    def test_same_point_zero_distance(self):
        assert haversine_distance_meters(0, 0, 0, 0) == 0.0

    def test_known_distance_approx(self):
        # Mumbai to Pune is roughly 150 km
        dist = haversine_distance_meters(19.9975, 73.7898, 19.9956, 73.7810)
        assert 500 < dist < 5000  # Rough check for ~7 km

    def test_antipodal_points(self):
        # Distance from equator to equator on opposite side
        dist = haversine_distance_meters(0, 0, 0, 180)
        assert abs(dist - 20_037_500) < 100_000  # Half Earth circumference


class TestIsSameLocation:
    def test_identical_points(self):
        assert is_same_location(0, 0, 0, 0)

    def test_nearby_points(self):
        assert is_same_location(0, 0, 0.00001, 0.00001, threshold_meters=2)

    def test_far_apart(self):
        assert not is_same_location(0, 0, 10, 10)

    def test_custom_threshold(self):
        assert is_same_location(0, 0, 0.001, 0.001, threshold_meters=200)
