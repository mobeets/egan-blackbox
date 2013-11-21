import os
import json
from twython import Twython

from story import screen_name, tweet_ranges

from dotenv import Dotenv
environ = Dotenv('.env')
# environ = os.environ

CONSUMER_KEY = environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = environ['TWITTER_CONSUMER_SECRET']
OAUTH_TOKEN = environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = environ['TWITTER_OAUTH_TOKEN_SECRET']
TWEET_LENGTH = 140

def twitter_handle():
    return Twython(CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def add_html_to_embed(handle, tweets):
    """
    Embedded tweet example:
    <blockquote class="twitter-tweet" lang="en"><p>HELLO WORLD</p>&mdash; New Yorker Fiction (@NYerFiction) <a href="https://twitter.com/NYerFiction/statuses/206177088045199361">May 26, 2012</a></blockquote>
    <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
    """
    for tweet in tweets:
        tweet['html'] = handle.get_oembed_tweet(id=tweet['id'])['html'] # ['url']

def tweets_in(handle, start_id, end_id):    
    tweets = handle.get_user_timeline(screen_name=screen_name,
        exclude_replies=True,
        count=200,
        since_id=start_id, # note this is not inclusive
        max_id=end_id)
    tweet = handle.show_status(id=start_id)
    tweets.append(tweet)
    add_html_to_embed(handle, tweets)
    return tweets

def save_to_json(tweets, outfile):
    json.dump(tweets, open(outfile, 'w'))
    
def get_out_while_you_still_can(tweets, outfile):
    fname, ext = os.path.splitext(outfile)
    indices = [str(i) for i in sorted(tweets.keys())]
    if not indices:
        print 'No tweets saved.'
        return
    print 'Saving tweets from indices {0}'.format(', '.join(indices))
    outfile = fname + '_' + '-'.join(indices) + ext
    save_to_json(tweets, outfile)

def main(outfile='tmp.json', min_index=4):
    handle = twitter_handle()
    tweets = {}
    no_errors = True
    for row in tweet_ranges:
        if min_index and row['index'] < min_index:
            continue
        assert row['index'] not in tweets
        print 'Fetching tweets in index {0}...'.format(row['index'])
        try:
            tweets[row['index']] = tweets_in(handle, row['tweet_start_id'], row['tweet_end_id'])
        except:
            get_out_while_you_still_can(tweets, outfile)
            no_errors = False
            break
    if no_errors:
        save_to_json(tweets, outfile)
        print 'All tweets saved.'

if __name__ == '__main__':
    main()
