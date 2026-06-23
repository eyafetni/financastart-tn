from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes.users import router as auth_router
from routes.projects import router as projects_router

app = FastAPI(
    title="FinançaStart TN — API",
    description="Backend pour le moteur de readiness financière tunisien (بوصلتي)",
    version="1.0.0"
)

# CORS — autorise le frontend (React/Next.js) à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser la base de données au démarrage
@app.on_event("startup")
def startup():
    init_db()

# Routes
app.include_router(auth_router)
app.include_router(projects_router)

@app.get("/")
def root():
    return {
        "app": "FinançaStart TN",
        "status": "running",
        "docs": "/docs"
    }
