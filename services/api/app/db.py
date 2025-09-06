import asyncpg
from fastapi import FastAPI

pool = None

async def connect_db(app: FastAPI):
    """
    Asynchronously establishes a connection pool to the PostgreSQL database.

    This function creates a global connection pool that can be used throughout the application
    for database operations. It configures the pool with specific settings for the IoT PV application.

    Parameters:
        app (FastAPI): The FastAPI application instance.

    Returns:
        None: The function sets the global 'pool' variable and doesn't return a value.

    Note:
        - The function connects to a PostgreSQL database named 'iot_pv'
        - It creates a connection pool with min_size=10 and max_size=1000
        - JIT is disabled in server settings for consistent performance
    """
    global pool
    pool = await asyncpg.create_pool(
        user='postgres', 
        password='postgres',
        database='iot_pv',
        host='postgres',
        port=5432,
        min_size=10,
        max_size=1000,
        server_settings={
                'jit': 'off' 
        }
    )

async def close_db(app: FastAPI):
    await pool.close()

async def get_db_pool():
    if pool is None:
        await connect_db()
    return pool
