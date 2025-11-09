import plotly.graph_objects as go
import pandas as pd
import math
from geopy.distance import geodesic
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import minimize_scalar
file = pd.read_csv('datasets/lineas_fuzzy.csv')
poblacion = pd.read_csv('datasets/regions.csv', sep=';') 

w_dist = 0.2
w_conc = 0.3       
w_pobl = 0.3      
w_diff = 0.15

estacion_anterior_ganadora = None
scoreGanador = -math.inf
w_diff = 0.9 
 
linea_ganadora = None
scoreGanador = 0
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
print(f"La mejor estación es {linea_ganadora['estacion'].values[0]} con un score de {scoreGanador}")
print(linea_ganadora)
print(distanciasGanadoras)

def densityheatmap(distanciasGanadoras):
    dx, dy = 2,1
    x0, y0 = 2.1, 41.1
    xi = []
    yi = []
    d = []
    r = 1
    for regions in distanciasGanadoras:
        xi.append(regions["lon"])
        yi.append(regions["lat"])
        d.append(regions["poblacion"])

    xi = np.array(xi, dtype=float)
    yi = np.array(yi, dtype=float)
    d = np.array(d, dtype=float) 
    marge = 0.01  
    alpha = 5000
    angle_centre = np.arctan2(dy,dx)
    delta = np.deg2rad(90)
    angles =np.linspace(angle_centre -delta/2, angle_centre + delta/2, 200)
    x_arc = x0 + r * np.cos(angles)
    y_arc = y0 + r * np.sin(angles)
    def F(x, y):
        return np.sum(d * np.exp(-alpha * ((x - xi)**2 + (y - yi)**2)))

    def f_theta(theta):
        x = x0 + r * np.cos(theta)
        y = y0 + r * np.sin(theta)
        return -F(x, y)  # negatiu perquè minimize busca mínims
    x_min, x_max = xi.min() - marge, xi.max() + marge
    y_min, y_max = yi.min() - marge, yi.max() + marge
    res = minimize_scalar(f_theta, bounds=(angle_centre - delta/2, angle_centre + delta/2), method='bounded')
    theta_opt = res.x
    x_opt = x0 + r * np.cos(theta_opt)
    y_opt = y0 + r * np.sin(theta_opt)
    xv = np.linspace(x_min, x_max, 200)
    yv = np.linspace(y_min, y_max, 200)
    X, Y = np.meshgrid(xv, yv)
    Z = np.zeros_like(X)
    
    fig = px.scatter_map(lat=[41.2, 41.2], lon=[2.8, 2.5])
    fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=12,
            mapbox_center={"lat": 41.38, "lon": 2.16},
            margin={"r":0,"t":0,"l":0,"b":0}
    )
    #fig.show()
    fig = go.Figure()

    # Add first point
    fig.add_trace(go.Scattermap(
        lat=[y0], lon=[x0],
        mode='markers',
        marker=dict(size=12, color='red')
        ))

    # Add second point
    fig.add_trace(go.Scattermap(
        lat=[41.2], lon=[2.5],
        mode='markers',
        marker=dict(size=12, color='blue')
    ))
    fig.add_trace(go.Scattermap(
        lon=[x0, x0 + dx],
        lat=[y0, y0 + dy],
        mode='lines+markers',
        line=dict(color='lime', width=3),
        marker=dict(size=8, color='lime')
    ))
    fig.add_trace(go.Scattermap(
        lon=x_arc,
        lat=y_arc,
        mode='lines',
        line=dict(color='cyan', width=3),
        name='Arc'
    ))
    fig.add_trace(go.Densitymap(
        lat=yi,
        lon=xi,
        z=d,
        radius=20,         # controls blur size
        colorscale="Plasma",
        opacity=0.5,
        name="Densitat"
    ))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=12,
        mapbox_center={"lat": 41.38, "lon": 2.16},
        margin={"r":0,"t":0,"l":0,"b":0}
        )

    fig.show()
    print(x_opt, y_opt)

densityheatmap(distanciasGanadoras)





    




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
