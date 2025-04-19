import datetime

def watch_movie(user_session, curs, conn):
    """
    Allows the user to watch a movie individually.  

    This function lets the user select a movie  
    to watch. When they access the movie, the system  
    records the date and time of access.  
    """

    print("Watch a movie")
    movie_name = input("Enter movie title: ").strip()
    
    try:
        
        # Search for movies by title
        curs.execute("SELECT movieid FROM movie WHERE title ILIKE %s", (movie_name,))
        movies = curs.fetchone()

        if not movies:
            
            print("No movie found with that title.")
            return
        
        watch_date = datetime.datetime.now()

        # adds an entry in watches table
        curs.execute("INSERT INTO watches(userid, movieid, datetimewatched) VALUES (%s, %s, %s)"
                     , (user_session["userId"], movies[0], watch_date))
        
        conn.commit()
        
        print(f"Watched {movie_name}")
        
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

        collection_name = input("Enter Collection Name: ").strip()

        # gets collectionid from collectionname
        curs.execute("SELECT collectionid FROM collection WHERE collectionname ILIKE %s AND userid = %s"
                     , (collection_name, user_session["userId"]))
        collection_id = curs.fetchone()[0]
        
        # gets movieid that are in the collection
        curs.execute("SELECT movieid FROM partof WHERE collectionid = %s", (collection_id,))
        movie_ids = curs.fetchall()
        watch_date = datetime.datetime.now()
        
        # checks if there are movies in the collection
        if not movie_ids:
            print("No movies in collection")
            return
        
        movie_list = ""
        # creates a watches entry for each movie in the collection
        for movie in movie_ids:
            
            movie_id = movie[0]
            curs.execute("INSERT INTO watches(userid, movieid, datetimewatched) VALUES (%s, %s, %s)",
                         (user_session["userId"], movie_id, watch_date))
            
            # adds movie name to a list to print
            curs.execute("SELECT title FROM movie WHERE movieid = %s", (movie_id,))         
            movie_list += "'" + curs.fetchone()[0] + "' "
            
            
        conn.commit()

        print(f"Watched {movie_list}")
        
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
        curs.execute("SELECT movieid FROM movie WHERE title ILIKE %s", (movie_name,))
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
        "2": "TO_CHAR(ro.releasedate, 'YYYY-MM-DD')",
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
        print(f"User Rating: {'Unrated' if user_rating is None else user_rating}")
        print(f"Studio: {studio}")
        print(f"Genre: {genre}")
        print(f"Release Year: {'Unreleased' if release_year is None else release_year}")

