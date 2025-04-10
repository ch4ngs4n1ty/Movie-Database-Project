import datetime
import bcrypt
from getpass import getpass 

def create_account(user_session, curs, conn):
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
        
        # ensure unique username
        while True:
            
            print()
            username = input("Username: ").strip()

            # check if the username is already taken
            curs.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            
            if curs.fetchone():
            
                print("Username already taken. Please choose a different one.")
            
            else:
            
                break  # username is unique
        
        raw_pass = getpass("Password: ").encode('utf-8').strip()
        password = bcrypt.hashpw(raw_pass, bcrypt.gensalt())

        #print("Hashed password:", password.decode())
        
        email = None
        # ensure unique email
        while True:
            
            email = input("Email address: ").strip()
            curs.execute("SELECT 1 FROM email WHERE email = %s", (email,))
            
            if curs.fetchone():
                
                print("Email already in use. Please enter a different email.")
                
            else:
                
                break  # email is unique
        
        firstname = input("First Name: ").strip()
        lastname = input("Last Name: ").strip()
        region = input("Region: ").strip()
        dob = input("Date of birth(YYYY-MM-DD): ").strip()
        email = email
        creation_date = datetime.datetime.now()
        
        # adds the users account to users
        # users(userid, username, firstname, lastname, region, dob, password, creationdate)
        curs.execute("INSERT INTO users(userid, username, firstname, lastname, region, dob, password, creationdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                     (uid, username, firstname, lastname, region, dob, password.decode(), creation_date))
        
        curs.execute('INSERT INTO email VALUES (%s, %s)', (uid, email))

        conn.commit()

        print("Account has been created\n")
        
    except Exception as e:
        
        print("Error occurred creating account", e)

        conn.rollback()

def login(user_session, curs, conn):
    """  
    After creating an account, users can log in.  

    This function prompts the user for their username and password.  
    The system then checks if the entered password matches the one in the database.  
    If successful, it updates the access time.  
    """

    print() # Newline to create space. 
    print("Login your account")

    username = input("Username: ")
    password = getpass("Enter password: ").encode('utf-8')

    try:

        #selects only userid, username, and password 
        curs.execute("SELECT userid, username, password FROM users WHERE username = %s", (username,)) 

        #search for user with the provided username
        #user = (userid, username, password)
        user = curs.fetchone() 

        #checks if user exists and user's password equals to inputted password
        if user and bcrypt.checkpw(password, user[2].encode('utf-8')): 

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

            conn.commit()

        else: 

            print("Invalid username or password")

    except Exception as e:

        print(f"An error occurred: {e}")

        conn.rollback()  