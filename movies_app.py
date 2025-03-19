import psycopg
import os

def main(cursor, connection):
    global curs, conn
    curs = cursor
    conn = connection
    user_session = {
        "loggedIn": False,
        "userId": None,
        "userIndex": [],
        "followers": 0,
        "following": 0,
        "collections": 0
    }
    
    while True:
        while not user_session["loggedIn"]:
            command = input("Would you like to login or create an account?\n")
            if command == "create account":
                create_account()
                user_session["loggedIn"] = True
            if command == "login":
                login()
                user_session["loggedIn"] = True
            else:
                print("login - log into an account")
                print("create account - create an account")
            
            while user_session["loggedIn"]:
                command = input("Enter a command:\n")
                #if commen
def create_account():
    curs.execute 
    
def login():
    pass