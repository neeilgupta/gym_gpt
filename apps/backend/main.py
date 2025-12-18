from fastapi import FastAPI
from dotenv import load_dotenv
from services.db import init_db
init_db()

load_dotenv()

app = FastAPI()

# health
@app.get("/health")
def health():
    return {"status": "ok"}

# routers
from routes.plans import router as plans_router
app.include_router(plans_router)