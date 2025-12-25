from fastapi import FastAPI
from api.routes import router as api_router
from api.websocket import ws_router
from database.mongo import init_collections

app = FastAPI(title="Real-Time Sentiment Platform")

@app.on_event("startup")
def startup():
    init_collections()

@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)
app.include_router(ws_router)