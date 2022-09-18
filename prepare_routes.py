import random
from collections import defaultdict
import copy
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
import haversine as hs
import requests
from NER_web import get_web_risks
from NER_twitter import get_twitter_risks
from bs4 import BeautifulSoup


def plot_routes(routes_to_plot, risks_to_plot):
    fig = go.Figure()

    for route in routes_to_plot:
        path, in_danger, desc, name = route["path"], route["in_danger"], route["desc"], route["name"]
        lons, lats, datetime = list(zip(*path))

        color = "red" if in_danger else "green"

        fig.add_trace(go.Scattermapbox(
            mode="markers+lines",
            lon=lons,
            lat=lats,
            fillcolor="blue",
            marker={'size': 10, "color": color},
            line=go.scattermapbox.Line(color=color),
            hovertext=desc if desc else None,
            name=name,
        ))

    for key, events in risks_to_plot.items():
        if len(events) == 0:
            continue
        events = np.array(events)

        fig.add_trace(go.Scattermapbox(
            mode="markers",
            lon=events[:, 2],
            lat=events[:, 1],
            fillcolor="blue",
            marker={'size': 10, "color": "black"},
            hovertext=key,
        ))

    fig.update_layout(
        margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
        mapbox={
            'center': {'lon': 10, 'lat': 10},
            'style': "stamen-terrain",
            'zoom': 1})

    fig.show()


def get_nature_risks():
    standard_fields = ['identifier', 'sent', 'url', 'description', 'event', 's', 'u', 'c', 'sn', 'effective', 'onset',
                       'expires', 'coord', 'areaDesc', 'mem']
    alll = []


    html = requests.get("https://severeweather.wmo.int/v2/json/").text
    soup = BeautifulSoup(html)
    for a in soup.find_all('a', href=True):
        if a['href'].find('.json') != -1 and a['href'] not in ['fog.json', 'gale.json', 'hvyrain.json',
                                                               'last24hrsCAP.json', 'nmhs.json', 'notInList.json',
                                                               'nowarning.json', 'sources.json', 'nmhs.json',
                                                               'thunderstorms.json', 'usa_tornado.json'] and a[
            'href'].find('tc_') == -1 and a['href'].find('wmo_') == -1:
            # #try:
            #     response = requests.get('https://severeweather.wmo.int/v2/json/'+a['href'])
            #     response.raise_for_status()
            #     jsonResponse = response.json()
            #     print(a['href'])
            #     i=0
            #     for row in jsonResponse:
            #         if 'coord' in list(row.keys()):
            #             severe=row['s']
            #             geo=row['coord'][0]
            #             if 'polygon' in geo.keys():
            #                 coords=[list(float(j) for j in i.split(',')) for i in row['coord'][0]['polygon'][0]]
            #                 alll.append((row['onset'],row['expires'],row['event'],Polygon(coords),Polygon(coords).centroid.x,Polygon(coords).centroid.y,severe))
            #             elif 'geocode' in geo.keys():
            #                 s=''
            #                 if geo['geocode'][0][0]['type']=='Polygon':
            #                     for coord in geo['geocode'][0][0]['coordinates']:
            #                         s=s+coord
            #                 elif geo['geocode'][0][0]['type']=='MultiPolygon':
            #                     for coord in geo['geocode'][0][0]['coordinates']:
            #                         s=s+coord[0]
            #                 alll.append((row['onset'],row['expires'],row['event'],Polygon(polyline.decode(s)),Polygon(polyline.decode(s)).centroid.x,Polygon(polyline.decode(s)).centroid.y,severe))
            #             i=i+1
            #     print(i)
            continue  # Currently, looking only at subset of nature risks
        elif a['href'] == 'thunderstorms.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            thunderstorms = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_storms = jsonResponse[key]
                    for storm in all_storms:
                        thunderstorms.append((key, float(storm[1]) / 100.0, float(storm[2]) / 100.0))
                        # df=pd.DataFrame(thunderstorms)
                        # df.to_csv('thunderstorms.csv',index=False)
        elif a['href'] == 'gale.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            gales = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_gales = jsonResponse[key]
                    for gale in all_gales:
                        gales.append((key, float(gale[1]) / 100.0, float(gale[2]) / 100.0))
                        # df=pd.DataFrame(gales)
                        # df.to_csv('gales.csv',index=False)
        elif a['href'] == 'fog.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            fogs = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_fogs = jsonResponse[key]
                    for fog in all_fogs:
                        fogs.append((key, float(fog[1]) / 100.0, float(fog[2]) / 100.0))
                        # df=pd.DataFrame(fogs)
                        # df.to_csv('fogs.csv',index=False)
        elif a['href'] == 'hvyrain.json':
            response = requests.get('https://severeweather.wmo.int/v2/json/' + a['href'])
            response.raise_for_status()
            jsonResponse = response.json()
            hvyrains = []
            for key in jsonResponse.keys():
                if key not in ['type', 'fields']:
                    all_hvyrains = jsonResponse[key]
                    for hvyrain in all_hvyrains:
                        hvyrains.append((key, float(hvyrain[1]) / 100.0, float(hvyrain[2]) / 100.0))
    return {"fogs": fogs, "hvyrains": hvyrains, "gales": gales, "thunderstorms": thunderstorms}


