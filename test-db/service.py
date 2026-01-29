#create a table
def create_table(cursor, conn):
    cursor.execute('''CREATE TABLE COMPANY
      (ID INT PRIMARY KEY     NOT NULL,
      NAME           TEXT    NOT NULL,
      AGE            INT     NOT NULL);''')
    print("Table created successfully")

    conn.commit()

#insert a table
def insert_table(cursor, conn):
    cursor.execute("INSERT INTO COMPANY (ID,NAME,AGE) \
      VALUES (1, 'Paul', 32)")

    cursor.execute("INSERT INTO COMPANY (ID,NAME,AGE) \
        VALUES (2, 'Allen', 25)")


    print("Records created successfully")

    conn.commit()

# fetch data from table
def fetch_data(cursor, conn):
    cursor.execute("SELECT id, name from COMPANY")
    rows = cursor.fetchall()

    for row in rows:
        print("ID = ", row[0])
        print("NAME = ", row[1], "\n")

    print("Operation done successfully")

def update_data(cursor, conn):
    cursor.execute("UPDATE COMPANY set name = 'Jacky' where ID=1")  
    conn.commit()
    print("Total number of rows updated :", cursor.rowcount)

    cursor.execute("SELECT id, name from COMPANY")
    rows = cursor.fetchall()

    for row in rows:
        print("ID = ", row[0])
        print("NAME = ", row[1], "\n")

    print("Operation done successfully") 

