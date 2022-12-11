from bs4 import BeautifulSoup
import requests
import re
import traceback
import spacy
from geopy.geocoders import Nominatim

def get_web_risks():

    # NER model: we use default model from spacy library
    beta = spacy.load("en_core_web_sm")

    def item_search(query):
        'Returns BS for the given query'

        # Sort search results by date
        params = {
            "pagesize": 10,
            "sort": "date",
            "direction": "DESC",
            'hl': 'en',
            'gl': 'us',
            'lr': 'lang_en',
        }
        # We take news only from trusted sources. In this setting we take news only from reuters.com
        news = f"https://www.google.com/search?q={query}+site%3Areuters.com"
        html = requests.get(news, params=params).text
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def get_details(url):
        'Returns text from the page given URL'

        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        for script in soup(["script", "style", 'aside', 'noscript', 'meta']):
            script.extract()
        return " ".join(re.split(r'[\n\t]+', soup.get_text()))

    def news_crawler(search_query):
        'Scrapping of pages given search query'

        links = []
        contents = []
        try:
            result = item_search(search_query)
            links = [x['href'][x['href'].find('https'):] for x in result.select('a') if '/url?q=' in x['href']]
            contents += [get_details(x[:x.index('&')]) for x in links]
        except Exception as e:
            traceback.print_exc()
        return contents

    # Topics for data
    queries = ['strike', 'cyber+attack', 'blackout', 'embargo', 'civil+unrest']
    contents = {}
    for query in queries:
        content = news_crawler(query)
        contents[query.replace('+', '')] = content
    
    # Initialize Nominatim API for geo positions parcing
    geolocator = Nominatim(user_agent="MyApp")

    # Create places dictionary that consists from the problem (topic of the news) and place
    places = {}
    for event in contents.keys():
        places[event] = {}
        content = contents[event]
        for c in content:
            # NER is applied on top of the news to find the relevant locations
            doc = beta(c)
            loc = None
            for ent in doc.ents:
                if ent.label_ == 'GPE':
                    loc = ent.text.lower()
                    try:
                        places[event][loc] += 1
                    except:
                        places[event][loc] = 1
        
        # delete irrelevent data: statistically insignificant places
        thrsh = 3 # Magic number
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
    data_web = get_web_risks()