def get_human_risks():

    # risks from twitter
    # data = get_twitter_risks() - instead, we, currently, just parse hardcoded data
    data = {'#strike': {(46.603354, 1.8883335): 27,
                        (39.7837304, -100.445882): 12,
                        (45.9896587, -94.6113288): 23,
                        (47.6038321, -122.330062): 24},
            '#civilunrest': {},
            '#lockdown': {(35.000074, 104.999927): 71,
                          (17.8495919, 79.1151663): 29,
                          (22.3511148, 78.6677428): 15,
                          (42.4804953, 85.4633464): 19,
                          (31.2322758, 121.4692071): 12,
                          (10.2116702, 38.6521203): 17,
                          (30.6598628, 104.0633717): 12},
            '#war': {(49.4871968, 31.2718321): 272,
                     (64.6863136, 97.7453061): 294,
                     (35.000074, 104.999927): 24,
                     (39.7837304, -100.445882): 17,
                     (54.7023545, -3.2765753): 11,
                     (22.3511148, 78.6677428): 12,
                     (49.2160489, 37.3015645): 14,
                     (49.1913721, 37.2784125): 11,
                     (48.2083537, 16.3725042): 18},
            '#blackout': {(-36.8623103, 147.2748395): 69,
                          (36.7014631, -118.755997): 18,
                          (49.4871968, 31.2718321): 54,
                          (64.6863136, 97.7453061): 39},
            '#cyberattack': {
                (64.6863136, 97.7453061): 22,
                (39.7837304, -100.445882): 11}
            }

    # Add risks from the web
    data.update(get_web_risks())

    # Structure on the same way as nature risks
    data = {k: list(v.keys()) for k, v in data.items()}
    data = {k: list((None, lat, long) for (lat, long) in v) for k, v in data.items()}

    return data


def check_if_route_is_in_danger(path, risks, risk_title):
    DIST_THRESHOLD = 30  # km
    DAYS_THRESHOLD = 5  # days
    risks = np.array(risks)

    def normalise_lat_long(lat, long):
        lat = float(lat)
        long = float(long)
        while long < -180:
            long += 180
        while long > 180:
            long -= 180

        return lat, long

    for route_long, route_lat, route_datetime in path:  # Don't check to often
        route_lat_long = normalise_lat_long(lat=route_lat, long=route_long)

        for event in risks:
            event_datetime, event_lat, event_long = event
            event_lat_long = normalise_lat_long(event_lat, event_long)

            dist = hs.haversine(route_lat_long, event_lat_long)
            if event_datetime:
                event_date = datetime.datetime.strptime(event_datetime, "%Y%m%d%H%M%S").date()
                route_date = route_datetime.date()
                is_date_close = abs(event_date - route_date) < datetime.timedelta(days=DAYS_THRESHOLD)
            else:
                is_date_close = True
            if dist < DIST_THRESHOLD and is_date_close:
                # print(event_lat_long)
                return True, risk_title

    return False, ""


