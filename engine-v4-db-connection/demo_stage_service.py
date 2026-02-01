import psycopg2
from service.stage import create_table, insert_stage, fetch_stage


# create a connection to the database
conn = None
try: 
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="temp_appointment",  
        user="postgres",  
        password="12345678"     
    )
    print("Connection to the database established successfully.")

    # create a cursor object
    cursor = conn.cursor()
    print("Cursor created successfully.")

    # create stage table
    # create_table(cursor, conn)

    # insert stage data
    # insert_stage(cursor, conn)

    # fetch stage data
    fetch_stage(cursor, conn)


except Exception as e:
    print(f"An error occurred while connecting to the database: {e}")

finally:
    if cursor:
        cursor.close()
        print("Database cursor closed.")

    if conn:
        conn.close()
        print("Database connection closed.")