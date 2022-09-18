import datetime
from google.cloud import firestore
from prepare_routes import get_routes_and_risks, get_current_routes_and_risks

db = firestore.Client()
db_paths = firestore.Client()

cur_datetime = datetime.datetime.now()
df_bestellu, df_shiptrac, df_bestellu_plus_raw, all_risks = get_routes_and_risks()
routes, upsampled_routes, risks = get_current_routes_and_risks(df_bestellu, df_shiptrac, df_bestellu_plus_raw,
                                                               all_risks, cur_datetime, upsample=True)

col_ref = db.collection('connected')
col_ref_paths = db_paths.collection('paths')
batch = db.batch()
batch_paths = db_paths.batch()

try:
    ts = 0
    max_ts = []
    for route in routes:
        max_ts.append(len(route['path']))
        for route_idx, route in enumerate(routes):
            doc_ref_paths = col_ref_paths.document(str(int(route['name'])))
            path_x = [x for x, _ in list(route['path'])]
            path_y = [y for _, y in list(route['path'])]
            batch_paths.set(doc_ref_paths, {
            'path_x': path_x,
            'path_y': path_y,
            'color': [190, 47, 43] if route['in_danger'] else [40, 163, 130],
            'in_danger': route['in_danger'],
            'desc': route['desc'],
            })
        batch_paths.commit()
    while True:
        ts += 1
        print(ts)
        for route_idx, route in enumerate(upsampled_routes if upsampled_routes else routes):
            curr_ts = ts % max_ts[route_idx]
            doc_ref = col_ref.document(str(int(route['name'])))
            doc_ref_paths = col_ref_paths.document(str(int(route['name'])))
            batch.set(doc_ref, {
                'lonlat': list(route['path'][curr_ts]),
                'timestamp': curr_ts
            })
        batch.commit()

except KeyboardInterrupt:
    pass