from movies.auth import (
    create_account,
    login
)
from movies.user import (
    follow,
    unfollow,
    view_followed,
    view_followers,
    view_profile, 
    view_top_20_movies_among_users,
    recommend_movies,
)

from movies.movie import (
    watch_movie,
    watch_collection,
    rate_movie,
    search,
    view_top_10,
    view_top_20_last_90_days,
    view_top_5_new_releases
)

from movies.collection import (
    add_to_collection,
    remove_from_collection,
    delete_collection,
    view_collections,
    create_collection,
    rename_collection,
    total_collections,
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
            command = command.strip()
            if command == "create account":
                create_account(user_session, curs, conn)

            if command == "login":
                login(user_session, curs, conn)
                if user_session["loggedIn"] == True: 
                    help()

            while user_session["loggedIn"]:
                print()
                command = input("Enter a command: (Enter 'help' to see commands) \n").strip()

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

                elif command == "view followed":
                    print()
                    view_followed(user_session, curs, conn)

                elif command == "view followers":
                    print()
                    view_followers(user_session, curs, conn)

                elif command == "view profile": 
                    print() 
                    view_profile(user_session, curs, conn)

                elif command == "view top 10 movies":
                    print()
                    view_top_10(user_session, curs, conn)

                elif command == "view top 20 (last 90 days)":
                    print()
                    view_top_20_last_90_days(curs, conn)

                elif command == "view top 20 (among users)":
                    print()
                    view_top_20_movies_among_users(user_session, curs, conn)

                elif command == "view top 5 new releases":
                    print()
                    view_top_5_new_releases(curs, conn)
                elif command == "view profile":
                    print()
                    view_profile(user_session, curs, conn)
                elif command == "view movie rec":
                    print()
                    recommend_movies(user_session, curs, conn)
                elif command == "help": 
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
delete collection- delete a collection
view collections - view all collections
create collection - create a collection
rename collection - rename a collection


PROFILE INFORMATION
view profile - view users profile

TOP MOVIES
view top 20 (last 90 days) - view top 20 most popular movies in the last 90 days
view top 20 (among users) - view the top 20 most popular movies among users followed by the current user
view top 5 new releases - view the top 5 new releases of the month (calendar month)
view movie rec - view recommended movies to watch to based on your play history (e.g. genre, cast member, rating) and the play history of similar users
"""
    print(help_msg)
