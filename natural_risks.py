from bs4 import BeautifulSoup
import requests
import polyline
from shapely.geometry import Polygon,Point,LineString
import warnings
warnings.filterwarnings('ignore')

def get_nature_risks():
    weather = []

    html = requests.get("https://severeweather.wmo.int/v2/json/").text
    soup = BeautifulSoup(html)
    for a in soup.find_all('a', href=True):
        # Parsing most of the files with information about weather in countries
        if a['href'].find('.json') != -1 and a['href'] not in ['fog.json', 'gale.json', 'hvyrain.json','thunderstorms.json',
                                                               'last24hrsCAP.json', 'nmhs.json', 'notInList.json',
                                                               'nowarning.json', 'sources.json', 'nmhs.json',
                                                                'usa_tornado.json'] and a['href'].find('tc_') == -1 and a['href'].find('wmo_') == -1:

            response = requests.get('https://severeweather.wmo.int/v2/json/'+a['href'])
            response.raise_for_status()
            jsonResponse = response.json()

            print('Processing file: ',a['href'])
            num_events=0

            for row in jsonResponse:
                if 'coord' in list(row.keys()):
                    severe=row['s']
                    geo=row['coord'][0]
                    if 'polygon' in geo.keys():
                        coords=[list(float(j) for j in i.split(',')) for i in row['coord'][0]['polygon'][0]]
                        weather.append((row['onset'],row['expires'],row['event'],Polygon(coords),Polygon(coords).centroid.x,Polygon(coords).centroid.y,severe))
                    elif 'geocode' in geo.keys():
                        s=''
                        if geo['geocode'][0][0]['type']=='Polygon':
                            for coord in geo['geocode'][0][0]['coordinates']:
                                s=s+coord
                        elif geo['geocode'][0][0]['type']=='MultiPolygon':
                            for coord in geo['geocode'][0][0]['coordinates']:
                                s=s+coord[0]
                        weather.append((row['onset'],row['expires'],row['event'],Polygon(polyline.decode(s)),Polygon(polyline.decode(s)).centroid.x,Polygon(polyline.decode(s)).centroid.y,severe))
                    num_events+=1

                    #weather [onset_time,expire_time,name,Polygon,centroid of the Polygon,severity]

            print('Number of weather conditions found: '+str(num_events))
        
        #Parsing information about thunderstorms
        elif a['href'] == 'thunderstorms.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            thunderstorms = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_storms = jsonResponse[key]
                    for storm in all_storms:
                        #thunderstorms [Datetime,lat,lon]
                        thunderstorms.append((key, float(storm[1]) / 100.0, float(storm[2]) / 100.0))
                        # df=pd.DataFrame(thunderstorms)
                        # df.to_csv('thunderstorms.csv',index=False)
            print('Number of thunderstorms found: '+str(len(thunderstorms)))
        #Parsing information about gales
        elif a['href'] == 'gale.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            gales = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_gales = jsonResponse[key]
                    for gale in all_gales:
                        #gales [Datetime, lat,lon]
                        gales.append((key, float(gale[1]) / 100.0, float(gale[2]) / 100.0))
                        # df=pd.DataFrame(gales)
                        # df.to_csv('gales.csv',index=False)
            print('Number of gales found: '+str(len(gales)))
        #Parsing infromation about fogs
        elif a['href'] == 'fog.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            fogs = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_fogs = jsonResponse[key]
                    for fog in all_fogs:
                        #fogs [Datetime, lat, lon]
                        fogs.append((key, float(fog[1]) / 100.0, float(fog[2]) / 100.0))
                        # df=pd.DataFrame(fogs)
                        # df.to_csv('fogs.csv',index=False)
            print('Number of fogs found: '+str(len(fogs)))
        #Parsing infromation about heavy rains
        elif a['href'] == 'hvyrain.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            hvyrains = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_hvyrains = jsonResponse[key]
                    for hvyrain in all_hvyrains:
                        #hvyrains [Datetime, lat, lon]
                        hvyrains.append((key, float(hvyrain[1]) / 100.0, float(hvyrain[2]) / 100.0))
            print('Number of heavy rains found: '+str(len(hvyrains)))
    return {"fogs": fogs, "hvyrains": hvyrains, "gales": gales, "thunderstorms": thunderstorms, 'weather':weather}

if __name__ == "__main__":
    natural_risks = get_nature_risks()