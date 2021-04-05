from datetime import datetime, timedelta

import tweepy


def get_tweets_by_timedelta(api, username, days=0, hours=0):
    """
    Returns user's tweets between today and a delta time
    """
    max_date = datetime.utcnow() - timedelta(days=days, hours=hours)
    tweets_in_timedelta = []

    while True:
        tweets = tweepy.Cursor(api.user_timeline, id=username, exclude_replies=True, include_rts=False).items()

        for tweet in tweets:
            if tweet.created_at > max_date:
                tweets_in_timedelta.append(tweet)
            else:
                return tweets_in_timedelta


def get_crypto_symbols_in_tweet(tweet, crypto_symbols):
    """
    Returns list of tweet's symbols
    """
    symbols = []
    for symbol in tweet.entities.get("symbols"):
        symbol_id = symbol.get("text").upper()
        if symbol_id not in symbols and symbol_id in crypto_symbols:
            symbols.append(symbol_id)
    return symbols
