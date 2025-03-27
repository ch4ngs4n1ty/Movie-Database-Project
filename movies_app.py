from movies.auth import (
    create_account,
    login
)
from movies.user import (
    follow,
    unfollow,
    view_followed,
    view_followers
)
from movies.movie import (
    watch_movie,
    watch_collection,
    rate_movie,
    search,
    view_top_10
)
from movies.collection import (
    add_to_collection,
    remove_from_collection,
    delete_collection,
    view_collections,
    create_collection,
    rename_collection,
    total_collections
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
            print()
            command = input("Would you like to login or create an account?\n" + 
                            "login - log into an account\n" +
                            "create account - create an account\n")
            if command == "create account":
                create_account(user_session, curs, conn)

            if command == "login":
                login(user_session, curs, conn)
                if user_session["loggedIn"] == True: 
                    help()

            while user_session["loggedIn"]:
                print()
                command = input("Enter a command:\n").strip()

                if command == "logout":
                    user_session["loggedIn"] = False
                    user_session["userId"] = ""
                    user_session["followers"] = 0
                    user_session["following"] = 0
                    user_session["collections"] = 0
                    print("Logged out")

                elif command == "follow":
                    print()
                    follow(user_session, curs, conn)

                elif command == "unfollow":
                    print()
                    unfollow(user_session, curs, conn)

                elif command == "watch movie":
                    print()
                    watch_movie(user_session, curs, conn)

                elif command == "watch collection":
                    print()
                    watch_collection(user_session, curs, conn)

                elif command == "rate":
                    print()
                    rate_movie(user_session, curs, conn)

                elif command == "search":
                    print()
                    search(user_session, curs, conn)

                elif command == "add":
                    print()
                    add_to_collection(user_session, curs, conn)

                elif command == "remove":
                    print()
                    remove_from_collection(user_session, curs, conn)

                elif command == "delete collection":
                    print()
                    delete_collection(user_session, curs, conn)

                elif command == "view collections":
                    print()
                    view_collections(user_session, curs, conn)

                elif command == "create collection":
                    print()
                    create_collection(user_session, curs, conn)

                elif command == "rename collection":
                    print()
                    rename_collection(user_session, curs, conn)
                elif command == "total collections":
                    print()
                    total_collections(user_session, curs, conn)
                elif command == "view followers":
                    print()
                    view_followers(user_session, curs, conn)
                elif command == "view following":
                    view_followed(user_session, curs, conn)
                elif command == "view top 10 movies":
                    view_top_10(user_session, curs, conn)
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
delete collection- delete a collection
view collections - view all collections
create collection - create a collection
rename collection - rename a collection


PROFILE INFORMATION
total collections - view total number of collections
view followed - view number of users you follow
view followers - view number of followers you have
view top 10 - view top 10 movies based on rating, plays, or both
"""
    print(help_msg)
