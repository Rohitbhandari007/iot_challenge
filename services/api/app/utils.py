import asyncio, time, logging
from collections import deque
from typing import List
from models import PVReading
from crud import insert_readings_batch

log = logging.getLogger("batch")
batch_queue = deque()
BATCH_SIZE = 1000
FLUSH_INTERVAL = 0.02  

async def batch_worker():
    """
    Asynchronous worker function that processes PV readings in batches.
    This function continuously runs in a loop, collecting PV readings from the batch_queue
    until either BATCH_SIZE is reached or the queue is empty. If a batch is collected,
    it inserts the readings into the database using insert_readings_batch.
    If no readings are available, it sleeps for FLUSH_INTERVAL seconds.
    Performance metrics for database insertion time and total cycle time are logged.
    Returns:
        None: This function runs indefinitely.
    Raises:
        Exception: Any exceptions during database insertion are caught and logged,
                   allowing the worker to continue processing subsequent batches.
    """
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
