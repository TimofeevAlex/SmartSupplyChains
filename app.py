import streamlit as st
from queue import Queue
from google.cloud import firestore
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt


db = firestore.Client(project='hackzurich-369916')
db_paths = firestore.Client(project='hackzurich-369916')
db_cats= firestore.Client(project='hackzurich-369916')
q = Queue()
q_paths = Queue()
q_cats = Queue()

st.set_page_config(page_title="Smart Supply Chains", layout="wide", page_icon='icons/letter-m.png')
# st.title('Smart Supply Chains')
st.subheader('Dashboard')
st.sidebar.title("Alerts")

# create blank DataFrame
df_trip = pd.DataFrame(columns=['path', 'last_pos', 'icon_data', 'timestamps'], data=None)
df_paths = pd.DataFrame(columns=['path',  'in_danger', 'color', 'desc'], data=None)
df_fogs = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_gales = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_hvyrains = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_thunderstorms = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_strike = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_civilunrest = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_lockdown = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_war = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_blackout = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_cyberattack = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
df_embargo = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)


ICON_URL = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/container.png'
icon_data = {
  "url": ICON_URL,
  "width": 128,
  "height": 128,
  "anchorY": 96,
  "anchorX": 64
}

URL_fogs = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/fog.png'
URL_gales = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/gale.png'
URL_hvyrains = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/hvrain.png'
URL_thunderstorms = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/typhoon.png'
URL_strike = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/strike.png'
URL_civilunrest = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/civilunrest.jpg'
URL_lockdown = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/lockdown.png'
URL_war = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/war.png' 
URL_blackout = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/blackout.png'
URL_cyberattack = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/cyberattack.png'
URL_embargo = 'https://raw.githubusercontent.com/TimofeevAlex/SmartSupplyChains/main/icons/embargo.png'

