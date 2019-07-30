#!/usr/bin/env python3
"""It's current_year"""

import os
import html
import datetime
from typing import List

import tweepy

class CurrentYear:
    """Twitter API wrapper"""

    def __init__(self, api: tweepy.API) -> None:
        self.api = api
        self.tweets: List[tweepy.models.Status] = []
        self.update_tweet_candidates()

    @staticmethod
    def _criteria(tweet: tweepy.models.Status) -> bool:
        """
        This shouldn't be necessary because we filter on the API level,
        but it is.
        """
        if "RT" in tweet.text or "t.co" in tweet.text \
            or len(tweet.text) > 240 or tweet.retweeted:
            return False
        return True

    def _log_status(self, tweet: tweepy.models.Status) -> None:
        text = "\"{}\" from @{} at {} UTC ({} left)" \
                .format(html.unescape(tweet.text), tweet.user.screen_name,
                        tweet.created_at, len(self.tweets))
        print(text)

    def _update(self, tweet: tweepy.models.Status) -> None:
        self._log_status(tweet)
        self.api.retweet(tweet.id)

    def update_tweet_candidates(self) -> None:
        """Searches for tweets"""
        year = datetime.datetime.now().year
        pattern = f"\"it\'s {year}\" -filter:retweets -filter:links"
        for tweet in self.api.search(q=pattern, lang="en", count=100):
            if tweet not in self.tweets and self._criteria(tweet):
                self.tweets.append(tweet)

    def retweet(self) -> None:
        """Generate and tweet"""
        tweet = self.tweets.pop()
        try:
            self._update(tweet)
        except tweepy.error.TweepError:
            self._log_status(tweet)
            raise

def main() -> None:
    """Entry point"""
    auth = tweepy.OAuthHandler(os.environ["API_KEY"], os.environ["API_SECRET"])
    auth.set_access_token(os.environ["ACCESS_TOKEN"],
                          os.environ["ACCESS_TOKEN_SECRET"])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    current_year = CurrentYear(api)
    current_year.retweet()

if __name__ == "__main__":
    main()
