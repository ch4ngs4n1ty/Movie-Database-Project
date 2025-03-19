"""
create_data.py

This script uses the Faker library to generate fake data and updates the database.
This script is a utility script used to automate the process of populating the database with fake data.
After data has been populated in the databse, this script should not be present in the connection.py file. 

Better practices can be utilized but to keep it simple this is okay I guess.

Type annotations are minimally used. It is just for clarity optional.

https://www.psycopg.org/docs/cursor.html - example for execute many
https://www.psycopg.org/docs/usage.html - example for execute
"""
from faker import Faker
from psycopg import Cursor, Connection
import random

msg1 = '✅ Running modify_database..........................[1/3]'
msg2 = '✅ Data created.....................................[2/3]'
msg3 = '✅ Update successful................................[3/3]'

def create_data(curs, conn, quantity: int) -> list[tuple[str, str]]:
    fake = Faker()

    tuples = []
    for i in range(1, quantity + 1):
        ##################### customize area #################### 
        curs.execute('SELECT firstname FROM users WHERE userid = %s', (f'u{i}',))
        a = curs.fetchone()[0]
        email = a + f'{random.randint(1,1000)}'+ random.choice(['@gmail.com', '@yahoo.com', '@outlook.com', '@hotmail.com'])
        t = (email, f'u{i}')
        #################### end of customize area ##############
        tuples.append(t)
    return tuples

def modify_database(curs: Cursor, conn: Connection) -> None:
    print(msg1)
    tuples = create_data(curs, conn, 5000)
    print(msg2)

    #change the sql statement to match the table
    sql_statement = 'INSERT INTO email (email, userid) VALUES (%s, %s)'
    try:
        curs.executemany(sql_statement, tuples)
        conn.commit()
        print(msg3)
    except Exception as e:
        conn.rollback()
        print(f'❌ Error updating database: {e}')