import asyncio, time, logging
from collections import deque
from typing import List
from models import PVReading
from crud import insert_readings_batch

log = logging.getLogger("batch")
batch_queue = deque()
BATCH_SIZE = 1000
FLUSH_INTERVAL = 0.02  # 10ms

async def batch_worker():
    while True:
        cycle_start = time.time()
        batch: List[PVReading] = []
        while len(batch) < BATCH_SIZE and batch_queue:
            batch.append(batch_queue.popleft())

        if batch:
            db_start = time.time()
            try:
                await insert_readings_batch(batch)
            except Exception as e:
                log.exception("insert batch failed")
            db_dur = time.time() - db_start
            log.info("Inserted %d rows in %.3fs (cycle total %.3fs)",
                     len(batch), db_dur, time.time() - cycle_start)
        else:
            await asyncio.sleep(FLUSH_INTERVAL)
