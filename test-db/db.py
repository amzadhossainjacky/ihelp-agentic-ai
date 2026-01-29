from psycopg2 import pool
from threading import Lock

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",
    port="3200",
    database="test_db",
    user="postgres",
    password="root"
)

_active_connections = 0
_lock = Lock()

def get_connection():
    global _active_connections
    conn = db_pool.getconn()
    with _lock:
        _active_connections += 1
    return conn

def release_connection(conn):
    global _active_connections
    db_pool.putconn(conn)
    with _lock:
        _active_connections -= 1

def pool_status():
    return {
        "active": _active_connections,
        "free": len(db_pool._pool),
        "max": db_pool.maxconn
    }
