import plotly.graph_objects as go
import pandas as pd
import math
from geopy.distance import geodesic

file = pd.read_csv('datasets/lineas_fuzzy.csv')
poblacion = pd.read_csv('datasets/regions.csv', sep=';') 

w_dist = 0.2
w_conc = 0.3       
w_pobl = 0.3      
w_diff = 0.15 

estacion_anterior_ganadora = None
scoreGanador = -math.inf
distanciasGanadoras = []
first = True

for idx, fin in file[file['final'] == 1].iterrows():
    linea_actual = fin['linea']

    if first:
        estacion_anterior = file.iloc[idx + 1]
        first = False
    else:
        estacion_anterior = file.iloc[idx - 1]
        first = True

    lx = fin['lon']
    ly = fin['lat']

    distancias = []
    for region in poblacion.itertuples():
        distancia = geodesic((ly, lx), (region.lat, region.lon)).meters
        distancias.append({
            'distancia': distancia,
            'poblacion': region.densitat,
            'dificultad': region.dificultad,
            'lon': region.lon,
            'lat': region.lat
        })
    #ahora ordenamos segun distancia
    distancias.sort(key=lambda x: x['distancia'])
    distancias = distancias[:5] # me quedo con los 5 mas cercanos  

    scoreActual = 0

    distAux = 0
    poblAux= 0
    diffAux= 0

    for punt in distancias:
        distPond = (10000 - punt['distancia']) / (10000-500)
        distAux += distPond

        poblPond = (punt['poblacion'] - 10) / (1500-10)
        poblAux += poblPond

        diffPond = (100 - punt['dificultad']) / (100)
        diffAux += diffPond
    
    concPond = (fin['concurrencia'] - 100000) / (5000000-100000)
    distAux /= 5
    poblAux /= 5
    diffAux /= 5

    
    scoreActual = (w_dist * distAux) + (w_conc * concPond) + (w_pobl * poblAux) - (w_diff * diffAux)

    if scoreActual > scoreGanador:
        scoreGanador = scoreActual
        linea_ganadora = fin
        distanciasGanadoras = distancias
        estacion_anterior_ganadora = estacion_anterior
        direccio_lat = fin['lat'] - estacion_anterior['lat']
        direccio_lon = fin['lon'] - estacion_anterior['lon']

print(f"La mejor estación es {linea_ganadora['estacion']} con un score de {scoreGanador} i la estación anterior es {estacion_anterior_ganadora['estacion']}")



    




'''


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
'''