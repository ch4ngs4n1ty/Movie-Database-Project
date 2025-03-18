import psycopg2
from sshtunnel import SSHTunnelForwarder
import json

import application

def main():
    
    with open('personal_information.json', 'r') as file:
        data = json.load(file)

    username = data['username']
    password = data['password']
    dbName = "p320_13"



        

    if True:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username,
                                ssh_password=password,
                                remote_bind_address=('127.0.0.1', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': username,
                'password': password,
                'host': 'localhost',
                'port': server.local_bind_port
            }


            conn = psycopg2.connect(**params)
            curs = conn.cursor()
            print("Database connection established")
            print("Starting application...")
            application.main(curs, conn)
            print("Application finished")
            conn.close()        
            print("Database connection closed")

if __name__ == "__main__":
    main()

