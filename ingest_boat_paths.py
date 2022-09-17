from google.cloud import firestore
from prepare_routes import prepare_routes

db = firestore.Client()
db_paths = firestore.Client()

routes, upsampled_routes = prepare_routes(upsample=True)
  
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
            'color': [256, 0, 128] if route['in_danger'] else [0, 256, 128],
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