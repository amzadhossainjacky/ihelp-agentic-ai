#1 install psycopg2-binary
import psycopg2
import os, sys
import service

#2 create a connection to the database

conn = None
try:
    conn = psycopg2.connect(
        host="localhost",
        port="3200",
        database="test_db",  
        user="postgres",  
        password="root"     

    )
    print("Connection to the database established successfully.")

    #3 create a cursor object
    cursor = conn.cursor()
    """ print("Cursor created successfully.")

    query = "SELECT version();"

    #4 execute a simple query
    cursor.execute(sql=query)

    db_version = cursor.fetchone()
    print(f"Database version: {db_version[0]}") """

    #5 call the create_table function from service.py
    # service.create_table(cursor, conn)

    #6 call the insert_table function from service.py
    # service.insert_table(cursor, conn)

    #7 call the fetch_data function from service.py
    service.fetch_data(cursor, conn)

    #8 call the update_data function from service.py
    #service.update_data(cursor, conn)


except Exception as e:
    print(f"An error occurred while connecting to the database: {e}")
finally:
    if cursor:
        cursor.close()
        print("Database cursor closed.")

    if conn:
        conn.close()
        print("Database connection closed.")



        
