# Run Commands

## FastAPI ETA Engine (Backend)

```bash
cd eta-service

# Install dependencies
pip install -r requirements.txt

# Run the dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Compute ETA
curl -X POST http://localhost:8000/api/v1/eta \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "pilgrim_001",
    "timestamp": "2026-08-05T09:15:00Z",
    "current_location": {"lat": 19.9975, "lng": 73.7898},
    "destination": {"lat": 19.9956, "lng": 73.7810}
  }'
```

### Run Tests

```bash
cd eta-service
pytest tests/ -v
```

## React Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm start
```

The frontend will be available at `http://localhost:3000`.
