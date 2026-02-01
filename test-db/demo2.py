from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2
import service


TOTAL_QUERIES = 1000
BATCH_SIZE = 100  # number of concurrent requests at a time

def run_query(query_id):
    conn = None
    try:
        # create a fresh connection each time
        conn = psycopg2.connect(
        host="localhost",
        port="3200",
        database="test_db",  
        user="postgres",  
        password="root"     

    )
        
        with conn:
            with conn.cursor() as cursor:
                service.fetch_data(cursor, conn)

        print(f"[Query {query_id}] Completed")

    except Exception as e:
        print(f"[Query {query_id}] Error:", e)

    finally:
        if conn:
            conn.close()


def main():
    for batch_start in range(0, TOTAL_QUERIES, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, TOTAL_QUERIES)
        print(f"Running batch {batch_start} to {batch_end - 1}")

        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = [executor.submit(run_query, i) for i in range(batch_start, batch_end)]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print("Thread error:", e)


if __name__ == "__main__":
    main()
