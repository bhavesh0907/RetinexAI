from fastapi import FastAPI
from contextlib import asynccontextmanager

# ✅ CORS
from fastapi.middleware.cors import CORSMiddleware

# ✅ STATIC FILES (🔥 REQUIRED FOR IMAGE PREVIEW)
from fastapi.staticfiles import StaticFiles

# Routers
from app.api import auth, screening, history, dashboard
from app.api import admin, health, model

# DB
from app.core.database import Base, engine

# ✅ MODELS
from app.models import User, Screening, History


# ======================================================
# LIFECYCLE
# ======================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting RetinexAI Backend...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
    yield
    print("🛑 Shutting down RetinexAI Backend...")


# ======================================================
# INIT
# ======================================================
app = FastAPI(
    title="RetinexAI Backend",
    description="AI-powered Retinal Disease Screening System",
    version="1.0.0",
    lifespan=lifespan,
)

# ======================================================
# ✅ CORS
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 🔥 STATIC FILES (FIX PREVIEW ISSUE)
# ======================================================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ======================================================
# ROUTES
# ======================================================
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth")
app.include_router(screening.router, prefix=f"{API_PREFIX}/screening")
app.include_router(history.router, prefix=f"{API_PREFIX}/history")
app.include_router(dashboard.router, prefix=f"{API_PREFIX}/dashboard")

# 🔥 ADMIN ROUTES (KEEP PREFIX)
app.include_router(admin.router, prefix=f"{API_PREFIX}/admin")

app.include_router(health.router, prefix=f"{API_PREFIX}/health")
app.include_router(model.router, prefix=f"{API_PREFIX}/model")


# ======================================================
# ROOT
# ======================================================
@app.get("/")
def root():
    return {
        "success": True,
        "message": "API running"
    }