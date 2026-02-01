from service.db_connection import get_db_connection, close_db_connection
from service.stage import fetch_stage

# get db connection
conn, cursor = get_db_connection()


# execute a query
fetch_stage(cursor, conn)

# close db connection
close_db_connection(conn, cursor)