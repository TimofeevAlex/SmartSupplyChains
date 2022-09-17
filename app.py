import threading
import time
import streamlit as st
from queue import Queue
from google.cloud import firestore
import pandas as pd
import pydeck as pdk
from prepare_routes import prepare_routes


db = firestore.Client()
q = Queue()

routes = prepare_routes(True)
routes = pd.read_json(routes.to_json())

st.title('Smart Supply Chains')
st.subheader('Dashboard')

# create blank DataFrame
df_trip = pd.DataFrame(columns=['path', 'last_pos', 'icon_data', 'timestamps'], data=None)

ICON_URL = 'https://raw.githubusercontent.com/TimofeevAlex/ZurichHack/main/container.png'
icon_data = {
  "url": ICON_URL,
  "width": 128,
  "height": 128,
  "anchorY": 96,
  "anchorX": 64
}

icon_layer = pdk.Layer(
  'IconLayer',
  data=df_trip,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position="last_pos"
)


trip_layer = pdk.Layer(
    type="PathLayer",
    data=routes,
    pickable=True,
    get_color=[0, 256, 128],
    width_scale=20,
    width_min_pixels=2,
    get_path="path",
    get_width=5,
)

r = pdk.Deck(
  map_provider="mapbox",
  map_style='satellite',
  initial_view_state=pdk.ViewState(
    height=380,
    latitude=20,
    longitude=60,
    zoom=1.5,
    pitch=0,
  ),
  layers=[trip_layer, icon_layer], 
)
rt_map = st.pydeck_chart(r)

col2 = st.columns(1)[0]

col2.subheader('Alerts:')
with col2:
  snap = st.empty()

# Create a callback on_snapshot function to capture changes
def on_snapshot(col_snapshot, changes, read_time):
    
  doc_list = []
  for change in changes:
    doc = change.document.to_dict()
    doc['id'] = str(change.document.id)
    doc_list.append(doc)
  q.put(doc_list)

def main():
  col_ref = db.collection('connected')

  col_ref.on_snapshot(on_snapshot)

  df_trip = pd.DataFrame(columns=['path', 'last_pos', 'icon_data', 'timestamps'], data=None)
  while True:
    doc_list = q.get()

    for doc in doc_list:
      vehicle_ind = doc['id']

      try:
        _path = df_trip.at[vehicle_ind, 'path']
      except KeyError:
        _path = []
      _path.append(doc['lonlat'])
      df_trip.at[vehicle_ind, 'path'] = _path
      df_trip.at[vehicle_ind, 'last_pos'] = doc['lonlat']
      df_trip.at[vehicle_ind, 'icon_data'] = icon_data

      _timestamps = df_trip.at[vehicle_ind, 'timestamps']
      if type(_timestamps) != list:
        _timestamps = []
      _timestamps.append(doc['timestamp'])
      df_trip.at[vehicle_ind, 'timestamps'] = _timestamps

    snap.write(doc_list)
    # trip_layer.current_time = doc_list[-1]['timestamp']
    # trip_layer.data = df_trip
    icon_layer.data = df_trip
    r.update()
    rt_map.pydeck_chart(r)


if __name__ == "__main__":
  main()