icon_data_fogs={"url":URL_fogs,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_gales={"url":URL_gales,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_hvyrains={"url":URL_hvyrains,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_thunderstorms={"url":URL_thunderstorms,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_strike={"url":URL_strike,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_civilunrest={"url":URL_civilunrest,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_lockdown={"url":URL_lockdown,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_war={"url":URL_war,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_blackout={"url":URL_blackout,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_cyberattack={"url":URL_cyberattack,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}
icon_data_embargo={"url":URL_embargo,"width": 64,"height": 64,"anchorY": 96,"anchorX": 64}

fogs_layer = pdk.Layer(
  'IconLayer',
  data=df_fogs,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

gales_layer = pdk.Layer(
  'IconLayer',
  data=df_gales,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

hvyrains_layer = pdk.Layer(
  'IconLayer',
  data=df_hvyrains,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)
thunderstorms_layer = pdk.Layer(
  'IconLayer',
  data=df_thunderstorms,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

strike_layer = pdk.Layer(
  'IconLayer',
  data=df_strike,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)
civilunrest_layer = pdk.Layer(
  'IconLayer',
  data=df_civilunrest,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

lockdown_layer = pdk.Layer(
  'IconLayer',
  data=df_lockdown,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)
war_layer = pdk.Layer(
  'IconLayer',
  data=df_war,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)
blackout_layer = pdk.Layer(
  'IconLayer',
  data=df_blackout,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

cyberattack_layer = pdk.Layer(
  'IconLayer',
  data=df_cyberattack,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

embargo_layer = pdk.Layer(
  'IconLayer',
  data=df_embargo,
  pickable=True,
  get_icon='icon_data',
  get_size=4,
  size_scale=12,
  get_position=["lat","lng"]
)

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
  layers=[trip_layer, 
          icon_layer, 
          fogs_layer,
          gales_layer,
          hvyrains_layer,
          thunderstorms_layer,
          strike_layer,
          civilunrest_layer,
          lockdown_layer,
          war_layer,
          blackout_layer,
          cyberattack_layer,
          embargo_layer], 
  height=1000
)
rt_map = st.pydeck_chart(r)

# col2 = st.columns(1)[0]



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

def on_snapshot_cats(col_snapshot, changes, read_time):
  doc_list = []
  for change in changes:
    doc = change.document.to_dict()
    doc['id'] = str(change.document.id)
    doc_list.append(doc)
  q_cats.put(doc_list)

def main():
  col_ref_paths = db_paths.collection('paths')
  col_ref = db.collection('connected')
  col_ref_cats=db_cats.collection('cats')

  col_ref_paths.on_snapshot(on_snapshot_paths)
  col_ref.on_snapshot(on_snapshot)
  col_ref_cats.on_snapshot(on_snapshot_cats)

  df_trip = pd.DataFrame(columns=['path', 'last_pos', 'icon_data', 'timestamps'], data=None)
  df_paths = pd.DataFrame(columns=['path', 'in_danger', 'color', 'desc'], data=None)
  df_fogs = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_gales = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_hvyrains = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_thunderstorms = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_strike = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_civilunrest = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_lockdown = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_war = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_blackout = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_cyberattack = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)
  df_embargo = pd.DataFrame(columns=['lat','lng','icon_data'], data=None)

  
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
    # Boats
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

      #Catastrophs
    doc_list_cats = q_cats.get()
    for doc in doc_list_cats:
      #cat_ind = doc['id']
      df_fogs['lat']=doc["fogs_lat"]
      df_fogs['lng']=doc["fogs_lng"]
      df_fogs['icon_data']=[icon_data_fogs]*len( df_fogs['lng'])
      df_gales['lat']=doc["gales_lat"]
      df_gales['lng']=doc["gales_lng"]
      df_gales['icon_data']=[icon_data_gales]*len( df_gales['lng'])
      df_hvyrains['lat']=doc["hvyrains_lat"]
      df_hvyrains['lng']=doc["hvyrains_lng"]
      df_hvyrains['icon_data']=[icon_data_hvyrains]*len( df_hvyrains['lng'])
      df_thunderstorms['lat']=doc["thunderstorms_lat"]
      df_thunderstorms['lng']=doc["thunderstorms_lng"]
      df_thunderstorms['icon_data']=[icon_data_thunderstorms]*len( df_thunderstorms['lng'])
      df_strike['lat']=doc["strike_lat"]
      df_strike['lng']=doc["strike_lng"]
      df_strike['icon_data']=[icon_data_strike]*len( df_strike['lng'])
      df_civilunrest['lat']=doc["civilunrest_lat"]
      df_civilunrest['lng']=doc["civilunrest_lng"]
      df_civilunrest['icon_data']=[icon_data_civilunrest]*len( df_civilunrest['lng'])
      df_lockdown['lat']=doc["lockdown_lat"]
      df_lockdown['lng']=doc["lockdown_lng"]
      df_lockdown['icon_data']=[icon_data_lockdown]*len( df_lockdown['lng'])
      df_war['lat']=doc["war_lat"]
      df_war['lng']=doc["war_lng"]
      df_war['icon_data']=[icon_data_war]*len(df_war['lng'])
      df_blackout['lat']=doc["blackout_lat"]
      df_blackout['lng']=doc["blackout_lng"]
      df_blackout['icon_data']=[icon_data_blackout]*len(df_blackout['lng'])
      df_cyberattack['lat']=doc["cyberattack_lat"]
      df_cyberattack['lng']=doc["cyberattack_lng"]
      df_cyberattack['icon_data']=[icon_data_cyberattack]*len(df_cyberattack['lng'])
      df_embargo['lat']=doc["embargo_lat"]
      df_embargo['lng']=doc["embargo_lng"]
      df_embargo['icon_data']=[icon_data_embargo]*len(df_embargo['lng'])
    
      fogs_layer.data = df_fogs
      gales_layer.data = df_gales
      hvyrains_layer.data = df_hvyrains
      thunderstorms_layer.data = df_thunderstorms
      strike_layer.data = df_strike
      civilunrest_layer.data = df_civilunrest
      lockdown_layer.data = df_lockdown
      war_layer.data = df_war
      blackout_layer.data = df_blackout
      cyberattack_layer.data = df_cyberattack
      embargo_layer.data = df_embargo


if __name__ == "__main__":
  main()
