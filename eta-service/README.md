# TirthTrack ETA Engine

A FastAPI-based route-based ETA microservice for the TirthTrack platform.

The service accepts GPS coordinates from an Android application (every 10 seconds) and returns
road-network-based Estimated Time of Arrival using OSRM, GraphHopper, or Google Routes API.

## Architecture

```
Android App (GPS every 10s)
        │
        ▼
POST /api/v1/eta
        │
        ▼
FastAPI ETA Engine
        │
        ├── Request Validation (Pydantic)
        ├── Session Manager (tracks pilgrim sessions)
        ├── Route Service (orchestrates routing providers)
        ├── ETA Calculator (with optimization/debounce)
        ├── Cache Service (Redis)
        └── JSON Response
        │
        ▼
OSRM / GraphHopper / Google Routes API
```

## Optimization Strategy

Although the Android app sends location updates every 10 seconds, the service only recalculates
the route when:

- The user moves more than **25 meters**
- The user deviates from the planned route by more than **50 meters**
- The destination changes
- A fixed refresh interval (**45 seconds**) has elapsed

For intermediate updates, the remaining ETA is estimated from the previously calculated route.

## Setup

```bash
cd eta-service
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your routing engine URLs and API keys
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OSRM_BASE_URL` | No | `http://localhost:5000` | OSRM server URL |
| `GRAPHHOPPER_BASE_URL` | No | — | GraphHopper server URL |
| `GRAPHHOPPER_API_KEY` | No | — | GraphHopper API key |
| `GOOGLE_ROUTES_API_KEY` | No | — | Google Routes API key |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection URL |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |

## API

### POST /api/v1/eta

Request body:

```json
{
  "device_id": "pilgrim_001",
  "timestamp": "2026-08-05T09:15:00Z",
  "current_location": {
    "lat": 19.9975,
    "lng": 73.7898
  },
  "destination": {
    "lat": 19.9956,
    "lng": 73.7810
  }
}
```

Response:

```json
{
  "status": "success",
  "device_id": "pilgrim_001",
  "route_distance_meters": 2845,
  "travel_time_seconds": 510,
  "remaining_distance_meters": 2845,
  "eta": "2026-08-05T09:23:30Z",
  "route_updated": true
}
```

## Testing

```bash
pytest tests/ -v
```

## Deployment

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
