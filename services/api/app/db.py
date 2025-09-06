import asyncpg
from fastapi import FastAPI

pool = None

async def connect_db(app: FastAPI):
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
