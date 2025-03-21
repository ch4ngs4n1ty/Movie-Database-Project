import psycopg
import os
import datetime

def main(cursor, connection):
    global curs, conn
    curs = cursor
    conn = connection
    user_session = {
        "loggedIn": False,
        "userid": None,
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
                if command == "logout":
                    user_session["logged_in"] = False
                    user_session["userid"] = ""
                    user_session["userIndex"] = []
                    user_session["followers"] = 0
                    user_session["following"] = 0
                    user_session["collections"] = 0
                    print("Logged out")
                elif command == "follow":
                    follow()
                elif command == "unfollow":
                    unfollow()
                elif command == "watch movie":
                    watch_movie()
                elif command == "watch collection":
                    watch_collection()
                elif command == "rate":
                    rate_movie()
                elif command == "search":
                    search()
                elif command == "add":
                    add_to_collection()
                elif command == "remove":
                    remove_from_collection()
                elif command == "delete":
                    delete_collection()
                elif command == "view collections":
                    view_collections()
                elif command == "create_collection":
                    create_collection()
                elif command == "name_collection":
                    name_collection()
                else:
                    print("Invalid command")
                    help()
                    

def create_account():
    curs.execute("SELECT MAX(userid) FROM users")
    uid = curs.fetchone()[0] + 1
    username = input("Username: ")
    password = input("Password: ")
    firstname = input("First Name: ")
    lastname = input("Last Name: ")
    email = input("Email address: ")
    creation_date = datetime.datetime.now()
    try:
        curs.execute("INSERT INTO users(userid, username, firstname, lastname, region, dob, password, creationdate) VALUES (%s, %s, %s, %s, %s,%s, %s)", (uid, email, username, password, firstname, lastname, password, creation_date))
        print("Account has been created \n")
        login()
    except Exception as e:
        print("Error occurred", e)
        conn.rollback()

def login():

    username = input("Username: ")
    password = input("Password: ")

    #selects only userid, username, and password 
    curs.execute("SELECT userid, username, password FROM users WHERE username = %s", (username,)) 

    #search for user with the provided username
    #user = (userid, username, password)
    user = curs.fetchone() 

    #checks if user exists and user's password equals to inputted password
    if user and user[2] == password: 

        access_date = datetime.datetime.now()

        #relational table is AccessDate(UserID, AccessDate)
        curs.execute("IN users SET AccessDate(userid, accessdate) VALUES (%s, %s)" , (user[0], access_date))

        conn.commit()

        print(f"Hello, {username}!")

    else: 

        print("Invalid username or password!")

def follow():
    pass

def unfollow():
    pass

def watch_movie():
    pass

def watch_collection():
    pass

def rate_movie():
    pass

def search():
    pass

def add_to_collection():
    pass

def remove_from_collection():
    pass

def delete_collection():
    pass

def view_collections():

    user_id = user_session["userid"]

    if not user_id:
        
        print("Need to be logged in to view collection")
        return

    curs.execute("""SELECT c.collectionname, 
                 COUNT(m.movieid) AS num_movies,
                 TO_CHAR(MAKE_INTERVAL(mins => SUM(duration)), 'HH24:MI') AS total_length
                 FROM collection c
                 LEFT JOIN movie m ON c.movieid = m.movieid
                 WHERE c.userid = %s
                 GROUP BY c.collectionname
                 ORDER BY c.collectionname ASC""", (user_id,))
                
    list_collections = conn.fetchall()

    for collect in list_collections:

        name = collect[0]
        num_movies = collect[1]
        total_length = collect[2]

        print("Collection Name: " + name + "Number Of Movies: " + num_movies + "Total Length Of Movies In Collection: " + total_length)

#user will be able to create collection of movies
def create_collection():

    #checks if the user is logged in
    user_id = user_session["userid"]

    if not user_id:
        
        print("Need to be logged in to create a new collection")
        return

    new_collection = input("Input the name of your new collection: ")
    collection_name = new_collection.strip()

    try:
        
        #relational table is Collection(CollectionName, UserID)
        curs.execute("INSERT INTO Collection(collectionname, userid) VALUES (%s, %s)", (collection_name, user_id))

        conn.commit()

        print(f"Collection '{collection_name}' has been created!")

    except Exception as e:

        print("Error occured when attempting to create collection:", e)
        conn.rollback()

def name_collection():
    pass

