from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host="localhost",
    port="3200",
    database="test_db",
    user="postgres",
    password="root"
)

import service

conn = None

try:
    # 1️⃣ get connection from pool
    conn = db_pool.getconn()
    print("Database connection acquired from pool.")

    # 2️⃣ create cursor
    cursor = conn.cursor()

    # 3️⃣ call service functions
    # service.create_table(cursor, conn)
    # service.insert_table(cursor, conn)
    service.fetch_data(cursor, conn)
    # service.update_data(cursor, conn)

    # 4️⃣ commit ONLY if data is modified
    # conn.commit()

except Exception as e:
    if conn:
        conn.rollback()
    print(f"An error occurred: {e}")

finally:
    if cursor:
        cursor.close()
        print("Database cursor closed.")

    if conn:
        # 5️⃣ return connection to pool (NOT close)
        db_pool.putconn(conn)
        print("Database connection returned to pool.")
