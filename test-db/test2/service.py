import time

def fetch_data(cursor):
    cursor.execute("SELECT id, name FROM COMPANY")
    rows = cursor.fetchall()
    for row in rows:
        print("ID =", row[0])
        print("NAME =", row[1], "\n")
