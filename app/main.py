from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.api import auth, students, risk, referrals, reports, assessments, interventions, geography, rbac, i18n

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Student Well-Being Early Warning, Intervention & Referral Support System",
    description="Decision-support tool for Malaysian school counselors. Never diagnoses, never replaces qualified counselors.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(risk.router)
app.include_router(referrals.router)
app.include_router(reports.router)
app.include_router(assessments.router)
app.include_router(interventions.router)
app.include_router(geography.router)
app.include_router(rbac.router)
app.include_router(i18n.router)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_login():
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/dashboard", include_in_schema=False)
def serve_dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/reset-password", include_in_schema=False)
def serve_reset_password():
    return FileResponse(STATIC_DIR / "reset_password.html")


@app.get("/health")
def health():
    return {"status": "ok"}
