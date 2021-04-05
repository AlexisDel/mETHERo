import tweepy

from os import path
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from utils import coingecko


def get_usernames_from_file(filename):
    """
    Returns a list of usernames from file
    """
    usernames = []
    try:
        file = open(filename, 'r')
        for user in file.readlines():
            usernames.append((user.strip()))
        file.close()

    except Exception:
        pass

    return usernames


def get_users_id_from_file(filepath):
    """
    Returns a list of id from file
    """
    user_ids = []
    try:
        file = open(filepath, 'r')
        for user in file.readlines():
            user_ids.append((int(user.strip())))
        file.close()

    except Exception:
        pass

    return user_ids


def write_users_list_in_file(filename, users):
    """
    Writes usernames on each line in file
    """
    file = open(filename, 'w')
    for user in users:
        file.write(str(user) + "\n")
    file.close()


def read_trends_from_file(filepath):
    """
    Returns trends dict from trends file
    """
    trends_dict = {}
    file = open(filepath, "r")
    for line in file.readlines():
        splited_line = line.split(" ")
        trends_dict[splited_line[0]] = int(splited_line[1].strip())
    file.close()
    return trends_dict


def write_trends_in_file(crypto_trends, dir_path):
    """
    Write crypto trends dict in a text file
    """
    scan_time = datetime.now() - timedelta(hours=1)
    path = dir_path / (scan_time.strftime("%H") + ".txt")

    with path.open('w') as file:
        for crypto in crypto_trends:
            file.write(str(crypto) + " " + str(crypto_trends.get(crypto)) + '\n')
        file.close()


def trends_from_timedelta(delta):
    trends = Counter()

    for i in range(delta):
        try:
            file_datetime = datetime.now() - timedelta(hours=i + 2)
            local_trends = read_trends_from_file(
                Path("../trends/twitter/" + file_datetime.strftime("%Y") + '/' + file_datetime.strftime(
                    "%B") + '/' + file_datetime.strftime("%d") + "/" + file_datetime.strftime("%H") + ".txt"))

            # Update global trends dict
            for crypto in local_trends:
                trends.update({crypto: local_trends.get(crypto)})

        except FileNotFoundError:
            pass

    return trends.most_common()


def trends_to_percent(trends):
    trends_percent = []
    sum_occurrences = sum(occurrence for crypto, occurrence in trends)
    for crypto, occurrence in trends:
        trends_percent.append((crypto, (occurrence / sum_occurrences * 100)))
    return trends_percent


def get_trends(timedelta, inout=None, top=None):
    return trends_to_percent(coingecko.filter_by_MC(trends_from_timedelta(timedelta), inout, top))


def get_hot_trends(timedelta, limit, inout=None, top=None):
    trends = get_trends(timedelta, inout, top)
    hot_trends = []
    for crypto, percent in trends:
        if percent > limit:
            hot_trends.append((crypto, percent))
    return hot_trends


def add_username_to_database(api, username):
    try:
        user = api.get_user(username)
        users_id = get_users_id_from_file(path.abspath("../data/users.txt"))

        if user.id not in users_id:
            file = open(path.abspath("../data/users.txt"), "a")
            file.write(user.id_str + '\n')
            file.close()
            return '\"' + user.screen_name + '\"' + " a été ajouté à la base de données"
        else:
            return '\"' + user.screen_name + '\"' + " est déjà dans la base de données"

    except tweepy.error.TweepError as e:
        if e.api_code == 50:
            return "Utilisateur introuvable"
        if e.api_code == 63:
            return "Utilisateur banni"
        else:
            return str(e)


def add_user_followers_to_database(api, username):
    try:
        user = api.get_user(username)
        user_ids = get_users_id_from_file(path.abspath("../data/users.txt"))

        user_followers_id = api.friends_ids(id=user.id_str)
        number_of_followers = len(user_followers_id)
        user_followers_id = map(str, user_followers_id)

        file = open(path.abspath("../data/users.txt"), "a")
        for user_id in user_followers_id:
            if user_id not in user_ids:
                file.write(user_id + '\n')
        file.close()
        return "Tous les followers de " + '\"' + user.screen_name + '\"' + " ont été ajoutés à la base de données, soit " + str(
            number_of_followers) + "  utilisateurs"

    except tweepy.error.TweepError as e:
        if e.api_code == 50:
            return "Utilisateur introuvable"
        if e.api_code == 63:
            return "Utilisateur banni"
        else:
            return str(e)
