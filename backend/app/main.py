
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="SitePulse AI",
    description=(
        "AI-powered multi-site risk prioritisation "
        "and intervention briefing prototype."
    ),
    version="0.1.0",
)

# Allow the local React development server to communicate
# with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "SitePulse AI",
    }


app.include_router(
    router,
    prefix="/api/v1",
    tags=["SitePulse API"],
)
