import psycopg
import os
import datetime

# 
user_session = {
    "loggedIn": False,
    "userId": None,
    "userIndex": [],
    "followers": 0,
    "following": 0,
    "collections": 0
    }

def main(cursor, connection):
    global curs, conn
    curs = cursor
    conn = connection
    
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
    try:
        curs.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(userId, 2) as INTEGER)), 0) + 1 FROM users")
        new_id = curs.fetchone()[0]
        uid = f"u{new_id}"
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        firstname = input("First Name: ").strip()
        lastname = input("Last Name: ").strip()
        email = input("Email address: ").strip()
        creation_date = datetime.datetime.now()
        
        curs.execute("INSERT INTO users(userid, username, firstname, lastname, password, creationdate) VALUES (%s, %s, %s, %s, %s, %s)", (uid, username, firstname, lastname, password, creation_date))
        print("Account has been created \n")
        login()
        #conn.commit()
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
    
    print("Follow a user")
    user_email = input("Enter users email: ").strip()
    
    try:
        
        # gets userid from email table
        curs.execute("SELECT userid FROM email WHERE email = %s", user_email)
        user_id = curs.fetchone()
        
        if not user_id:
            
            print("No user with this email found")
            return
        
        followed_id = user_id[0]
        
        # gets username of the userid from users table
        curs.execute("SELECT username FROM users WHERE userid = %s", (followed_id))
        user_data = curs.fetchone()
        
        if not user_data:
            
            print("User data missing")
            return
        
        followed_username = user_data[0]
        curs.execute("INSERT INTO follows VALUES (%s, %s)", user_session["userId"], followed_id)
        #conn.commit()
        print(f"You are follwing {followed_username}")
        
    except Exception as e:
        
        print("Error following user")
        conn.rollback()

def unfollow():
    
    print("Unfollow a user")
    user_email = input("Enter users email: ").strip()
    
    try:
        
        # gets userid 
        curs.execute("SELECT userid FROM email WHERE email = %s", user_email)
        user_id = curs.fetchone()
        
        if not user_id:
            
            print("No user with this email found")
            return
        
        followed_id = user_id[0]
        
        # gets username of the userid from users table
        curs.execute("SELECT * FROM follows WHERE follower = %s AND followee = %s", (user_session["userId"], followed_id))
        user_data = curs.fetchone()
        
        if not user_data:
            
            print("User data missing")
            return
        
        followed_username = user_data[0]
        curs.execute("DELETE FROM follows WHERE follower = %s AND followee = %s", user_session["userId"], followed_id)
        #conn.commit()
        print(f"You unfollowed {followed_username}")
        
    except Exception as e:
        
        print("Error following user")
        conn.rollback()

def watch_movie():
    pass

def watch_collection():
    pass

def rate_movie():
    
    print("Rate movie")
    movie_id = int(input("Enter movie ID: "))
    rating = round(float(input("Enter rating: ")))
    curs.execute("SELECT * FROM movie WHERE movieId = %s", movie_id)
    movie = curs.fetchone()
    if movie:
        try:
            curs.execute("INSERT INTO rates VALUES (%s, %s, %s)", (user_session["userId"], movie_id, rating))
            print("Rating successful")
        except Exception as e:
            print("Error occured rating movie")
            conn.rollback

def search():
    pass

def add_to_collection():
    pass

def remove_from_collection():
    pass

def delete_collection():
    pass

def view_collections():
    pass

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

