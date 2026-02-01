# from db import get_connection, release_connection, pool_status
# import service

# conn = None

# try:
#     conn = get_connection()
#     print("Pool status:", pool_status())

#     with conn:
#         with conn.cursor() as cursor:
#             service.fetch_data(cursor)

# except Exception as e:
#     print(e)

# finally:
#     if conn:
#         release_connection(conn)
#         print("Pool status:", pool_status())


from concurrent.futures import ThreadPoolExecutor, as_completed
from db import get_connection, release_connection, pool_status
import service

TOTAL_QUERIES = 10000   # total queries you want to simulate
POOL_SIZE = 10          # must match your DB pool maxconn
BATCH_SIZE = POOL_SIZE  # threads running at a time

def run_query(query_id):
    conn = None
    try:
        conn = get_connection()
        print(f"[Query {query_id}] Pool status (acquired): {pool_status()}")

        # run your blocking psycopg2 query
        with conn:
            with conn.cursor() as cursor:
                service.fetch_data(cursor)  # your fetch_data function

    except Exception as e:
        print(f"[Query {query_id}] Error:", e)

    finally:
        if conn:
            release_connection(conn)
            print(f"[Query {query_id}] Pool status (released): {pool_status()}")


def main():
    # ThreadPool limited to pool size
    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        futures = []
        for query_id in range(TOTAL_QUERIES):
            futures.append(executor.submit(run_query, query_id))

        # Wait for all queries to finish
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("Error in thread:", e)


if __name__ == "__main__":
    main()
