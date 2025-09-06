from typing import List
from datetime import datetime
import asyncpg
import json
import logging

from models import PVReading
from db import get_db_pool


log = logging.getLogger("crud")


async def insert_readings_batch(readings: List[PVReading]):
    if not readings:
        return

    pool = await get_db_pool()
    records = []

    for r in readings:
        try:
            # Parse timestamp if it's a string
            if isinstance(r.timestamp, str):
                timestamp_dt = datetime.fromisoformat(r.timestamp.replace('Z', '+00:00'))
            else:
                timestamp_dt = r.timestamp

            # Handle fault_code conversion
            fault_code = r.status.fault_code
            if isinstance(fault_code, str):
                fault_code = int(fault_code) if fault_code.isdigit() else None

            records.append(
                (
                    timestamp_dt,      # for 'timestamp' column
                    timestamp_dt,      # for 'time' column (same value)
                    r.device_id,
                    r.location.site,
                    r.location.coordinates.lat,
                    r.location.coordinates.lon,
                    r.measurements.ac_power,
                    r.measurements.dc_voltage,
                    r.measurements.dc_current,
                    r.measurements.temperature_module,
                    r.measurements.temperature_ambient,
                    r.status.operational,
                    fault_code,
                    json.dumps(r.metadata.model_dump()),
                )
            )
        except (ValueError, TypeError, AttributeError) as e:
            log.error("Skipping invalid record for device %s: %s", r.device_id, e)

    if not records:
        log.warning("No valid records to insert after filtering.")
        return

    async with pool.acquire() as conn:
        try:
            await conn.copy_records_to_table(
                'pv_readings',
                records=records,
                columns=[
                    'timestamp', 'time', 'device_id', 'site', 'lat', 'lon',
                    'ac_power', 'dc_voltage', 'dc_current',
                    'temperature_module', 'temperature_ambient',
                    'operational', 'fault_code', 'metadata'
                ]
            )
            log.info("Successfully inserted %d records into the database.", len(records))
        except asyncpg.exceptions.PostgresError as e:
            log.exception("Database insertion failed.")
            raise


async def get_readings(pool: asyncpg.Pool, device_id: str = None, limit: int = 100):
    """
    Retrieves the most recent PV readings from the database.
    """
    async with pool.acquire() as conn:
        if device_id:
            rows = await conn.fetch("""
                SELECT * FROM pv_readings
                WHERE device_id=$1
                ORDER BY timestamp DESC
                LIMIT $2
            """, device_id, limit)
        else:
            rows = await conn.fetch("""
                SELECT * FROM pv_readings
                ORDER BY timestamp DESC
                LIMIT $1
            """, limit)
        return [dict(row) for row in rows]