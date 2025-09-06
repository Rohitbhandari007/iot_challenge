import asyncio
from contextlib import asynccontextmanager
import asyncpg
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import PVReading
from utils import batch_worker, batch_queue
from crud import get_readings
from db import connect_db, close_db, get_db_pool 

BATCH_QUEUE_MAX = 5000  

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db(app)
    task = asyncio.create_task(batch_worker())
    yield 
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await close_db(app)

app = FastAPI(
    title="IoT PV Data Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/submit")
async def submit_reading(payload: PVReading):
    if len(batch_queue) >= BATCH_QUEUE_MAX:
        raise HTTPException(status_code=503, detail="Queue full, try again later")
    batch_queue.append(payload)
    return {"status": "queued"}

@app.get("/")
async def list_events(
    device_id: str = None,
    limit: int = 100,

    pool: asyncpg.Pool = Depends(get_db_pool)
):
    return await get_readings(pool=pool, device_id=device_id, limit=limit)

@app.get("/api/events")
async def list_events(
    device_id: str = None,
    limit: int = 100,

    pool: asyncpg.Pool = Depends(get_db_pool)
):
    return await get_readings(pool=pool, device_id=device_id, limit=limit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
    )