def view_top_10(user_session, curs, conn):
    """
    Helper function allow users to query their top 10 movies 
    by Highest rated, most watched or combination of both
    """
    
    print("View your top 10 movies by:")
    print("1. Highest Rating")
    print("2. Most watched")
    print("3. Both")

    search_by = input("Select (1-3): ").strip()

    if search_by not in ["1", "2", "3"]:
        print("Invalid option")
        return
    userid = user_session.get("userId")

    if search_by == "1":
        order_clause = "ORDER BY user_rating DESC NULLS LAST, title"
        rating_join = "INNER JOIN rates r ON m.movieid = r.movieid AND r.userid = %s"
        watch_join = "LEFT JOIN watches w ON m.movieid = w.movieid AND w.userid = %s"
        where_clause = ""
        
    elif search_by == "2":
        rating_join = "LEFT JOIN rates r ON m.movieid = r.movieid AND r.userid = %s"
        watch_join = "INNER JOIN watches w ON m.movieid = w.movieid AND w.userid = %s"
        where_clause = ""
        order_clause = "ORDER BY watch_count DESC, title"

    else:  # search_by == "3":
        rating_join = "LEFT JOIN rates r ON m.movieid = r.movieid AND r.userid = %s"
        watch_join = "LEFT JOIN watches w ON m.movieid = w.movieid AND w.userid = %s"
        where_clause = "WHERE r.starrating IS NOT NULL OR w.userid IS NOT NULL"
        order_clause = "ORDER BY user_rating DESC NULLS LAST, watch_count DESC, title"
    
    base_query = f"""
        SELECT
            m.movieid,
            m.title,
            m.duration,
            m.mpaarating,
            ROUND(MAX(r.starrating), 1) AS user_rating,
            COUNT(w.userid) AS watch_count,
            STRING_AGG(DISTINCT CONCAT(mp.firstname, ' ', mp.lastname), ', ') AS cast_members,
            STRING_AGG(DISTINCT CONCAT(dp.firstname, ' ', dp.lastname), ', ') AS director_name,
            STRING_AGG(DISTINCT s.studioname, ', ') AS studios,
            STRING_AGG(DISTINCT g.genrename, ', ') AS genres,
            EXTRACT(YEAR FROM ro.releasedate) AS release_year

        FROM
            Movie m
            LEFT JOIN starsin si ON m.movieid = si.movieid
            LEFT JOIN moviepeople mp ON si.personid = mp.personid
            LEFT JOIN directs dir ON m.movieid = dir.movieid
            LEFT JOIN moviepeople dp ON dir.personid = dp.personid
            {rating_join}
            LEFT JOIN created c ON m.movieid = c.movieid
            LEFT JOIN studios s ON c.studioid = s.studioid
            LEFT JOIN contains co ON m.movieid = co.movieid
            LEFT JOIN genre g ON co.genreid = g.genreid
            LEFT JOIN releasedon ro ON m.movieid = ro.movieid
            {watch_join}
        {where_clause}
        GROUP BY
            m.movieid, m.title, m.duration, m.mpaarating, ro.releasedate
        {order_clause}
        LIMIT 10
    """

    try:
        curs.execute(base_query, (userid, userid))
        result_list = curs.fetchall()

        print("\nTop 10 Movies Based on Your Choice:\n")
        if not result_list:
            print("No movies found. Watch or rate some movies to see your top picks!")
            return

        for row in result_list:
            (movieid, title, duration, mpaa, rating, watch_count,
            cast, director, studios, genres, release_year) = row

            print("-" * 40)
            print(f"Title: {title}")
            print(f"Duration: {duration} mins")
            print(f"MPAA Rating: {mpaa}")
            print(f"Your Rating: {'Unrated' if rating is None else rating}")
            print(f"Times Watched: {watch_count}")
            print(f"Cast: {cast}")
            print(f"Director: {director}")
            print(f"Studios: {studios}")
            print(f"Genres: {genres}")
            print(f"Release Year: {'Unreleased' if release_year is None else int(release_year)}")

    except Exception as e:
        print("An error occurred while retrieving your top 10 movies:")
        print(e)
        return

def view_top_20_last_90_days(curs, conn):

    #rolling meaning it updates everyday for new movies in top 20 list
    print("The Top 20 Most Popular Movies In Last 90 Days\n")

    try:
        
        current_date = datetime.datetime.now()

        ninety_days_ago = (current_date - datetime.timedelta(days=90)).strftime('%Y-%m-%d')

        #print(datetime.timedelta(days=90)).strftime('%Y-%m-%d')

        query = f"""
            SELECT 
                m.title AS movie_name,
                COUNT(w.movieid) as watch_count
                FROM movie m
                JOIN watches w on m.movieid = w.movieid
                WHERE w.datetimewatched >= %s
                GROUP BY m.movieid, m.title
                ORDER BY watch_count DESC
                LIMIT 20;
                """

        curs.execute(query, (ninety_days_ago,))

        top_20_list = curs.fetchall()

        #print(len(top_20_movie))

        i = 0

        for movie in top_20_list:

            movie_name = movie[0]
            watch_count = movie[1]

            i += 1

            print(f"Movie {i}: {movie_name} with watch count of {watch_count}.\n")

    except Exception as e:
        
        print(f"Error viewing top 20 movies last 90 days: {e}")

        conn.rollback()

#Find the top 5 new releases of the month (calendar month)

def view_top_5_new_releases(curs, conn):

    print("View Top 5 New Releases Of The Month")

    try:

        #current_date = datetime.datetime.now()

        #current_month = current_date.month

        #

        #print(current_month)

        get_month = input("Input the month (1-12): ")
        get_year = input("Inputer the year (YYYY): ")
        print("\n")

        query = f"""
            SELECT
                m.title AS movie_name,
                COUNT(w.movieid) as watch_count
                FROM movie m
                JOIN watches w on m.movieid = w.movieid
                JOIN releasedon r on m.movieid = r.movieid
                WHERE EXTRACT(YEAR FROM r.releasedate) = %s
                AND EXTRACT(MONTH FROM r.releasedate) = %s
                GROUP BY m.movieid, m.title
                ORDER BY watch_count DESC
                LIMIT 5;
                """

        curs.execute(query, (get_year, get_month))

        top_5_list = curs.fetchall()

        i = 0

        for movie in top_5_list:

            i += 1

            movie_name = movie[0]
            watch_count = movie[1]

            print(f"Movie {i}: {movie_name} with watch count of {watch_count}.\n")


    except Exception as e:

        print(f"Error viewing top 5 new releases of the month: {e}")

        conn.rollback()
