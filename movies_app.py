import psycopg
import os
import datetime

user_session = {
    "loggedIn": False,
    "userId": None,
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
                
            if command == "login":
                
                login()
                
            else:
                
                print("login - log into an account")
                print("create account - create an account")
            
            while user_session["loggedIn"]:
                
                command = input("Enter a command:\n")
                
                if command == "logout":
                    
                    user_session["loggedIn"] = False
                    user_session["userId"] = ""
                    user_session["followers"] = 0
                    user_session["following"] = 0
                    user_session["collections"] = 0
                    print("Logged out")
                    
                elif command == "follow":
                    follow()
                    help()
                elif command == "unfollow":
                    unfollow()
                    help()
                elif command == "watch movie":
                    watch_movie()
                    help()
                elif command == "watch collection":
                    watch_collection()
                    help()
                elif command == "rate":
                    rate_movie()
                    help()
                elif command == "search":
                    search()
                    help()
                elif command == "add":
                    add_to_collection()
                    help()
                elif command == "remove":
                    remove_from_collection()
                    help()
                elif command == "delete collection":
                    delete_collection()
                    help()
                elif command == "view collections":
                    view_collections()
                    help()
                elif command == "create collection":
                    create_collection()
                    help()
                elif command == "name collection":
                    name_collection()
                    help()
                else:
                    print("Invalid command")
                    help()

def help():
    help_msg = \
"""
logout - logout of account
follow - follow a user
unfollow - unfollow a user
watch movie - watch a movie
watch collection - watch a collection
rate - rate a movie
search - search for a movie or user
add - add a movie to a collection
remove - remove a movie from a collection
delete collection- delete a movie from a collection
view collections - view all collections
create collection - create a collection
name collection - name a collection
"""
    print(help_msg)
    
def create_account():
    """  
    Allow users to create new accounts.  

    This function lets users create an account with a username, password, first and last name,  
    region, date of birth, and email address. The system will also record the date and time  
    of account creation.  
    """

    try:
        
        # gets the next available userId from users
        curs.execute("SELECT COALESCE(MAX(CAST(SUBSTRING(userId, 2) as INTEGER)), 0) + 1 FROM users")
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
        # users(userid, username, firstname, lastname, region, dob, password, creationdate)
        curs.execute("INSERT INTO users(userid, username, firstname, lastname, region, dob, password, creationdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                     (uid, username, firstname, lastname, region, dob, password, creation_date))
        
        curs.execute('INSERT INTO email VALUES (%s, %s)', (uid, email))

        conn.commit()

        print("Account has been created\n")

        login()
        
    except Exception as e:
        
        print("Error occurred creating account", e)

        conn.rollback()

def login():
    """  
    After creating an account, users can log in.  

    This function prompts the user for their username and password.  
    The system then checks if the entered password matches the one in the database.  
    If successful, it updates the access time.  
    """

    print("Login your account")

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

            user_id = user[0]

            #accessdates(userid, accessdate)
            curs.execute("SELECT 1 FROM accessdates WHERE userid = %s", (user_id,))

            existing_date = curs.fetchone()

            #if user contains an access date already, it updates automatically to current access date
            if existing_date:  

                curs.execute("""
                    UPDATE accessdates 
                    SET accessdate = %s 
                    WHERE userid = %s """, (access_date, user_id))
                
                #print(f"Access date updated for {username}!")

            else:  

                #if user is new and doesn't have the access date

                curs.execute("""
                    INSERT INTO accessdates(userid, accessdate)
                    VALUES (%s, %s)""", (user[0], access_date))
            
            user_session["userId"] = user[0]
            user_session["username"] = user[1]
            user_session["loggedIn"] = True
            
            print(f"Hello, {username}!")

            help()

            conn.commit()

        else: 

            print("Invalid username or password")

    except Exception as e:

        print(f"An error occurred: {e}")

        conn.rollback()  

def follow():
    """
    Allows the user to follow another user.  

    This function asks the user for another user's email  
    to send a follow request. The system notifies the user  
    if the followee cannot be found or if they are already following them.  
    """
    
    print("Follow a user")

    user_email = input("Enter users email: ").strip()
    
    try:
        
        # gets userid from email table
        curs.execute("SELECT userid FROM email WHERE email = %s", (user_email,))
        user_id = curs.fetchone()
        
        if not user_id:
            
            print("No user with this email found")
            return
        
        followed_id = user_id[0]
        
        # check if the user is already being followed
        curs.execute("SELECT 1 FROM follows WHERE follower = %s AND followee = %s", (user_session["userId"], followed_id))
        existing_follow = curs.fetchone()

        if existing_follow:
        
            print(f"You are already following {user_email}")

            return
        
        # gets username of the userid from users table
        curs.execute("SELECT username FROM users WHERE userid = %s", (followed_id,))
        user_data = curs.fetchone()
        
        if not user_data:
            
            print("User data missing")
            return
        
        followed_username = user_data[0]
        curs.execute("INSERT INTO follows VALUES (%s, %s)", (user_session["userId"], followed_id))
        conn.commit()

        print(f"You are following {followed_username}")
        
    except Exception as e:
        
        print("Error following user")
        conn.rollback()

def unfollow():
    """
    Allows the user to unfollow another user.  

    This function asks the user for the other user's email.  
    The system checks if the user exists and notifies them  
    if no account is found or if they are not following the user.      
    """
    
    print("Unfollow a user")
    user_email = input("Enter users email: ").strip()
    
    try:
        
        # gets userid 
        curs.execute("SELECT userid FROM email WHERE email = %s", (user_email,))
        user_id = curs.fetchone()
        
        if not user_id:
            
            print("No user with this email found")
            return
        
        followed_id = user_id[0]
        
        # check if the user is already being followed
        curs.execute("SELECT 1 FROM follows WHERE follower = %s AND followee = %s", (user_session["userId"], followed_id))
        existing_follow = curs.fetchone()

        if not existing_follow:
        
            print(f"You are not following {user_email}")
            return
        
        # gets username of the userid from users table
        curs.execute("SELECT * FROM follows WHERE follower = %s AND followee = %s", (user_session["userId"], followed_id))
        user_data = curs.fetchone()
        
        if not user_data:
            
            print("User data missing")
            return
        
        # Get the followed user's username
        curs.execute("SELECT username FROM users WHERE userid = %s", (followed_id,))
        followed_user = curs.fetchone()
        
        if not followed_user:
        
            print("Followed user not found")
            return
        
        followed_username = followed_user[0]
        
        # delete follower, followee relation from follows
        curs.execute("DELETE FROM follows WHERE follower = %s AND followee = %s", (user_session["userId"], followed_id))
        conn.commit()
        print(f"You unfollowed {followed_username}")
        
    except Exception as e:
        
        print("Error unfollowing user")
        conn.rollback()

def watch_movie():
    """
    Allows the user to watch a movie individually.  

    This function lets the user select a movie  
    to watch. When they access the movie, the system  
    records the date and time of access.  
    """

    print("Watch a movie")
    movie_id = input("Enter Movie ID: ").strip()
    
    try:
        
        # checks if movie exists in database
        curs.execute("SELECT * FROM movie WHERE movieid = %s", (movie_id,))
        movie = curs.fetchone()
        
        if not movie:
            print("Movie not found")
            return
        
        watch_date = datetime.datetime.now()

        # adds an entry in watches table
        curs.execute("INSERT INTO watches(userid, movieid, datetimewatched) VALUES (%s, %s, %s)"
                     , (user_session["userId"], movie_id, watch_date))
        conn.commit()
        print(f"Watched {movie}")
        
    except Exception as e:
        
        print("Error watching movie")
        conn.rollback()
    
def watch_collection():
    """
    Allows the user to watch an entire collection of movies.  

    This function lets the user select a collection to watch,  
    playing all movies in that collection. The system records  
    the date and time of access while watching.
    """        
    try:
        
        print("Watch a collection")

        user_id = user_session["userId"]

        curs.execute("SELECT collectionid, collectionname FROM collection where userid = %s", (user_id,))

        collection_list = curs.fetchall()

        if not collection_list:
            
            print("You have no collections right now")

            return
        
        print("Your Collections: ")
        
        for collection in collection_list:

            print(f"ID: {collection[0]}, Collection Name: {collection[1]}")

        collection_id = input("Enter Collection ID: ").strip()

        # gets movieid that are in the collection

        curs.execute("SELECT movieid FROM partof WHERE collectionid = %s", (collection_id,))
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
            
        conn.commit()

        print(f"Watched {collection_list}")
        
    except Exception as e:
        
        print("Error watching collection")
        conn.rollback()

def rate_movie():
    """
    Allows users to rate a movie.  

    This function lets the user provide a star rating (1-5)  
    for a specific movie. After rating, the rating is saved  
    to the movie's rating record.  
    """
    print("Rate movie")
    movie_name = input("Enter movie title: ").strip()
    
    try:
        
        # Search for movies by title
        curs.execute("SELECT movieid, title FROM movie WHERE title ILIKE %s", (movie_name,))
        movies = curs.fetchone()

        if not movies:
            
            print("No movie found with that title.")
            return
        
        movie_id = movies[0]
        rating = round(float(input("Enter rating(1-5): ")))

        # ensure rating within valid range
        if rating < 1 or rating > 5:
             
            print("Invalid rating! Please enter a number between 1 and 5.")
            return

        # Check if the user has already rated this movie
        curs.execute("SELECT * FROM rates WHERE movieid = %s AND userid = %s", 
                     (movie_id, user_session["userId"]))
        existing_rating = curs.fetchone()

        if existing_rating:
            
            # Update existing rating
            curs.execute("UPDATE rates SET starrating = %s WHERE movieid = %s AND userid = %s", 
                         (str(rating), movie_id, user_session["userId"]))
            print("Rating updated")
            
        else:
            
            # adds the movie rating into rates table
            curs.execute("INSERT INTO rates(movieid, userid, starrating) VALUES (%s, %s, %s)", 
                         (movie_id, user_session["userId"], str(rating)))
            print("Rating submitted")
        
        conn.commit()
        
    except Exception as e:
        
        print("Error occured rating movie")
        conn.rollback

def search():
    """
    Allows users to search movies by name, release date, cast members, studio, or genre.  

    This function lets users search for movies in the database based on their chosen criteria.  
    The system returns a list of movies sorted alphabetically (ascending) by movie name and release date.  
    Users can also choose to sort the list in ascending or descending order.  
    """

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
    "4": "LOWER(s.studioname)",  
    "5": "LOWER(g.genrename)"   
}

    search_by = input("Select (1 - 5): ").strip()

    #searched value to actually get the value user inputs
    selected_search = search_options[search_by]

    #prompt used to guide user's interaction
    selected_prompt = prompt_options[search_by] 

    search_value = input(f"Enter {selected_prompt}: ").strip()       

    #val = f"%{search_value.lower()}" 

    print("Sort Results By:")
    print("1. Movie Name")
    print("2. Studio")
    print("3. Genre")
    print("4. Release Date")

    sort_by = input("Select (1 - 4): ").strip()

    sort_options = {
        "1": "m.title",
        "2": "s.studioname",  
        "3": "g.genrename",   
        "4": "ro.releasedate"
    }
  
    if sort_by:

        sort_order = input("Select order (ASC or DESC): ").strip()

        if sort_order not in ["ASC", "DESC"]:

            print("Must either select ASC or DESC!")

            return

        sort_column = sort_options[sort_by]
        selected_order = (f"{sort_column} {sort_order}")

    else:

        selected_order = "ORDER BY m.title ASC, ro.releasedate ASC"

    query = f"""
            SELECT 
            m.title AS movie_name,
        CONCAT(mp.firstname, ' ', mp.lastname) AS cast_members,
        CONCAT(dp.firstname, ' ', dp.lastname) AS director_name,
        m.duration AS movie_duration,
        m.mpaarating AS mpaa_rating,
        ROUND(AVG(r.starrating), 1) AS user_rating,
        s.studioname AS studio,
        g.genrename AS genre,
        EXTRACT(YEAR FROM ro.releasedate) AS release_year
        FROM 
        Movie m
        LEFT JOIN starsin si ON m.movieid = si.movieid
        LEFT JOIN moviepeople mp ON si.personid = mp.personid
        LEFT JOIN directs dir ON m.movieid = dir.movieid
        LEFT JOIN moviepeople dp ON dir.personid = dp.personid
        LEFT JOIN rates r ON m.movieid = r.movieid 
        LEFT JOIN created c ON m.movieid = c.movieid
        LEFT JOIN studios s ON c.studioid = s.studioid
        LEFT JOIN contains co ON m.movieid = co.movieid
        LEFT JOIN genre g ON co.genreid = g.genreid
        LEFT JOIN releasedon ro ON m.movieid = ro.movieid
        WHERE 
        {selected_search} LIKE %s
        GROUP BY 
        m.movieid, m.title, mp.firstname, mp.lastname, dp.firstname, dp.lastname, m.duration, m.mpaarating, s.studioname, g.genrename, ro.releasedate
        ORDER BY 
        {selected_order};
        """

    val = f"%{search_value.lower()}%"  

    curs.execute(query, (val,))
    
    result_list = curs.fetchall()

    if not result_list:

        print("No results found")
        return

    for row in result_list:
        movie_name, cast_members, director_name, movie_duration, mpaa_rating, user_rating, studio, genre, release_year = row
        print(f"Movie: {movie_name}")
        print(f"Cast: {cast_members}")
        print(f"Director: {director_name}")
        print(f"Duration: {movie_duration} minutes")
        print(f"MPAA Rating: {mpaa_rating}")
        print(f"User Rating: {user_rating}")
        print(f"Studio: {studio}")
        print(f"Genre: {genre}")
        print(f"Release Year: {release_year}")
        print("-" * 40)


def add_to_collection():
    """
    Allows users to add movies to a collection.  

    This function lets users select a movie they want to add to one of their created collections.  
    The system will notify users if the movie is not found in the database or if they have no collections.  
    """

    print("Adding a movie to your collection")

    try:

        user_id = user_session["userId"]

        curs.execute("SELECT collectionid, collectionname FROM collection where userid = %s", (user_id,))

        collection_list = curs.fetchall()

        if not collection_list:
            
            print("You have no collections right now")

            return
        
        print("Your Collections: ")
        
        for collection in collection_list:

            print(f"ID: {collection[0]}, Collection Name: {collection[1]}")

        collection_id = input("Select Collection ID: ").strip()

        valid_collection_ids = [collection[0] for collection in collection_list]

        if collection_id not in valid_collection_ids:

            print("Invalid Collection ID. Must input c1, c2, c3....")
            
            return

        for collection in collection_list:

            if collection[0] == collection_id:

                collection_name = collection[1]

                break
        
        #collection_id = collection_list[collection_index][0]
        #collection_name = collection_list[collection_id][1]

        movie_name = input("Input the Movie Name to add: ").strip()

        curs.execute("""SELECT movieid
                        FROM movie
                        WHERE title = %s""", (movie_name,))
        
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
    """  
    Allows users to remove movies from a collection.  

    This function lets users view their collections,  
    select a collection, and see the movies within it.  
    """

    print("Removing a movie from your collection")

    try:
        user_id = user_session["userId"]

        # collection(collectionid, collectionname, userid)
        curs.execute("""SELECT CollectionID, CollectionName
                        FROM Collection
                        WHERE UserID = %s""", (user_id,))
        
        collection_list = curs.fetchall()

        if not collection_list:
            print("You currently have no collections right now.")
            return

        print("Your Collections: ")

        for collection in collection_list:

            print(f"ID: {collection[0]}, Collection Name: {collection[1]}")

        collection_id = input("Select Collection ID: ").strip()

        valid_collection_ids = [collection[0] for collection in collection_list]

        if collection_id not in valid_collection_ids:

            print("Invalid Collection ID. Must input c1, c2, c3....")
            
            return

        for collection in collection_list:

            if collection[0] == collection_id:

                collection_name = collection[1]

                break

        movie_name = input("Input the Movie Name to remove: ").strip()

        curs.execute("""SELECT movieid
                        FROM movie
                        WHERE title = %s""", (movie_name,))
        
        movie = curs.fetchone()

        if not movie:
            print("Movie is not found in database")
            return
        
        movie_id = movie[0]

        # Check if the movie exists in the collection
        curs.execute("""SELECT *
                        FROM PartOf 
                        WHERE CollectionID = %s AND MovieID = %s""", (collection_id, movie_id))
        
        movie_in_collection = curs.fetchone()

        if not movie_in_collection:
            print(f"'{movie_name}' is not in the collection '{collection_name}'")
            return

        # If movie exists in the collection, remove it
        curs.execute("""DELETE FROM PartOf
                        WHERE CollectionID = %s AND MovieID = %s""", (collection_id, movie_id))

        conn.commit()

        print(f"Successfully removed '{movie_name}' from '{collection_name}'")

    except Exception as e:
        print("Error removing movie from collection:", e)
        conn.rollback()

def delete_collection():
    """
    Allows users to delete an entire collection.  

    This function lets users select the collection ID they want to delete.  
    The system will notify users if the selected collection doesn't exist  
    or if there is an error during the deletion process.  
    """
    
    print("Deleting a collection")
    collection_name = input("Enter collection name: ").strip()
    
    try:
        
        curs.execute('SELECT collectionid FROM collection WHERE collectionname = %s', (collection_name,))
        collection_id = curs.fetchone()[0]
        
        # curs.execute("SELECT * FROM collection WHERE collectionname = %s", (collection_name,))
        # collection = curs.fetchone()
        
        # if not collection:
        #     print("Collection not found")
        #     return
        
        # delete collection from partof table
        curs.execute("DELETE FROM partof WHERE collectionid = %s", (collection_id,))
        
        # delete collection from collection table
        curs.execute("DELETE FROM collection WHERE collectionname = %s", (collection_name,))
        conn.commit()
        print(f"Deleted collection {collection_name}")
    
    except Exception as e:
        
        print("Error deleting collection")
        conn.rollback()

    
def view_collections():
    """
    Allows users to view a list of all their collections.  

    This function returns a list of all user-created collections,  
    sorted by name in ascending order. It also displays the number of  
    movies in each collection and the total length of movies in the collection.  
    """

    user_id = user_session["userId"]

    if not user_id:
        
        print("Need to be logged in to view collection")
        return

    try:
        curs.execute("""
            SELECT c.collectionname, 
                   COUNT(p.movieid) AS num_movies,
                   TO_CHAR(COALESCE(SUM(m.duration), 0) * INTERVAL '1 minute', 'HH24:MI') AS total_length
            FROM collection c
            LEFT JOIN partof p ON c.collectionid = p.collectionid  -- Correct JOIN using partof
            LEFT JOIN movie m ON p.movieid = m.movieid  -- Movies are linked via partof
            WHERE c.userid = %s
            GROUP BY c.collectionname
            ORDER BY c.collectionname ASC
        """, (user_id,))
                
        list_collections = curs.fetchall()

        for collect in list_collections:

            name = collect[0]
            num_movies = collect[1]
            #total_length = collect[2]
            total_length = collect[2] if collect[2] else "00:00" 

            print(f"Collection Name: '{name}'  Number Of Movies: '{num_movies}' Total Length Of Movies In Collection: '{total_length}'")
    except Exception as e:
        print(f"Error viewing collection: {e}")
        conn.rollback()

def create_collection():
    """
    Allows users to create a collection of movies.  

    This function lets users create new collections of movies.  
    The system will notify users if they try to create a collection with the same exact name as an existing one.  
    """

    print("Creating a new collection")

    #checks if the user is logged in
    #user_id = user_session["userid"]

    new_collection = input("Input the name of your new collection: ")

    collection_name = new_collection.strip()

    user_id = user_session["userId"]

    try:
        
        curs.execute("SELECT collectionid FROM collection WHERE collectionname = %s AND userid = %s", (new_collection, user_id))
        exist_collection = curs.fetchone()

        if exist_collection:

            print(f"You already have a collection named '{new_collection}'")

            return
        
        # gets the highest collection id
        # since collection id is a string like c1, c2, c3...
        # we use substring 2 to get numbers after "c" and cast numbers into integers
        curs.execute("""
            SELECT MAX(CAST(SUBSTRING(collectionid FROM 2) AS INT)) 
            FROM collection
        """)

        # the very last collection id of the database
        # must retrieve the value by using [0] in tuple
        latest_cid = curs.fetchone()[0]

        if latest_cid:

            collection_id = f"c{latest_cid + 1}"

        else:

            collection_id = "c1"

        #relational table is collection(collectionid, collectionname, userid)
        curs.execute("INSERT INTO Collection(collectionid, collectionname, userid) VALUES (%s, %s, %s)", (collection_id, collection_name, user_id))

        conn.commit()

        print(f"Collection '{collection_name}' has been created!")

    except Exception as e:

        print("Error occured when attempting to create collection:", e)
        conn.rollback()

def name_collection():
    """  
    Allows users to modify the name of a collection.  

    This function lets users select an existing collection and change its name,  
    without deleting or adding new collections.  
    """

    print("Modifying the name of a collection")

    try: 

        user_id = user_session["userId"]

        curs.execute("SELECT collectionid, collectionname FROM collection where userid = %s", (user_id,))

        collection_list = curs.fetchall()

        if not collection_list:
            
            print("You have no collections right now")

            return
        
        print("Your Collections: ")
        
        for collection in collection_list:

            print(f"ID: {collection[0]}, Collection Name: {collection[1]}")

        collection_id = input("Select Collection ID: ").strip()

        valid_collection_ids = [collection[0] for collection in collection_list]

        if collection_id not in valid_collection_ids:

            print("Invalid Collection ID. Must input c1, c2, c3....")
            
            return

        for collection in collection_list:

            if collection[0] == collection_id:

                collection_name = collection[1]

                break

        new_collection_name = input(f"Current Collection Name: '{collection_name}'. Enter new name: ").strip()

        if not new_collection_name:

            print("Collection name cannot be empty")

            return

        curs.execute("""UPDATE collection
                        SET collectionname = %s
                        WHERE collectionid = %s""", (new_collection_name, collection_id))

        conn.commit()

        print(f"Collection name successfully updated to '{new_collection_name}'.")

    except Exception as e:
        
        print("Error modifying collection name:", e)
        conn.rollback()

