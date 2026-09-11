from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import images, watersheds, interventions, analysis, change, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Watershed Intelligence API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(images.router)
app.include_router(watersheds.router)
app.include_router(interventions.router)
app.include_router(analysis.router)
app.include_router(change.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return {"message": "Watershed Intelligence API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
