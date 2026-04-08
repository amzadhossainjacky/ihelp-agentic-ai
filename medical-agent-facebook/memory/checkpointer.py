import os
import asyncpg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv
load_dotenv()

_checkpointer = None  # module-level singleton


async def get_checkpointer() -> AsyncPostgresSaver:
    """
    Returns a Postgres checkpointer (creates tables on first run).
    This is what gives every conversation persistent memory.
    LangGraph stores the full ConversationState after every turn.
    The thread_id (set per user) determines which state is loaded.
    """
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    conn = await asyncpg.connect(os.getenv("DB_URI"))
    _checkpointer = AsyncPostgresSaver(conn)
    # Creates langgraph_checkpoints table in your DB automatically
    await _checkpointer.setup()
    return _checkpointer