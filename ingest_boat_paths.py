from google.cloud import firestore
from prepare_routes import prepare_routes

db = firestore.Client()

routes = prepare_routes()
  
col_ref = db.collection('connected')
batch = db.batch()

try:
    ts = 0
    max_ts = []
    for route in routes:
        max_ts.append(len(route['path']))
    while True:  
        ts += 1
        print(ts)
        for route_idx, route in enumerate(routes):
            curr_ts = ts % max_ts[route_idx]
            doc_ref = col_ref.document(str(int(route['name'])))
            # print(route['path'][:curr_ts].tolist())
            batch.set(doc_ref, {
            'lonlat': route['path'][curr_ts].tolist(),
            'timestamp': curr_ts
            })
        batch.commit()

except KeyboardInterrupt:
    pass