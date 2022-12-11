import spacy
from textblob import TextBlob
import tweepy
import re
from geopy.geocoders import Nominatim


def preprocess_tweet(sentence):
    '''Cleans text data up, leaving only 2 or more char long non-stepwords composed of A-Z & a-z only
    in lowercase'''

    # Remove RT
    sentence = re.sub('RT @\w+: ', " ", sentence)

    # Remove special characters
    sentence = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", sentence)

    # Single character removal
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ',
                      sentence)  # When we remove apostrophe from the word "Mark's", the apostrophe is replaced by an empty space. Hence, we are left with single character "s" that we are removing here.

    # Remove multiple spaces
    sentence = re.sub(r'\s+', ' ',
                      sentence)  # Next, we remove all the single characters and replace it by a space which creates multiple spaces in our text. Finally, we remove the multiple spaces from our text as well.

    return sentence


def get_twitter_risks():

    # Authentication to Twitter API
    consumerKey = "YourConsumerPublicKey"
    consumerSecret = "YourConsumerPrivateKey"
    bearToken = "YourBearToken"
    accessToken = "YourAppAccessToken"
    accessTokenSecret = "YourAppAccessTokenSecret"

    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    client = tweepy.Client(bearer_token=bearToken)

    # NER model: we use default model from spacy library
    beta = spacy.load("en_core_web_sm")

    # hashtags we use to retrieve data from Twitter
    hashtags = [
        'strike',
        'civilunrest',
        'lockdown',
        'war',
        'blackout',
        'cyberattack'
    ]

    # Number of tweets we retrieve
    max_results = 100
    limit = 10
    num = max_results * limit
    tweets = {}
    # Retrieve the tweets with given hashtag
    for hashtag in hashtags:
        query = '#' + hashtag + ' -is:retweet lang:en'
        paginator = tweepy.Paginator(
            client.search_recent_tweets,
            query=query,
            max_results=max_results,
            limit=limit
        )
        
        # Clean tweets before saving them
        cleaned_tweets = []
        for tweet in paginator.flatten():  # Total number of tweets to retrieve
            cleaned_tweets.append(preprocess_tweet(tweet.text))
        tweets[hashtag] = cleaned_tweets

    # Initialize Nominatim API for geo positions parcing
    geolocator = Nominatim(user_agent="MyApp")

    # Create places dictionary that consists from the problem (hashtag) and place
    places = {}
    for event in tweets.keys():
        places[event] = {}
        cleaned_tweets = tweets[event]
        for tweet in cleaned_tweets:
            # Check the sentiment of the tweet
            tb = TextBlob(tweet)
            score = tb.sentiment.polarity
            # if tweet is negative of neutral then we add the location to our pool
            if score <= 0:
                # NER is applied on top of the tweet to find the location
                doc = beta(tweet)
                loc = None
                for ent in doc.ents:
                    if ent.label_ == 'GPE':
                        loc = ent.text.lower()
                        try:
                            places[event][loc] += 1
                        except:
                            places[event][loc] = 1

        # delete irrelevent data: statistically insignificant places
        thrsh = int(num * 0.01)  # if number of mentions is less than 1% of tweets
        keys_to_del = []
        for key in places[event].keys():
            if places[event][key] <= thrsh:
                keys_to_del.append(key)
        for key in keys_to_del:
            del places[event][key]

        # change from city/country names to Longitude/Latitude
        new_keys = []
        for key in places[event].keys():
            location = geolocator.geocode(key)
            try:
                new_key = (location.latitude, location.longitude)
            except:
                new_key = None
            new_keys.append(new_key)

        old_keys = list(places[event].keys())
        for key, new_key in zip(old_keys, new_keys):
            val = places[event].pop(key)
            if new_key:
                places[event][new_key] = val

    return places


if __name__ == "__main__":
    data_twitter = get_twitter_risks()