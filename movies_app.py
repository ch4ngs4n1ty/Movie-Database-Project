from movies.auth import (
    create_account,
    login
)
from movies.user import (
    follow,
    unfollow
)
from movies.movie import (
    watch_movie,
    watch_collection,
    rate_movie,
    search
)
from movies.collection import (
    add_to_collection,
    remove_from_collection,
    delete_collection,
    view_collections,
    create_collection,
    name_collection
)

def main(curs, conn):
    user_session = {
        "loggedIn": False,
        "userId": None,
        "followers": 0,
        "following": 0,
        "collections": 0
    }

    while True:
        while not user_session["loggedIn"]:
            command = input("Would you like to login or create an account?\n" + 
                            "login - log into an account\n" +
                            "create account - create an account\n")
            if command == "create account":
                create_account(user_session, curs, conn)

            if command == "login":
                login(user_session, curs, conn)

            else:
                print("login - log into an account")
                print("create account - create an account")

            while user_session["loggedIn"]:
                help()
                command = input("Enter a command:\n")

                if command == "logout":
                    user_session["loggedIn"] = False
                    user_session["userId"] = ""
                    user_session["followers"] = 0
                    user_session["following"] = 0
                    user_session["collections"] = 0
                    print("Logged out")

                elif command == "follow":
                    follow(user_session, curs, conn)

                elif command == "unfollow":
                    unfollow(user_session, curs, conn)

                elif command == "watch movie":
                    watch_movie(user_session, curs, conn)

                elif command == "watch collection":
                    watch_collection(user_session, curs, conn)

                elif command == "rate":
                    rate_movie(user_session, curs, conn)

                elif command == "search":
                    search(user_session, curs, conn)

                elif command == "add":
                    add_to_collection(user_session, curs, conn)

                elif command == "remove":
                    remove_from_collection(user_session, curs, conn)

                elif command == "delete collection":
                    delete_collection(user_session, curs, conn)

                elif command == "view collections":
                    view_collections(user_session, curs, conn)

                elif command == "create collection":
                    create_collection(user_session, curs, conn)

                elif command == "name collection":
                    name_collection(user_session, curs, conn)

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
