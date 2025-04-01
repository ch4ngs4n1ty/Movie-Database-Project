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

    user_email = input("Input user's email to view their profile:  ").strip()

    try:

        curs.execute("SELECT userid FROM email WHERE email = %s", (user_email,))

        user_id = curs.fetchone()

        if not user_id:
            
            print("No user with this email found")
            return

        user_id = user_id[0]

        print("Number Of Collections\n")

        curs.execute("SELECT COUNT(*) FROM collection WHERE userid = %s", (user_id,))

        num_collection = curs.fetchone()[0]

        print(f"Collection Count: {num_collection}")

    except Exception as e:
        
        print("Error viewing profile")
        conn.rollback()    






    