def preprocess_orders(df_bestellu, df_raw):
    df_raw = df_raw.drop_duplicates()
    df_raw = df_raw.dropna()
    df_bestellu = df_bestellu.drop_duplicates()
    df_bestellu = df_bestellu.dropna()
    dest_ports_to_analyse = ["Rotterdam", "Antwerpen", "Genoa",
                             "La Spezia"]  # Most frequently used ports (df_raw_trac.pod_name.value_counts())
    df_bestellu_plus_raw = df_bestellu.merge(df_raw, on="bestellnummer", how="inner")
    df_bestellu_plus_raw = df_bestellu_plus_raw.loc[df_bestellu_plus_raw.pod_name.isin(dest_ports_to_analyse)]
    df_bestellu_plus_raw = df_bestellu_plus_raw.drop_duplicates(subset=['bestellnummer'])

    df_bestellu_plus_raw['datum_abgang'] = pd.to_datetime(df_bestellu_plus_raw.datum_abgang, dayfirst=True)
    df_bestellu_plus_raw['datum_abgang'] = df_bestellu_plus_raw['datum_abgang'] + datetime.timedelta(weeks=52)

    df_bestellu_plus_raw['datum_ankunft'] = pd.to_datetime(df_bestellu_plus_raw.datum_ankunft, dayfirst=True)
    df_bestellu_plus_raw['datum_ankunft'] = df_bestellu_plus_raw['datum_ankunft'] + datetime.timedelta(weeks=52)
    return df_bestellu_plus_raw


def preprocess_shiptrac(df_shiptrac):
    df_shiptrac['date_datetime'] = pd.to_datetime(df_shiptrac.date, dayfirst=True)
    df_shiptrac['date_datetime'] = df_shiptrac['date_datetime'] + datetime.timedelta(
        weeks=52)  # artificially created data for current date
    df_shiptrac = df_shiptrac.sort_values(['imo_number', 'date_datetime'], ignore_index=True)
    df_shiptrac['long_diff'] = df_shiptrac.longitude - df_shiptrac.longitude.shift(
        fill_value=df_shiptrac.iloc[0].longitude)
    df_shiptrac['lat_diff'] = df_shiptrac.latitude - df_shiptrac.latitude.shift(fill_value=df_shiptrac.iloc[0].latitude)
    return df_shiptrac


def trip_match(imo_nr, date_start, date_finish, df_shiptrac):
    date_finish = date_finish + datetime.timedelta(days=3)
    return df_shiptrac[(df_shiptrac.imo_number == imo_nr) & (df_shiptrac.date_datetime >= date_start) & (
            df_shiptrac.date_datetime <= date_finish)]


def find_another_supplier(df_bestellu, route_info, desc):
    products_info = pd.DataFrame(df_bestellu.groupby("bb_name")["incoterms_ort"].apply(lambda x: np.unique(x))).reset_index()
    another_ports = products_info[products_info.bb_name == route_info.bb_name].incoterms_ort.values[0]
    list(another_ports).remove(route_info.incoterms_ort)
    if len(another_ports) != 0:
        desc = desc + "\n => Danger of delay in supply of the " + route_info.bb_name + "! Please, check other supply sources: " + '\n'.join(another_ports[:5])
    else:
        desc = desc + "\n => Danger of delay in supply of the " + route_info.bb_name + "! There are no other supply sources!"

    return desc


def get_current_risks():
    all_risks = get_nature_risks()
    human_risk_dict = get_human_risks()
    all_risks.update(human_risk_dict)
    for key in all_risks.keys():
        print(f"Analysed {len(all_risks[key])} {key} events")

    return all_risks


def get_routes_and_risks():
    df_bestellu = pd.read_csv('data/gis_opex_international_bestellu.csv', sep=';', error_bad_lines=False)
    df_raw = pd.read_csv('data/gis_opex_international_raw.csv', sep=';', error_bad_lines=False)
    df_shiptrac = pd.read_csv('data/gis_opex_international_shiptrac.csv', sep=';', error_bad_lines=False)

    df_bestellu_plus_raw = preprocess_orders(df_bestellu, df_raw)
    df_shiptrac = preprocess_shiptrac(df_shiptrac)
    all_risks = get_current_risks()

    return df_bestellu, df_shiptrac, df_bestellu_plus_raw, all_risks


