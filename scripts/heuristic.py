# scripts/heuristic.py
import pandas as pd
import math
from geopy.distance import geodesic
import numpy as np
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go
import plotly.express as px

<<<<<<< HEAD
def calcular_mejor_estacion(file_path='datasets/lineas_fuzzy.csv',
                             poblacion_path='datasets/regions.csv',
                             w_dist=0.2, w_conc=0.3, w_pobl=0.3, w_diff=0.15):
    file = pd.read_csv(file_path)
    poblacion = pd.read_csv(poblacion_path, sep=';')
=======
w_dist = 0.2
w_conc = 0.3       
w_pobl = 0.3      
w_diff = 0.15
>>>>>>> dce912676b91c61a019c9e5b51bb50a5e532a7af

    estacion_anterior_ganadora = None
    linea_ganadora = None
    scoreGanador = -math.inf
    distanciasGanadoras = []
    first = True

    for idx, fin in file[file['final'] == 1].iterrows():
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

        # Ordenar por distancia y quedarnos con los 5 más cercanos
        distancias.sort(key=lambda x: x['distancia'])
        distancias = distancias[:5]

        distAux = sum((10000 - d['distancia'])/(10000-500) for d in distancias)/5
        poblAux = sum((d['poblacion']-10)/(1500-10) for d in distancias)/5
        diffAux = sum((100 - d['dificultad'])/100 for d in distancias)/5
        concPond = (fin['concurrencia'] - 100000) / (5000000-100000)

        scoreActual = w_dist*distAux + w_conc*concPond + w_pobl*poblAux - w_diff*diffAux

        if scoreActual > scoreGanador:
            scoreGanador = scoreActual
            linea_ganadora = fin
            distanciasGanadoras = distancias
            estacion_anterior_ganadora = estacion_anterior

    return file, linea_ganadora, distanciasGanadoras, estacion_anterior_ganadora


def generar_heatmap(distanciasGanadoras, x0=2.1, y0=41.1, dx=2, dy=1, r=1):
    xi = np.array([d["lon"] for d in distanciasGanadoras])
    yi = np.array([d["lat"] for d in distanciasGanadoras])
    d = np.array([d["poblacion"] for d in distanciasGanadoras])

    marge = 0.01  
    alpha = 5000
    angle_centre = np.arctan2(dy, dx)
    delta = np.deg2rad(90)
    angles = np.linspace(angle_centre - delta/2, angle_centre + delta/2, 200)
    x_arc = x0 + r * np.cos(angles)
    y_arc = y0 + r * np.sin(angles)

    def F(x, y):
        return np.sum(d * np.exp(-alpha * ((x - xi)**2 + (y - yi)**2)))

    def f_theta(theta):
        x = x0 + r * np.cos(theta)
        y = y0 + r * np.sin(theta)
        return -F(x, y)

    res = minimize_scalar(f_theta, bounds=(angle_centre - delta/2, angle_centre + delta/2), method='bounded')
    theta_opt = res.x
    x_opt = x0 + r * np.cos(theta_opt)
    y_opt = y0 + r * np.sin(theta_opt)

    # Crear figura Plotly
    fig = go.Figure()
    fig.add_trace(go.Scattermap(
        lat=[y0], lon=[x0],
        mode='markers',
        marker=dict(size=12, color='red')
    ))
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
        radius=20,
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

<<<<<<< HEAD
    return fig, (x_opt, y_opt)
=======
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
>>>>>>> dce912676b91c61a019c9e5b51bb50a5e532a7af
