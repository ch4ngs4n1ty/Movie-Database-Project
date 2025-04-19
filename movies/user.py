from movies.collection import total_collections
from movies.movie import view_top_10

from movies.collection import total_collections

def follow(user_session, curs, conn):
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

def unfollow(user_session, curs, conn):
    """
    Allows the user to unfollow another user.  

    This function asks the user for the other user's email.  
    The system checks if the user exists and notifies them  
    if no account is found or if they are not following the user.      
    """
    
    print("Unfollow A User")
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


def view_followed(user_session, curs, conn):
    """
    Helper function for User Profile to find total users followed
    """

    user_id = user_session["userId"]

    if not user_id:
        print("Need to be logged in to view followed count")
        return

    try:
        curs.execute("""
            SELECT COUNT(*) FROM follows
            WHERE follower = %s
            """,(user_id,))

        total_following = curs.fetchone()[0]
        print(f"You follow {total_following} people.")
        return total_following
    
    except Exception as e:
        print(f"Error retrieving followed count: {e}")

def view_followers(user_session, curs, conn):
    """
    Helper function for User Profile to find total followers
    """ 

    user_id = user_session["userId"]

    if not user_id:
        print("Need to be logged in to view follower count")
        return

    try:
        curs.execute("""
            SELECT COUNT(*) FROM follows
            WHERE followee = %s
            """,(user_id,))

        total_followers = curs.fetchone()[0]
        print(f"You have {total_followers} followers.")
        return total_followers
    
    except Exception as e:
        print(f"Error retrieving follower count: {e}")

def view_profile(user_session, curs, conn):
    """
    displays all the funtionality of the user (follower count, followers count, total collections, top 10 watched)
    """

    user_id = user_session["userId"]

    if not user_id:
        print("Must be logged in to view profile details")
        return
    
    view_followed(user_session, curs, conn)
    view_followers(user_session, curs, conn)
    total_collections(user_session, curs, conn)
    view_top_10(user_session, curs, conn)


def view_top_20_movies_among_users(user_session, curs, conn):

    print("The top 20 most popular movies among users followed by the current user\n")

    try:

        user_id = user_session["userId"]

        query = f"""
            SELECT
                m.title AS movie_name,
                COUNT(w.movieid) AS watch_count
                FROM follows f
                JOIN watches w ON f.followee = w.userid
                JOIN movie m ON w.movieid = m.movieid
                WHERE f.follower = %s
                GROUP BY m.movieid, m.title
                ORDER BY watch_count DESC
                LIMIT 20;
                """

        curs.execute(query, (user_id,))

        top_20_list = curs.fetchall()

        i = 0

        for movie in top_20_list:

            movie_name = movie[0]
            watch_count = movie[1]

            i += 1

            print(f"Movie {i}: {movie_name} with watch count of {watch_count}.")

    except Exception as e:

        print(f"Error viewing top 20 most popular movies among users followed by the current user: {e}")

        conn.rollback()

#You must provide the ability to recommend movies to watch to based on your playhistory 
#(e.g. genre, cast member, rating) and the play history of similar users

