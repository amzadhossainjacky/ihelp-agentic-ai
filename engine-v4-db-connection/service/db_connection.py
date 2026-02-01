import os
from configuration.postgress_config import get_postgres_db_config
import psycopg2

# get db connection
def get_db_connection():
    db_config = get_postgres_db_config()

    #  get db values
    host = db_config["host"]
    port = db_config["port"]
    database = db_config["database"]
    user = db_config["user"]
    password = db_config["password"]

    # all_db_config = f"host={host} port={port} dbname={database} user={user} password={password}"

    try:
        # create a connection to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print("Connection to the database established successfully.")

        cursor = conn.cursor()

        
        print("Cursor created successfully.")

        return conn, cursor

    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")
    

    
# close db connection
def close_db_connection(conn, cursor):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed.")
    except Exception as e:
        print(f"An error occurred while closing the database connection: {e}")


    