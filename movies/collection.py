def add_to_collection(user_session, curs, conn):
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

        collection_name = input("Select Collection Name: ").strip()

        valid_collection_names = [collection[1] for collection in collection_list]

        if collection_name not in valid_collection_names:

            print("Invalid Collection Name.")
            
            return

        for collection in collection_list:

            if collection[1] == collection_name:

                collection_id = collection[0]

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

def remove_from_collection(user_session, curs, conn):
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

        collection_name = input("Select Collection Name: ").strip()

        valid_collection_names = [collection[1] for collection in collection_list]

        if collection_name not in valid_collection_names:

            print("Invalid Collection Name.")
            
            return

        for collection in collection_list:

            if collection[1] == collection_name:

                collection_id = collection[0]

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

def delete_collection(user_session, curs, conn):
    """
    Allows users to delete an entire collection.  

    This function lets users select the collection ID they want to delete.  
    The system will notify users if the selected collection doesn't exist  
    or if there is an error during the deletion process.  
    """
    
    print("Which collection do you want to delete?")
    view_collections(user_session, curs, conn)
    collection_name = input("Enter collection name: ").strip()
    
    try:
        curs.execute('SELECT collectionname FROM collection WHERE userid = %s AND collectionname = %s', (user_session["userId"], collection_name))
        collectionname_check = curs.fetchone()

        if (collectionname_check is None): 
            print(f"No collection with name '{collection_name}'")
            return
        
        curs.execute('SELECT collectionid FROM collection WHERE collectionname = %s', (collection_name,))
        collection_id = curs.fetchone()[0]

        # delete collection from partof table
        curs.execute("DELETE FROM partof WHERE collectionid = %s", (collection_id,))
        
        # delete collection from collection table
        curs.execute("DELETE FROM collection WHERE collectionname = %s", (collection_name,))
        conn.commit()
        print(f"Deleted collection {collection_name}")
    
    except Exception as e:
        
        print("Error deleting collection")
        conn.rollback()

    
def view_collections(user_session, curs, conn):
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

        if not list_collections:
            
            print("You have no collections right now")

            return

        for collect in list_collections:

            name = collect[0]
            num_movies = collect[1]
            total_length = collect[2] if collect[2] else "00:00" 

            print(f"Collection Name: '{name}'  Number Of Movies: '{num_movies}' Total Length Of Movies In Collection: '{total_length}'")
    
    except Exception as e:

        print(f"Error viewing collection: {e}")

        conn.rollback()

def create_collection(user_session, curs, conn):
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

def rename_collection(user_session, curs, conn):
    """  
    Allows users to modify the name of a collection.  

    This function lets users select an existing collection and change its name,  
    without deleting or adding new collections.  
    """

    print("Choose a collection to rename.")

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

        print() #Creating white space to separate things for readability.
        collection_name = input("Select Collection Name: ").strip()

        valid_collection_names = [collection[1] for collection in collection_list]

        if collection_name not in valid_collection_names:

            print("Invalid Collection Name.")
            
            return

        for collection in collection_list:

            if collection[1] == collection_name:

                collection_id = collection[0]

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

def total_collections(user_session, curs, conn):
    try: 
        curs.execute("""
            SELECT COUNT(*) as count 
            FROM collection
            WHERE userid = %s
        """, (user_session["userId"],))
        num_of_collections = curs.fetchone()
    except Exception as e: 
        conn.rollback
        print(f'❌ Error counting total collections: {e}') 

    print(f'You have {num_of_collections[0]} collections.')
    