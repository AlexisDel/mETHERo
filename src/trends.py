import asyncio
import aiocron
import tweepy

from collections import Counter
from datetime import timedelta, datetime
from pathlib import Path
from tqdm import tqdm

from utils import coingecko
from utils import database
from utils import twitter
from config import api_keys

# Constants
MAX_PROCESSING_TIME_FOR_TRENDS_SCAN = 50  # In minutes (must be < 45 to respect (free) Twitter API limitations)
DATA_DIRECTORY_PATH = "../data"
TRENDS_DIRECTORY_PATH = "../trends"


@aiocron.crontab('0 * * * *')
def get_trends():
    # Twitter authentication
    auth = tweepy.OAuthHandler(api_keys.TWITTER_CONSUMER_KEY, api_keys.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(api_keys.TWITTER_ACCESS_TOKEN, api_keys.TWITTER_ACCESS_TOKEN_SECRET)
    TwitterAPI = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=False)

    # CoinGecko listed coins
    crypto_symbols = coingecko.get_crypto_symbols_from_CoinGecko()

    # Get users to scan from "users.txt"
    users_to_scan = database.get_users_id_from_file(Path(DATA_DIRECTORY_PATH + "/users.txt"))

    # Main loop
    crypto_trends = Counter()
    start_time = datetime.now()

    scanned_tweets = 0
    users_bar = tqdm(users_to_scan, postfix={"Tweets": scanned_tweets}, leave=True,
                     desc="Getting CT Trends (" + (datetime.now() - timedelta(hours=1)).strftime(
                         "%H") + "h-" + datetime.now().strftime("%H") + "h" + ") ",
                     bar_format="{l_bar}{bar}| [Time: {elapsed}, Users={n_fmt}/{total_fmt}{postfix}]")
    for user in users_bar:
        try:
            tweets = twitter.get_tweets_by_timedelta(TwitterAPI, user, hours=1)
            for tweet in tweets:
                tags = twitter.get_crypto_symbols_in_tweet(tweet, crypto_symbols)
                crypto_trends.update(tags)

                scanned_tweets += 1
                users_bar.set_postfix({"Tweets": scanned_tweets})  # Update number of scanned tweets displayed

        except Exception as e:
            pass

        if datetime.now() > start_time + timedelta(minutes=MAX_PROCESSING_TIME_FOR_TRENDS_SCAN):
            print("Max scanning time exceeded")  # For monitoring purpose
            break

    # Write hourly trends
    scan_time = datetime.now() - timedelta(hours=1)
    dir_path = Path(
        TRENDS_DIRECTORY_PATH + "/twitter/" + scan_time.strftime("%Y") + '/' + scan_time.strftime(
            "%B") + '/' + scan_time.strftime(
            "%d"))

    dir_path.mkdir(parents=True, exist_ok=True)
    database.write_trends_in_file(crypto_trends, dir_path)


asyncio.get_event_loop().run_forever()
