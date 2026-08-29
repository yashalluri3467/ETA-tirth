# Deployment Guide & Online API Documentation — TirthTrack ETA Service

This document provides step-by-step instructions for running the TirthTrack ETA engine locally, making API requests, and deploying it online to Vercel, Render, Railway, AWS, or Docker containers.

---

## 1. Running Locally

### Backend Server (FastAPI Engine)
```bash
# Navigate to the service folder
cd eta-service

# Install dependencies
pip install -r requirements.txt

# Start the dev server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.  
Interactive Swagger UI docs are at `http://localhost:8000/docs`.

### React Frontend
```bash
cd frontend
npm install
npm start
```
The web dashboard will be available at `http://localhost:3000`.

---

## 2. Docker Deployment (1-Click Containerization)

### Using Docker Compose (FastAPI + Redis Cache)
```bash
docker-compose up --build -d
```
This starts the backend on port `8000` alongside an isolated Redis 7 cache on port `6379`.

### Using Docker Image Standalone
```bash
docker build -t tirthtrack-eta-service .
docker run -p 8000:8000 tirthtrack-eta-service
```

---

## 3. Deploying Online for Public API Access

### Option A: Vercel (Serverless Deployment — Recommended)
1. Install the Vercel CLI or connect your GitHub repository to [Vercel](https://vercel.com).
2. The project contains pre-configured `vercel.json` and `api/index.py` files.
3. Deploy directly via CLI:
   ```bash
   vercel --prod
   ```
4. Your API will be available online at `https://<your-project>.vercel.app/api/v1/eta`.

### Option B: Render / Railway / Koyeb / Fly.io
1. Create a new Web Service pointing to your GitHub repository.
2. Select **Python 3** or **Docker**.
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Render/Railway will provide an HTTPS public URL (e.g. `https://tirthtrack-eta.onrender.com`).

---

## 4. API Endpoints & Request Examples

### A. Health Check
- **Endpoint:** `GET /health`
- **cURL Request:**
  ```bash
  curl -s http://localhost:8000/health
  ```
- **Response:**
  ```json
  {
    "status": "ok",
    "service": "eta-engine"
  }
  ```

---

### B. Compute Pilgrimage ETA (`/api/v1/eta`)
- **Endpoint:** `POST /api/v1/eta`
- **Headers:** `Content-Type: application/json`
- **Request Payload:**
  ```json
  {
    "device_id": "pilgrim_001",
    "timestamp": "2026-08-29T09:15:00Z",
    "current_location": {
      "lat": 19.9975,
      "lng": 73.7898
    },
    "destination": {
      "lat": 19.9956,
      "lng": 73.7810
    },
    "crowd_density_index": 0.6,
    "is_festival": true,
    "weather_severity": 0.2,
    "include_queue_time": true
  }
  ```

- **cURL Command:**
  ```bash
  curl -X POST http://localhost:8000/api/v1/eta \
    -H "Content-Type: application/json" \
    -d '{
      "device_id": "pilgrim_001",
      "timestamp": "2026-08-29T09:15:00Z",
      "current_location": {"lat": 19.9975, "lng": 73.7898},
      "destination": {"lat": 19.9956, "lng": 73.7810},
      "crowd_density_index": 0.6,
      "is_festival": true
    }'
  ```

- **Response:**
  ```json
  {
    "status": "success",
    "device_id": "pilgrim_001",
    "route_distance_meters": 1706.3,
    "travel_time_seconds": 671.0,
    "base_travel_time_seconds": 122.2,
    "predicted_travel_time_seconds": 433.3,
    "predicted_queue_time_seconds": 237.7,
    "traffic_delay_factor": 3.55,
    "remaining_distance_meters": 1706.3,
    "eta": "2026-08-29T09:35:00Z",
    "route_updated": true,
    "ml_model_used": true
  }
  ```

---

### C. AI Pilgrimage Assistant (`/api/v1/chat`)
- **Endpoint:** `POST /api/v1/chat`
- **Request Payload:**
  ```json
  {
    "device_id": "pilgrim_001",
    "message": "How long is the darshan queue wait time?",
    "crowd_density_index": 0.8,
    "is_festival": true
  }
  ```

- **Response:**
  ```json
  {
    "status": "success",
    "device_id": "pilgrim_001",
    "reply": "The estimated darshan queue waiting time right now is approximately 4.3 minutes. Note: Festival peak crowd active. Expect longer screening lines at Gate 1.",
    "intent": "queue_inquiry",
    "recommendations": {
      "suggested_gate": "Gate 2 (East Entry)"
    },
    "eta_summary": null
  }
  ```
