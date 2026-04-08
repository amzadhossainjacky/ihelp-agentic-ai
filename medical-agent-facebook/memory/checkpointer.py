import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

load_dotenv()

_checkpointer = None  # module-level singleton

async def get_checkpointer():
    """Returns a singleton AsyncPostgresSaver instance."""
    global _checkpointer
    if _checkpointer is None:
        print("Initializing AsyncPostgresSaver...")
        
        pool = AsyncConnectionPool(
            conninfo=os.getenv("DB_URI"),
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0},
            open=False  # we open it manually below
        )
        await pool.open()
        
        _checkpointer = AsyncPostgresSaver(conn=pool)
        await _checkpointer.setup()  # creates checkpointer tables if they don't exist
        
        print("AsyncPostgresSaver initialized and connected to DB.")
    return _checkpointer