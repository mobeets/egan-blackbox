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
        embed_info = handle.get_oembed_tweet(id=tweet['id'])
        tweet['html'] = embed_info['html']
        tweet['url'] = embed_info['url']

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

def print_as_html(infile, outfile):
    fname, ext = os.path.splitext(outfile)
    tweets = json.load(open(infile))
    head = '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><html><head></head><body>'
    head += "<h1>Jennifer Egan's <i>Black Box</i></h1>\n"
    head += """<i>A short story serialized on twitter by <a href="https://twitter.com/nyerfiction">@NYerFiction</a> between May 24, 2012 - June 2, 2012.</i><br>\n"""
    tail = '<br></body></html>'
    indices = sorted(tweets, key=lambda key: int(key))
    for index in indices:
        ts = tweets[index]
        content = ''
        content += '<h2>Chapter {0}</h2>\n'.format(index)
        for tweet in ts:
            content += '{0}\n'.format(tweet['html'].encode('utf-8'))
        out = head + content + tail
        outfile = fname + '_' + index + ext
        open(outfile, 'w').write(out)

def print_as_txt(infile, outfile):
    tweets = json.load(open(infile))
    out = '-----------------------------\n'
    out += "Jennifer Egan's Black Box\n"
    out += '-----------------------------\n'
    out += "A short story serialized on twitter by @NYerFiction between May 24, 2012 - June 2, 2012.\n\n"
    indices = sorted(tweets, key=lambda key: int(key))
    for index in indices:
        ts = tweets[index]
        out += '------------\n'
        out += 'Chapter {0}\n'.format(index)
        out += '------------\n'
        for tweet in ts:
            out += '{0}\n'.format(tweet['text'].encode('utf-8'))
        out += '\n'
    open(outfile, 'w').write(out)

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

def main(outfile='blackbox.json', min_index=None):
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
    # main()
    print_as_html('blackbox.json', 'blackbox.html')
    # print_as_txt('blackbox.json', 'blackbox.txt')
