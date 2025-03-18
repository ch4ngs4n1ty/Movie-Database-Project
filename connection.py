import psycopg
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("NAME")
password = os.getenv("PASS")
dbName = 'p32001_23'


try:
    with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                            ssh_username=username,
                            ssh_password=password,
                            ssh_pkey=None,
                            remote_bind_address=('127.0.0.1', 5432)) as server:
        server.start()
        print("SSH tunnel established")
        params = {
            'dbname': dbName,
            'user': username,
            'password': password,
            'host': 'localhost',
            'port': server.local_bind_port
        }


        conn = psycopg.connect(**params)
        curs = conn.cursor()
        print("Database connection established")

        #DB work here....

        conn.close()
        print("Database connection closed.")
except:
    print("Connection failed")
