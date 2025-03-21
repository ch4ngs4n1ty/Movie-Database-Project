import psycopg
import os
import datetime

user_session = {
    "loggedIn": False,
    "userId": None,
    "userIndex": [],
    "followers": 0,
    "following": 0,
    "collections": 0
    }
curs = None
conn = None

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
        
        # gets the next available userId from users
        curs.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(userId FROM 2) as INTEGER)), 0) + 1 FROM users")
        new_id = curs.fetchone()[0]
        uid = f"u{new_id}"
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        firstname = input("First Name: ").strip()
        lastname = input("Last Name: ").strip()
        region = input("Region: ").strip()
        dob = input("Date of birth(YYYY-MM-DD): ").strip()
        email = input("Email address: ").strip()
        creation_date = datetime.datetime.now()
        
        # adds the users account to users
        curs.execute("INSERT INTO users(userid, username, firstname, lastname, region, dob, password, creationdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                     (uid, username, firstname, lastname, region, dob, password, creation_date))
        
        # adds to email table
        curs.execute("INSERT INTO email(userid, email) VALUES(%s, %s)", (uid, email))
        
        conn.commit()
        print("Account has been created \n")
        login()
        
    except Exception as e:
        
        print("Error occurred creating account", e)
        conn.rollback()


def login():

    username = input("Username: ")
    password = input("Password: ")

    try:

        #selects only userid, username, and password 
        curs.execute("SELECT userid, username, password FROM users WHERE username = %s", (username,)) 

        #search for user with the provided username
        #user = (userid, username, password)
        user = curs.fetchone() 

        #checks if user exists and user's password equals to inputted password
        if user and user[2] == password: 

            access_date = datetime.datetime.now()

            #relational table is accessdates(userid), accessdate)
            #curs.execute("INSERT INTO accessdates(userid, accessdate) VALUES (%s, %s)", (user[0], access_date))

            curs.execute("SELECT 1 FROM accessdates WHERE userid = %s", (user[0],))

            existing_entry = curs.fetchone()

            if existing_entry:  

                curs.execute("""
                    UPDATE accessdates 
                    SET accessdate = %s 
                    WHERE userid = %s """, (access_date, user[0]))
                
                #print(f"Access date updated for {username}!")

            else:  

                curs.execute("""
                    INSERT INTO accessdates(userid, accessdate)
                    VALUES (%s, %s)""", (user[0], access_date))
                
            
            print(f"Hello, {username}!")

            conn.commit()

        else: 

            print("Invalid username or password!")

    except Exception as e:

        print(f"An error occurred: {e}")

        conn.rollback()  

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
        conn.commit()
        print(f"You are following {followed_username}")
        
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
        conn.commit()
        print(f"You unfollowed {followed_username}")
        
    except Exception as e:
        
        print("Error following user")
        conn.rollback()

def watch_movie():
    
    print("Watch a movie")
    movie_id = input("Enter Movie ID: ").strip()
    
    try:
        
        # checks if movie exists in database
        curs.execute("SELECT * FROM movie WHERE movieid = %s", movie_id)
        movie = curs.fetchone()
        
        if not movie:
            print("Movie not found")
            return
        
        watch_date = datetime.datetime.now()

        # adds an entry in watches table
        curs.execute("INSERT INTO watches(userid, movieid, datetimewatched) VALUES (%s, %s, %s)"
                     , user_session["userId"], movie_id, watch_date)
        conn.commit()
        print(f"Watched {movie}")
        
    except Exception as e:
        
        print("Error watching movie")
        conn.rollback()
        
        

def watch_collection():
    
    print("Watch a collection")
    collection_id = input("Enter Collection ID: ").strip()
    
    try:
        
        # gets movieid that are in the collection
        curs.execute("SELECT movieid FROM partof WHERE collectionid = %s", collection_id)
        movies = curs.fetchall()
        watch_date = datetime.datetime.now()
        
        # checks if there are movies in the collection
        if not movies:
            print("No movies in collection")
            return
        
        # creates a watches entry for each movie in the collection
        for movie in movies:
            
            movie_id = movie[0]
            curs.execute("INSERT INTO watches(userid, movieid, datetimewatched) VALUES (%s, %s, %s)",
                         (user_session["userId"], movie_id, watch_date))
        
    except Exception as e:
        
        print("Error watching collection")
        conn.rollback()

def rate_movie():
    
    print("Rate movie")
    movie_id = int(input("Enter movie ID: "))
    rating = round(float(input("Enter rating: ")))
    
    # gets the movie with the movieid
    curs.execute("SELECT * FROM movie WHERE movieId = %s", movie_id)
    movie = curs.fetchone()
    
    if movie:
        
        try:
            
            # adds the movie rating into rates table
            curs.execute("INSERT INTO rates VALUES (%s, %s, %s)", (user_session["userId"], movie_id, rating))
            print("Rating successful")
        
        except Exception as e:
        
            print("Error occured rating movie")
            conn.rollback

def search():

    print("Search Movies By:")
    print("1. Name")
    print("2. Release Date")
    print("3. Cast Member")
    print("4. Studio")
    print("5. Genre")

    prompt_options = {
        "1": "Title of Movie",
        "2": "Release Date In YYYY-MM-DD",
        "3": "Cast Member Name",
        "4": "Studio",
        "5": "Genre"
    }

    search_options = {
        "1": "LOWER(m.title)",   
        "2": "LOWER(ro.releasedate)",
        "3": "LOWER(CONCAT(mp.firstname, ' ', mp.lastname))",
        "4": "LOWER(m.studio)",
        "5": "LOWER(m.genre)"
    }

    search_by = input("Select (1 - 5): ").strip()

    #searched value to actually get the value user inputs
    selected_search = search_options[search_by]

    #prompt used to guide user's interaction
    selected_prompt = prompt_options[search_by] 

    search_value = input(f"Enter {selected_prompt}: ").strip()       

    val = f"%{search_value.lower()}" 

    curs.execute("""SELECT m.title, 
                    mp.firstname,
                    mp.lastname,
                    d.firstname,
                    d.lastname,
                    m.duration,
                    m.mpaarating,
                    ROUND(AVG(r.starrating), 1) AS user_rating
                    FROM Movie m
                    LEFT JOIN StarsIn si ON m.movieid = si.movieid
                    LEFT JOIN MoviePeople mp ON si.personid = mp.personid
                    LEFT JOIN Directs dir on m.movieid = dir.movieid
                    LEFT JOIN MoviePeople p on dir.personid = p.personid
                    LEFT JOIN Rates r on m.movieid = r.movieid 
                    LEFT JOIN ReleaseOn ro on m.movieid = ro.movieid
                    WHERE {selected_search} LIKE %s
                    GROUP BY m.movieid, mp.firstname, mp.lastname, d.firstname, d.lastname, m.duration, m.mpaarating
                    ORDER BY m.title ASC, ro.releasedate ASC;""", (val,)) 
    
    result_list = curs.fetchall()

    if not result_list:
        print("No results found")
        return

    for result in result_list:

        title, cast_member, director, length, mpaa_rating, user_rating, release_date = result

        print(f"Title: {title}")
        print(f"Cast: {cast_member}")
        print(f"Director: {director}")
        print(f"Length: {length}")
        print(f"MPAA Rating: {mpaa_rating}")
        print(f"User Rating: {user_rating}")
        print(f"Release Date: {release_date}")


def add_to_collection():

    print("Adding a movie to your collection")

    try:

        user_id = user_session["userId"]

        # Collection(CollectionID, CollectionName, UserID)
        curs.execute("""SELECT CollectionID, CollectionName, 
                        FROM Collection 
                        WHERE UserID = %s""" , (user_id,))
        
        collection_list = curs.fetchall()

        if not collection_list:
            
            print("You currently have no collections right now.")

            return

        print("Your Collections: ")

        for collection in collection_list:
            
            print(f"ID: {collection[0]}, Collection Name: {collection[1]}")

        collection_index = int(input("Select Collection ID: ").strip()) - 1

        if collection_index < 0 or collection_index >= len(collection_list):

            print("Invalid selection for collection")

            return
        
        collection_id = collection_list[collection_index][0]
        collection_name = collection_list[collection_index][1]

        movie_name = input("Input the Movie Name to add: ").strip()

        curs.execute("""SELECT MovieID
                        FROM Movie
                        WHERE MovieName = %s""", (movie_name,))
        
        movie = curs.fetchone()

        if not movie:

            print("Movie is not found in database")

            return
        
        movie_id = movie[0]

        # checks if movie is already in the collection
        curs.execute("""SELECT *
                        FROM PartOf 
                        WHERE CollectionID = %s AND MovieID = %s""", (collection_id, movie_id))
        
        already_exist = curs.fetchone()

        if already_exist:
            
            print(f"'{movie_name}' is already in a collection you selected")

            return
        
        curs.execute("INSERT INTO PartOf(MovieID, CollectionID) VALUES (%s, %s)" , (movie_id, collection_id))

        conn.commit()

        print(f"Successfully added '{movie_name}' to '{collection_name}")

    except Exception as e:

        print("Error adding movie to collection", e)

        conn.rollback()

def remove_from_collection():
    pass

def delete_collection():
    
    print("Deleting a collection")
    collection_id = input("Enter collection ID: ").strip()
    
    try:
        
        curs.execute("SELECT * FROM collection WHERE collectionid = %s", collection_id)
        collection = curs.fetchone()
        
        if not collection:
            print("Collection not found")
            return
        
        # delete collection from partof table
        curs.execute("DELETE FROM partof WHERE collectionid = %s", collection_id)
        
        # delete collection from collection table
        curs.execute("DELETE FROM collection WHERE collection id = %s", collection_id)
        conn.commit()
        print(f"Deleted collection {collection_id}")
    
    except Exception as e:
        
        print("Error deleting collection")
        conn.rollback()

    
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

        print("Collection Name: '{name}'  Number Of Movies: '{num_movies}' Total Length Of Movies In Collection: '{total_length}'")

#user will be able to create collection of movies
def create_collection():

    print("Creating a new collection")

    #checks if the user is logged in
    #user_id = user_session["userid"]

    new_collection = input("Input the name of your new collection: ")

    collection_name = new_collection.strip()

    user_id = user_session["userId"]

    try:
        
        curs.execute("SELECT collectionname FROM collection WHERE collectionname = %s AND userid = %s", (new_collection, user_id))

        exist_collection = curs.fetchone()

        if exist_collection:

            print(f"You already have a collection named '{new_collection}'")

            return

        #must get the current collectionid and increment it

        curs.execute("SELECT COALESCE(MAX(CAST(collectionid AS INTEGER)), 0) + 1 FROM collection")

        collection_id = curs.fetchone()[0]  # Get the next collectionid

        #relational table is Collection(CollectionName, UserID)
        curs.execute("INSERT INTO Collection(collectionid, collectionname, userid) VALUES (%s, %s, %s)", (collection_id, collection_name, user_id))

        conn.commit()

        print(f"Collection '{collection_name}' has been created!")

    except Exception as e:

        print("Error occured when attempting to create collection:", e)
        conn.rollback()

def name_collection():
    pass

