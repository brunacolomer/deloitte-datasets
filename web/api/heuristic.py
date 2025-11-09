import plotly.graph_objects as go
import pandas as pd
import math
from geopy.distance import geodesic

file = pd.read_csv('scripts/datasets/lineas_fuzzy.csv')
poblacion = pd.read_csv('scripts/datasets/regions.csv', sep=';') 


w_dens = 0.5       
w_conc = 0.3       
w_diff = 0.15      
w_cerca = 0.05     

radio_dens = 500
radio_diff = 500
radio_cerca = 300





for linea, df_linea in file.groupby('linea'):
    distancias = []
    fin = df_linea[df_linea['final'] == 1]
    if fin.empty or len(df_linea) < 2:
        continue
    
    lx = fin['lon'].values[0]
    ly = fin['lat'].values[0]

    for region in poblacion:
        distancia = geodesic((ly, lx), (poblacion['lat'], poblacion['lon'])).meters
        distancias.append(distancia)
        print(distancia)









fig = go.Figure()

for linea, df_linea in file_mod.groupby('linea'):
    fig.add_trace(go.Scattermapbox(
        lat=df_linea['lat'],
        lon=df_linea['lon'],
        mode='markers+lines',
        marker=dict(size=8),
        name=f"{linea}",
        text=df_linea['estacion'],
        hoverinfo='text',
        line=dict(width=4)
    ))


fig.add_trace(go.Scattermapbox(
    lat=[mejor['lat']],
    lon=[mejor['lon']],
    mode='markers+text',
    marker=dict(size=14, color='gold', symbol='star'),
    text=["Nueva estación sugerida"],
    textposition='bottom right',
    name='Nueva parada'
))

fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_zoom=12,
    mapbox_center={"lat": 41.38, "lon": 2.16},
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig.show()
fig.write_json("map.json")
