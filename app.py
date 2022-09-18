import streamlit as st
from queue import Queue
from google.cloud import firestore
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

db = firestore.Client()
db_paths = firestore.Client()
q = Queue()
q_paths = Queue()

st.set_page_config(page_title="Smart Supply Chains", layout="wide", page_icon='letter-m.png')
# st.title('Smart Supply Chains')
st.subheader('Dashboard')
st.sidebar.title("Alerts")

# create blank DataFrame
df_trip = pd.DataFrame(columns=['path', 'last_pos', 'icon_data', 'timestamps'], data=None)
df_paths = pd.DataFrame(columns=['path',  'in_danger', 'color', 'desc'], data=None)

ICON_URL = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/container.png'
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
    data=df_paths,
    pickable=True,
    get_color="color",
    width_scale=20,
    width_min_pixels=2,
    get_path="path",
    get_width=5,
)

r = pdk.Deck(
  map_provider="mapbox",
  map_style='mapbox://styles/mapbox/streets-v11',
  api_keys={'mapbox':'pk.eyJ1IjoidGltb2ZlZXZhbGV4IiwiYSI6ImNsODZlNDY0NjB6NXMzcHMybnVlNmFnMDUifQ.Y_wyQ239E1hmfQrKlXA8Wg'},
  initial_view_state=pdk.ViewState(
    height=700,
    latitude=20,
    longitude=60,
    zoom=1.5,
    pitch=0,
  ),
  layers=[trip_layer, icon_layer], 
  height=1000
)
rt_map = st.pydeck_chart(r)

# col2 = st.columns(1)[0]

# col2.subheader('Alerts:')
# with col2:
#   snap = st.empty()


# Create a callback on_snapshot function to capture changes
def on_snapshot(col_snapshot, changes, read_time):
  doc_list = []
  for change in changes:
    doc = change.document.to_dict()
    doc['id'] = str(change.document.id)
    doc_list.append(doc)
  q.put(doc_list)
  
  
def on_snapshot_paths(col_snapshot, changes, read_time):
  doc_list = []
  for change in changes:
    doc = change.document.to_dict()
    doc['id'] = str(change.document.id)
    doc_list.append(doc)
  q_paths.put(doc_list)

def main():
  col_ref_paths = db_paths.collection('paths')
  col_ref = db.collection('connected')

  col_ref_paths.on_snapshot(on_snapshot_paths)
  col_ref.on_snapshot(on_snapshot)

  df_trip = pd.DataFrame(columns=['path', 'last_pos', 'icon_data', 'timestamps'], data=None)
  df_paths = pd.DataFrame(columns=['path', 'in_danger', 'color', 'desc'], data=None)

  
  while True:
    # Paths
    doc_list_paths = q_paths.get()
    for doc in doc_list_paths:
      path_ind = doc['id']
      df_paths.at[path_ind, 'path'] = [[x, y] for x, y in zip(doc['path_x'], doc['path_y'])]
      df_paths.at[path_ind, 'color'] = doc['color']
      df_paths.at[path_ind, 'desc'] = doc['desc']
      df_paths.at[path_ind, 'in_danger'] = doc['in_danger']
      if doc['in_danger']:
        st.sidebar.error(f'{path_ind}: ' + doc['desc'], icon="🚨") # TODO: Add time
    trip_layer.data = df_paths
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
    icon_layer.data = df_trip
    r.update()
    rt_map.pydeck_chart(r)


if __name__ == "__main__":
  main()
