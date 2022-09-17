import pandas as pd
import numpy as np
import datetime
import random
import plotly.graph_objects as go


def preprocess_orders(df_bestellu, df_raw):
    df_raw = df_raw.drop_duplicates()
    df_raw = df_raw.dropna()
    df_bestellu = df_bestellu.drop_duplicates()
    df_bestellu = df_bestellu.dropna()
    dest_ports_to_analyse = ["Rotterdam", "Antwerpen", "Genoa", "La Spezia"]
    df_bestellu_plus_raw = df_bestellu.merge(df_raw, on="bestellnummer", how="inner")
    df_bestellu_plus_raw.loc[df_bestellu_plus_raw.pod_name.isin(dest_ports_to_analyse)]
    df_bestellu_plus_raw = df_bestellu_plus_raw.drop_duplicates(subset=['bestellnummer'])
    return df_bestellu_plus_raw


def preprocess_shiptrac(df_shiptrac):
    df_shiptrac['date_datetime'] = pd.to_datetime(df_shiptrac.date, dayfirst=True)
    df_shiptrac = df_shiptrac.sort_values(['imo_number', 'date_datetime'], ignore_index=True)
    df_shiptrac['long_diff'] = df_shiptrac.longitude - df_shiptrac.longitude.shift(fill_value=df_shiptrac.iloc[0].longitude)
    df_shiptrac['lat_diff'] = df_shiptrac.latitude - df_shiptrac.latitude.shift(fill_value=df_shiptrac.iloc[0].latitude)
    return df_shiptrac


def trip_match(imo_nr, date_start, date_finish, df_shiptrac):  
    date_start = pd.to_datetime(date_start, dayfirst=True)  
    date_finish = pd.to_datetime(date_finish, dayfirst=True) + datetime.timedelta(days=7)
    return df_shiptrac[(df_shiptrac.imo_number == imo_nr) & (df_shiptrac.date_datetime >= date_start) & (df_shiptrac.date_datetime <= date_finish)]


def prepare_routes(as_df=False):
    df_bestellu = pd.read_csv('data/gis_opex_international_bestellu.csv', sep=';', error_bad_lines=False)
    df_raw = pd.read_csv('data/gis_opex_international_raw.csv', sep=';', error_bad_lines=False)
    df_shiptrac = pd.read_csv('data/gis_opex_international_shiptrac.csv', sep=';', error_bad_lines=False)

    df_bestellu_plus_raw = preprocess_orders(df_bestellu, df_raw)
    df_shiptrac = preprocess_shiptrac(df_shiptrac)
    routes = []
    names = set()
    for ind in range(1, len(df_bestellu_plus_raw), 10):
        # Pipeline

        # Find routes ("imo_nr", "pol_name", "datum_abgang", "pod_name", "datum_ankunft", "bb_name")
        route_info = df_bestellu_plus_raw.iloc[ind][
            ["imo_nr", "pol_name", "datum_abgang", "pod_name", "datum_ankunft", "bb_name"]]
        res = trip_match(imo_nr=route_info.imo_nr, 
                         date_start=route_info.datum_abgang, 
                         date_finish=route_info.datum_ankunft, 
                         df_shiptrac=df_shiptrac)
        if len(res) == 0:
            continue

        if max(res.long_diff) > 15.0 or min(res.long_diff) < -15.0:
            continue

        if max(res.lat_diff) > 5.0 or min(res.lat_diff) < -5.0:
            continue

        long_lat = res[["longitude", "latitude"]].values

        # Annotate routes with in_danger
        in_danger = random.choice([True, False])
        desc = "Tyfoon risk" if in_danger else ""

        # Draw routes, drop duplicated routes
        if route_info.imo_nr not in names:
            names.add(route_info.imo_nr)
            route = {"path": long_lat, "in_danger": in_danger, "desc": desc, "name": route_info.imo_nr}
            routes.append(route)
    if as_df:
        routes_df = pd.DataFrame(columns=['name', 'path'])
        for route in routes:
            routes_df = routes_df.append({'name': route['name'], 'path': route['path']}, ignore_index=True)
        routes_df = routes_df.set_index('name')
        return routes_df
    return routes