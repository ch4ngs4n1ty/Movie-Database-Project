from collection import total_collections

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

def view_profile(user_session, curs, conn): 
    total_collections(user_session, curs, conn)
    view_followers(user_session, curs, conn)
    view_followed(user_session, curs, conn)

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

    # print("you have x followers")

def view_top_20_movies_among_users(user_session, curs, conn):

    print("The top 20 most popular movies among users followed by the current user")

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

        print(top_20_list)

        i = 0

        for movie in top_20_list:

            movie_name = movie[0]
            watch_count = movie[1]

            i += 1

            print(f"Movie {i}: {movie_name} with watch count of {watch_count}.\n")

    except Exception as e:

        print(f"Error viewing top 20 most popular movies among users followed by the current user: {e}")

        conn.rollback()
