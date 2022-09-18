import datetime
import numpy as np
import pandas as pd
from google.cloud import firestore
from prepare_routes import get_routes_and_risks, get_current_routes_and_risks,get_nature_risks

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] ='C:/Users/tihon/Downloads/hackzurich22-4093-47107959b1ae.json'

db = firestore.Client()
db_paths = firestore.Client()
db_cats = firestore.Client()

# cur_datetime = datetime.datetime.now()
df_bestellu, df_shiptrac, df_bestellu_plus_raw, all_risks = get_routes_and_risks()
# routes, upsampled_routes, risks = get_current_routes_and_risks(df_bestellu, df_shiptrac, df_bestellu_plus_raw,
                                                            #    all_risks, cur_datetime, upsample=True)

col_ref = db.collection('connected')
col_ref_paths = db_paths.collection('paths')
col_ref_cats=db_cats.collection('cats')
batch = db.batch()
batch_paths = db_paths.batch()
batch_cats = db_cats.batch()

try:
    ts = 0
    offset_ts = []
    scale_ts = []
    while True:
        ts += 1
        print(ts)
        cur_datetime = datetime.datetime.now()
        routes, upsampled_routes, risks = get_current_routes_and_risks(df_bestellu, df_shiptrac, df_bestellu_plus_raw,
                                                                       all_risks, cur_datetime, upsample=True, simulate=True)
        if not offset_ts:
            offset_ts = [np.random.randint(0, len(route["path"])) for route in upsampled_routes if upsampled_routes else routes]
            scale_ts = [np.random.randint(1, 3) for route in upsampled_routes if upsampled_routes else routes]

        for route_idx, route in enumerate(routes):
            doc_ref_paths = col_ref_paths.document(route['name'])
            path_x = [x for x, _, _ in list(route['path'])]
            path_y = [y for _, y, _ in list(route['path'])]
            batch_paths.set(doc_ref_paths, {
            'path_x': path_x,
            'path_y': path_y,
            'color': [190, 47, 43] if route['in_danger'] else [40, 163, 130],
            'in_danger': route['in_danger'],
            'desc': route['desc'],
            })
        batch_paths.commit()
        max_ts = []
        for route in upsampled_routes if upsampled_routes else routes:
            max_ts.append(len(route['path']))
        for route_idx, route in enumerate(upsampled_routes if upsampled_routes else routes):
            curr_ts = (offset_ts[route_idx] + ts * scale_ts[route_idx] ) % max_ts[route_idx]
            doc_ref = col_ref.document(route['name'])
            doc_ref_paths = col_ref_paths.document(route['name'])
            batch.set(doc_ref, {
                'lonlat': list(route['path'][curr_ts]),
                'timestamp': curr_ts
            })
        batch.commit()

        
        doc_ref_cats=col_ref_cats.document("cats")

        #Natural
        fogs_lat=[]
        fogs_lng=[]
        for i in all_risks["fogs"]:
            fogs_lat.append(i[1])
            fogs_lng.append(i[2])

        gales_lat=[]
        gales_lng=[]
        for i in all_risks["gales"]:
            gales_lat.append(i[1])
            gales_lng.append(i[2])

        hvyrains_lat=[]
        hvyrains_lng=[]
        for i in all_risks["hvyrains"]:
            hvyrains_lat.append(i[1])
            hvyrains_lng.append(i[2])

        thunderstorms_lat=[]
        thunderstorms_lng=[]
        for i in all_risks["thunderstorms"]:
            thunderstorms_lat.append(i[1])
            thunderstorms_lng.append(i[2])

        #Twitter
        strike_lat=[]
        strike_lng=[]
        for i in all_risks["#strike"]:
            strike_lat.append(i[1])
            strike_lng.append(i[2])

        civilunrest_lat=[]
        civilunrest_lng=[]
        for i in all_risks["#civilunrest"]:
            civilunrest_lat.append(i[1])
            civilunrest_lng.append(i[2])

        lockdown_lat=[]
        lockdown_lng=[]
        for i in all_risks["#lockdown"]:
            lockdown_lat.append(i[1])
            lockdown_lng.append(i[2])

        war_lat=[]
        war_lng=[]
        for i in all_risks["#war"]:
            war_lat.append(i[1])
            war_lng.append(i[2])

        blackout_lat=[]
        blackout_lng=[]
        for i in all_risks["#blackout"]:
            blackout_lat.append(i[1])
            blackout_lng.append(i[2])

        cyberattack_lat=[]
        cyberattack_lng=[]
        for i in all_risks["#cyberattack"]:
            cyberattack_lat.append(i[1])
            cyberattack_lng.append(i[2])
        
        # embargo_lat=[]
        # embargo_lng=[]
        # for i in all_risks["#embargo"]:
        #     embargo_lat.append(i[1])
        #     embargo_lng.append(i[2])

        batch_cats.set(doc_ref_cats, {"timestamp":ts,
                                    "fogs_lat":fogs_lat,
                                    "fogs_lng":fogs_lng,
                                    "gales_lat":gales_lat,
                                    "gales_lng":gales_lng,
                                    "hvyrains_lat":hvyrains_lat,
                                    "hvyrains_lng":hvyrains_lng,
                                    "thunderstorms_lat" : thunderstorms_lat,
                                    "thunderstorms_lng" : thunderstorms_lng,
                                    "strike_lat":strike_lat,
                                    "strike_lng":strike_lng,
                                    "civilunrest_lat":civilunrest_lat,
                                    "civilunrest_lng":civilunrest_lng,
                                    "lockdown_lat":lockdown_lat,
                                    "lockdown_lng":lockdown_lng,
                                    "war_lat":war_lat,
                                    "war_lng":war_lng,
                                    "blackout_lat":blackout_lat,
                                    "blackout_lng":blackout_lng,
                                    "cyberattack_lat":cyberattack_lat,
                                    "cyberattack_lng":cyberattack_lng
                                    })

        batch_cats.commit()
except KeyboardInterrupt:
    pass