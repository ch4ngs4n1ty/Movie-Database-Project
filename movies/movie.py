import datetime

def watch_movie(user_session, curs, conn):
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
    
def watch_collection(user_session, curs, conn):
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

def rate_movie(user_session, curs, conn):
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

def search(user_session, curs, conn):
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

    search_value = input(f"Enter {prompt_options[search_by]}: ").strip()       

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
    
    from_clause = """
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
    """
    if sort_by == "1":
        query = f"""
            SELECT 
                m.title AS movie_name,
                STRING_AGG(DISTINCT CONCAT(mp.firstname, ' ', mp.lastname), ', ') AS cast_members,
                STRING_AGG(DISTINCT CONCAT(dp.firstname, ' ', dp.lastname), ', ') AS director_name,
                m.duration AS movie_duration,
                m.mpaarating AS mpaa_rating,
                ROUND(AVG(r.starrating), 1) AS user_rating,
                STRING_AGG(DISTINCT s.studioname, ', ') AS studios,
                STRING_AGG(DISTINCT g.genrename, ', ') AS genres, 
                STRING_AGG(DISTINCT EXTRACT(YEAR FROM ro.releasedate)::TEXT, ', ') AS release_year
            {from_clause}
            WHERE 
                {selected_search} LIKE %s
            GROUP BY 
                m.movieid, m.title, m.duration, m.mpaarating
            ORDER BY 
                {selected_order};
            """
    elif sort_by == "2":
        query = f"""
            SELECT 
                m.title AS movie_name,
                STRING_AGG(DISTINCT CONCAT(mp.firstname, ' ', mp.lastname), ', ') AS cast_members,
                STRING_AGG(DISTINCT CONCAT(dp.firstname, ' ', dp.lastname), ', ') AS director_name,
                m.duration AS movie_duration,
                m.mpaarating AS mpaa_rating,
                ROUND(AVG(r.starrating), 1) AS user_rating,
                s.studioname AS studios,
                STRING_AGG(DISTINCT g.genrename, ', ') AS genres, 
                STRING_AGG(DISTINCT EXTRACT(YEAR FROM ro.releasedate)::TEXT, ', ') AS release_year
            {from_clause}
            WHERE 
                {selected_search} LIKE %s
            GROUP BY 
                m.movieid, m.title, m.duration, m.mpaarating, s.studioname
            ORDER BY 
                {selected_order};
            """
    elif sort_by == "3":
        query = f"""
            SELECT 
                m.title AS movie_name,
                STRING_AGG(DISTINCT CONCAT(mp.firstname, ' ', mp.lastname), ', ') AS cast_members,
                STRING_AGG(DISTINCT CONCAT(dp.firstname, ' ', dp.lastname), ', ') AS director_name,
                m.duration AS movie_duration,
                m.mpaarating AS mpaa_rating,
                ROUND(AVG(r.starrating), 1) AS user_rating,
                STRING_AGG(DISTINCT s.studioname, ', ') AS studios,
                g.genrename AS genres, 
                STRING_AGG(DISTINCT EXTRACT(YEAR FROM ro.releasedate)::TEXT, ', ') AS release_year
            {from_clause}
            WHERE 
                {selected_search} LIKE %s
            GROUP BY 
                m.movieid, m.title, m.duration, m.mpaarating, g.genrename
            ORDER BY 
                {selected_order};
            """
    elif sort_by == "4":
        query = f"""
            SELECT 
                m.title AS movie_name,
                STRING_AGG(DISTINCT CONCAT(mp.firstname, ' ', mp.lastname), ', ') AS cast_members,
                STRING_AGG(DISTINCT CONCAT(dp.firstname, ' ', dp.lastname), ', ') AS director_name,
                m.duration AS movie_duration,
                m.mpaarating AS mpaa_rating,
                ROUND(AVG(r.starrating), 1) AS user_rating,
                STRING_AGG(DISTINCT s.studioname, ', ') AS studios,
                STRING_AGG(DISTINCT g.genrename, ', ') AS genres, 
                EXTRACT(YEAR FROM ro.releasedate) AS release_year
            {from_clause}
            WHERE 
                {selected_search} LIKE %s
            GROUP BY 
                m.movieid, m.title, m.duration, m.mpaarating, ro.releasedate
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
        print("-" * 40)
        print(f"Movie: {movie_name}")
        print(f"Cast: {cast_members}")
        print(f"Director: {director_name}")
        print(f"Duration: {movie_duration} minutes")
        print(f"MPAA Rating: {mpaa_rating}")
        print(f"User Rating: {"Unrated" if user_rating is None else user_rating}")
        print(f"Studio: {studio}")
        print(f"Genre: {genre}")
        print(f"Release Year: {"Unreleased" if release_year is None else release_year}")