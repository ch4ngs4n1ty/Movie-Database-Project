'''
connection.py

This script establishes a connection to the database and calls functions from
other files to update the database if needed or to run an application.
'''
import os
import psycopg
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

import movies_app as movies_app

load_dotenv()

username = os.getenv("RIT_USERNAME")
password = os.getenv("RIT_PASSWORD")
dbName = 'p32001_23'

try:
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            remote_bind_address=('127.0.0.1', 5432)) as server: 
        server.start()  # type: ignore
        print("SSH tunnel established")
        params = {
            'dbname': dbName,
            'user': username,
            'password': password,
            'host': 'localhost',
            'port': server.local_bind_port  # type: ignore
        }

        conn = psycopg.connect(**params)
        curs = conn.cursor()
        print("Database connection established")

        #DB work here....
        movies_app.main(curs, conn)

        conn.close()
        print("Database connection closed.")

except Exception as e:
    print(f"Connection failed: {e}")

#except:
#    print("Connection failed")