def generate_risks(long_lat_datetime, n_risks=None):
    # Generate risks for particular route
    possible_risks_reasons = ["strike", "typhoon", "storm", "gales"]

    if not n_risks:
        n_risks = random.randint(15, 20)

    risks = defaultdict(list)
    for _ in range(n_risks):
        risk_reason = random.choice(possible_risks_reasons)
        if risk_reason in ["strike"]:
            risk_locations = [long_lat_datetime[0], long_lat_datetime[-1]]
        else:
            risk_locations = long_lat_datetime[0:-1]

        in_danger = random.choices([True, False], weights=[1, 5], k=1)[0]
        risk_location = random.choice(risk_locations)
        long, lat, risk_datetime = risk_location

        if in_danger:
            risks[risk_reason].append((risk_datetime.strftime(format="%Y%m%d%H%M%S"),
                                       lat + random.randint(-2, 2), long + random.randint(-2, 2)))
        else:
            risks[risk_reason].append((risk_datetime.strftime(format="%Y%m%d%H%M%S"),
                                   lat + random.randint(-30, 30), long + random.randint(-30, 30)))

    return risks


def get_current_routes_and_risks(df_bestellu, df_shiptrac, df_bestellu_plus_raw,
                                 all_risks, cur_datetime, simulate=False, upsample=False):
    routes = []
    upsampled_routes = []
    names = set()

    df_bestellu_plus_raw = df_bestellu_plus_raw[(df_bestellu_plus_raw.datum_ankunft >= cur_datetime) & (
            df_bestellu_plus_raw.datum_abgang <= cur_datetime)]

    print(f"There were {len(df_bestellu_plus_raw)} active shipments on {cur_datetime}")
    for ind in range(1, len(df_bestellu_plus_raw), 1):

        # Find routes ("imo_nr", "pol_name", "datum_abgang", "pod_name", "datum_ankunft", "bb_name")
        route_info = df_bestellu_plus_raw.iloc[ind][
            ["imo_nr", "pol_name", "datum_abgang", "pod_name", "datum_ankunft", "bb_name", "incoterms_ort"]]
        res = trip_match(imo_nr=route_info.imo_nr,
                         date_start=route_info.datum_abgang,
                         date_finish=route_info.datum_ankunft,
                         df_shiptrac=df_shiptrac)
        if len(res) == 0:
            continue

        if max(res.long_diff) > 30.0 or min(res.long_diff) < -30.0:
            continue

        if max(res.lat_diff) > 30.0 or min(res.lat_diff) < -30.0:
            continue

        long_lat_datetime = res[["longitude", "latitude", "date_datetime"]].values

        # Annotate routes with in_danger
        if simulate:
            all_risks = generate_risks(long_lat_datetime)

        in_danger = False
        desc = ""
        for key in all_risks.keys():
            if in_danger:  # Look for the closest risks
                break
            in_danger, desc = check_if_route_is_in_danger(long_lat_datetime, all_risks[key], risk_title=key)

        if in_danger:
            desc = find_another_supplier(df_bestellu=df_bestellu, route_info=route_info, desc=desc)

        # Draw routes, drop duplicated routes
        if route_info.imo_nr not in names:
            names.add(route_info.imo_nr)
            route = {"path": long_lat_datetime.tolist(), "in_danger": in_danger, "desc": desc, "name": f"Ship N{int(route_info.imo_nr)}"}
            if upsample:
                xs = [lon for lon, _, _ in route['path']]
                ys = [lat for _, lat, _ in route['path']]
                upsampled_path = []
                for i in range(1, len(xs)):
                    interp_x = np.linspace(xs[i - 1], xs[i], 5)
                    interp_y = np.linspace(ys[i - 1], ys[i], 5)
                    # interp_y = np.interp(interp_x, [xs[i - 1], xs[i]], [ys[i - 1], ys[i]])
                    upsampled_path.extend([[x, y] for x, y in zip(interp_x, interp_y)])
                upsampled_route = copy.deepcopy(route)
                upsampled_route['path'] = upsampled_path
                upsampled_routes.append(upsampled_route)
            routes.append(route)

    return routes, upsampled_routes, all_risks


if __name__ == "__main__":
    cur_datetime = datetime.datetime.now()
    df_bestellu, df_shiptrac, df_bestellu_plus_raw, all_risks = get_routes_and_risks()
    routes, upsampled_routes, risks = get_current_routes_and_risks(df_bestellu, df_shiptrac, df_bestellu_plus_raw, all_risks, cur_datetime, simulate=True)
    plot_routes(routes, risks)