def recommend_movies(user_session, curs, conn):

    print("Recommend Movies")

    try:
    
        user_id = user_session["userId"]

        print("Recommend Your Movie History By:")
        print("1. Genre")
        print("2. Cast Member")
        print("3. Star Rating")

        rec_by = input("Select (1 - 3) or press ENTER based on similar users: ").strip()

        rec_options = {

            "1": "g.genrename",
            "2": "LOWER(CONCAT(mp.firstname, ' ', mp.lastname))",  
            "3": "m.mpaarating",   
        }

        if rec_by:

            if rec_by == "1":

                genre_option = rec_options[rec_by]

                genre = input("Select Genre: ")

                from_clause = """
                    FROM users u
                    LEFT JOIN watches w ON w.userid = u.userid
                    LEFT JOIN movie m ON w.movieid = m.movieid
                    LEFT JOIN contains c ON m.movieid = c.movieid
                    LEFT JOIN genre g ON c.genreid = g.genreid
                    """

                query = f"""
                    SELECT
                        m.title as movie_name,
                        COUNT(w.movieid) AS watch_count,
                        STRING_AGG(DISTINCT g.genrename, ', ') AS genres

                        {from_clause}
        
                        WHERE 
                            {genre_option} ILIKE %s
                            AND m.movieid NOT IN (
                            SELECT movieid FROM watches WHERE userid = %s
                            )

                        GROUP BY m.title
                        ORDER BY watch_count DESC
                        LIMIT 5;

                        """
                curs.execute(query, (genre, user_id))

                rec_genre_list = curs.fetchall()

                i = 0

                for movie in rec_genre_list:

                    i += 1

                    movie_name = movie[0]
                    watch_count = movie[1]
                    genre_name = movie[2]

                    print(f"{genre_name} Recommendation List\n")
                    print(f"Movie {i}: {movie_name} with watch count of {watch_count}.\n")

            elif rec_by == "2":

                cast_option = rec_options[rec_by]

                member = input("Select Cast Member: ").strip().lower()

                from_clause = """
                    FROM users u
                    LEFT JOIN watches w ON w.userid = u.userid
                    LEFT JOIN movie m ON w.movieid = m.movieid
                    LEFT JOIN starsin s ON m.movieid = s.movieid
                    LEFT JOIN moviepeople mp ON s.personid = mp.personid 
                    """

                query = f"""
                    SELECT
                        m.title as movie_name,
                        COUNT(w.movieid) AS watch_count,
                        STRING_AGG(DISTINCT CONCAT(mp.firstname, ' ', mp.lastname), ', ') AS cast_member

                        {from_clause}

                        WHERE 
                            {cast_option} ILIKE %s
                            AND m.movieid NOT IN (
                            SELECT movieid FROM watches WHERE userid = %s
                            )

                        GROUP by m.title 
                        ORDER BY watch_count DESC
                        LIMIT 5;
                        """

                curs.execute(query, (member, user_id))

                rec_member_list = curs.fetchall()

                i = 0

                for movie in rec_member_list:

                    i += 1

                    movie_name = movie[0]
                    watch_count = movie[1]
                    member_name = movie[2]

                    print(f"{member_name} Recommendation\n")
                    print(f"Movie {i}: {movie_name} with watch count of {watch_count}.\n")

            elif rec_by == "3":

                mpaa_option = rec_options[rec_by]

                mpaa = input("Select MPAA Rating: ")

                from_clause = """
                    FROM users u
                    LEFT JOIN watches w ON w.userid = u.userid
                    LEFT JOIN movie m ON w.movieid = m.movieid
                    """

                query = f"""
                    SELECT
                        m.title as movie_name,
                        COUNT(w.movieid) AS watch_count,
                        m.mpaarating AS mpaa_rating
                        
                        {from_clause}

                        WHERE 
                            {mpaa_option} ILIKE %s
                            AND u.userid = %s

                        GROUP by m.title, m.mpaarating
                        ORDER BY watch_count DESC
                        LIMIT 5;
                        """
                
                curs.execute(query, (mpaa, user_id))

                rec_mpaa_list = curs.fetchall()

                i = 0

                for movie in rec_mpaa_list:

                    i += 1

                    movie_name = movie[0]
                    watch_count = movie[1]
                    mpaa_name = movie[2]

                    print(f"{mpaa_name} Recommendation\n")
                    print(f"Movie {i}: {movie_name} with watch count of {watch_count}.\n")

        else:

            print("Viewing Similar User Play History\n")

            from_clause = """
                FROM follows f
                LEFT JOIN watches w ON w.userid = f.follower
                LEFT JOIN movie m ON w.movieid = m.movieid
                """

            query = f"""
                SELECT
                    m.title AS movie_name,
                    COUNT(w.movieid) AS watch_count,
                    f.follower AS follower

                    {from_clause}

                    WHERE 
                        f.followee = %s
                        AND m.movieid NOT IN (
                        SELECT movieid FROM watches WHERE userid = %s
                        )

                    GROUP by m.title, f.follower
                    ORDER BY watch_count DESC
                    LIMIT 5;

                    """
                
            curs.execute(query, (user_id,))

            rec_user_list = curs.fetchall()


            i = 0

            for movie in rec_user_list:

                i += 1

                movie_name = movie[0]
                watch_count = movie[1]
                follower_name = movie[2]

                print(f"Similar User: {follower_name}, Movie {i}: {movie_name} with watch count of {watch_count}.\n")

    except Exception as e:

        
        print(f"Error viewing recommended movies: {e}")

        conn.rollback()


