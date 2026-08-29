from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.eta import router as eta_router
from app.api.chat import router as chat_router
from app.api.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    yield


app = FastAPI(
    title="TirthTrack ETA Engine",
    description="Route-based ETA microservice for the TirthTrack platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Android app and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(eta_router)
app.include_router(chat_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    """Redirect root URL to Swagger UI docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "eta-engine"}
