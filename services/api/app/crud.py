from typing import List
from datetime import datetime
import asyncpg
import json
import logging

from models import PVReading
from db import get_db_pool


log = logging.getLogger("crud")


async def insert_readings_batch(readings: List[PVReading]):
    """
    Asynchronously inserts a batch of PV readings into the database.
    This function processes a list of PV readings, performs validation and data type conversion,
    and inserts the valid records into the 'pv_readings' table using the PostgreSQL COPY protocol
    for efficient batch insertion.
    Args:
        readings (List[PVReading]): A list of PVReading objects to be inserted into the database.
                                   Each object contains device information, measurements, status,
                                   location, and metadata.
    Returns:
        None
    Raises:
        asyncpg.exceptions.PostgresError: If the database insertion operation fails.
    Notes:
        - The function handles timestamp conversion from ISO format strings to datetime objects
        - Invalid records (those causing exceptions during processing) are logged and skipped
        - Empty input lists or situations where all records are invalid are handled gracefully
        - Metadata is serialized to JSON before storage
    """
    if not readings:
        return

    pool = await get_db_pool()
    records = []

    for r in readings:
        try:
            if isinstance(r.timestamp, str):
                timestamp_dt = datetime.fromisoformat(r.timestamp.replace('Z', '+00:00'))
            else:
                timestamp_dt = r.timestamp

            fault_code = r.status.fault_code
            if isinstance(fault_code, str):
                fault_code = int(fault_code) if fault_code.isdigit() else None

            records.append(
                (
                    timestamp_dt,
                    timestamp_dt,
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