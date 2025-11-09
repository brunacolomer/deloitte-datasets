from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import math
import random
from geopy.distance import geodesic
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go

# --- Archivos ---
url_lineas = "datasets/lineas_fuzzy.csv"
url_poblacion = "datasets/regions.csv"

# --- Lectura inicial ---
file = pd.read_csv(url_lineas)
poblacion = pd.read_csv(url_poblacion, sep=';')
poblacion = poblacion.rename(columns={"lon": "lon", "lat": "lat"})

# --- FastAPI setup ---
app = FastAPI(title="Heuristic Map API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelo de pesos ---
class Weights(BaseModel):
    w_dist: float = 0.2
    w_conc: float = 0.3
    w_pobl: float = 0.3
    w_diff: float = 0.15

weights = Weights()

# --- Funciones base ---
def find_best_end(w_dist, w_conc, w_pobl, w_diff):
    score_ganador = -math.inf
    linea_ganadora = None
    distancias_ganadoras = []
    estacion_anterior_ganadora = None

    first = True

    for idx, fin in file[file['final'] == 1].iterrows():
        if first and idx + 1 < len(file):
            estacion_anterior = file.iloc[idx + 1]
            first = False
        else:
            estacion_anterior = file.iloc[idx - 1]
            first = True

        lx, ly = fin['lon'], fin['lat']

        distancias = []
        for region in poblacion.itertuples():
            distancia = geodesic((ly, lx), (region.lat, region.lon)).meters
            distancias.append({
                'distancia': float(distancia),
                'poblacion': float(region.densitat),
                'dificultad': float(region.dificultad),
                'lon': float(region.lon),
                'lat': float(region.lat)
            })

        distancias.sort(key=lambda x: x['distancia'])
        distancias = distancias[:5]

        distAux = poblAux = diffAux = 0
        for punt in distancias:
            distAux += (10000 - punt['distancia']) / (10000 - 500)
            poblAux += (punt['poblacion'] - 10) / (1500 - 10)
            diffAux += (100 - punt['dificultad']) / 100

        concPond = (fin['concurrencia'] - 100000) / (5000000 - 100000)
        distAux /= 5
        poblAux /= 5
        diffAux /= 5

        score_actual = (w_dist * distAux) + (w_conc * concPond) + (w_pobl * poblAux) - (w_diff * diffAux)

        if score_actual > score_ganador:
            score_ganador = score_actual
            linea_ganadora = fin
            distancias_ganadoras = distancias
            estacion_anterior_ganadora = estacion_anterior
            direccio_lat = fin['lat'] - estacion_anterior['lat']
            direccio_lon = fin['lon'] - estacion_anterior['lon']

    return linea_ganadora, distancias_ganadoras, estacion_anterior_ganadora, direccio_lat, direccio_lon

def insertar_parada(df, nueva_parada, parada_anterior):
    linea = nueva_parada["linea"]
    df_linea = df[df["linea"] == linea].copy().reset_index(drop=True)

    matches = df_linea[df_linea["estacion"] == parada_anterior["estacion"]]
    if matches.empty:
        return df_linea

    idx_anterior = matches.index[0]

    if idx_anterior == 0:
        df_linea = pd.concat([pd.DataFrame([nueva_parada]), df_linea], ignore_index=True)
    elif idx_anterior == len(df_linea) - 1:
        df_linea = pd.concat([df_linea, pd.DataFrame([nueva_parada])], ignore_index=True)

    df_linea["final"] = 0
    df_linea.at[df_linea.index[0], "final"] = 1
    df_linea.at[df_linea.index[-1], "final"] = 1

    df_restante = df[df["linea"] != linea]
    df_updated = pd.concat([df_restante, df_linea], ignore_index=True)
    df_updated.to_csv(url_lineas, index=False)
    return df_updated

def generate_map(df, nueva_parada=None, arc=None, opt=None):
    fig = go.Figure()
    for linea, df_linea in df.groupby('linea'):
        fig.add_trace(go.Scattermapbox(
            lat=df_linea['lat'].astype(float).tolist(),
            lon=df_linea['lon'].astype(float).tolist(),
            mode='markers+lines',
            marker=dict(size=8),
            name=str(linea),
            text=df_linea['estacion'].astype(str).tolist(),
            line=dict(width=4)
        ))

    if nueva_parada:
        fig.add_trace(go.Scattermapbox(
            lat=[float(nueva_parada['lat'])],
            lon=[float(nueva_parada['lon'])],
            mode='markers+text',
            marker=dict(size=14, color='gold', symbol='star'),
            text=[nueva_parada['estacion']],
            textposition="bottom right",
            name="Nueva parada"
        ))

    if arc and opt:
        fig.add_trace(go.Scattermapbox(lat=arc['y'], lon=arc['x'], mode='lines', line=dict(color='cyan', width=3), name='Arc'))
        fig.add_trace(go.Scattermapbox(lat=[opt['y']], lon=[opt['x']], mode='markers', marker=dict(size=12, color='blue')))

    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=12, mapbox_center={"lat": 41.38, "lon": 2.16},
                      margin={"r":0,"t":0,"l":0,"b":0})
    return fig.to_plotly_json()

# --- Endpoint para crear nueva parada usando heurística ---
@app.post("/add_stop")
def add_stop(w: Weights = weights):
    global file
    linea_ganadora, distanciasGanadoras, estacion_anterior_ganadora, dy, dx = find_best_end(
        w.w_dist, w.w_conc, w.w_pobl, w.w_diff
    )

    x0, y0 = linea_ganadora['lon'], linea_ganadora['lat']
    r = 0.007
    angle_centre = np.arctan2(dy, dx)
    delta = np.deg2rad(90)
    angles = np.linspace(angle_centre - delta/2, angle_centre + delta/2, 200)
    x_arc = x0 + r * np.cos(angles)
    y_arc = y0 + r * np.sin(angles)

    xi = np.array([reg["lon"] for reg in distanciasGanadoras])
    yi = np.array([reg["lat"] for reg in distanciasGanadoras])
    d = np.array([reg["poblacion"] for reg in distanciasGanadoras])
    alpha = 5000

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

    nueva = {
        "linea": linea_ganadora["linea"],
        "estacion": "NUEVA_PARADA_" + str(random.randint(1,100000)),
        "concurrencia": 0,
        "final": 1,
        "lon": float(x_opt),
        "lat": float(y_opt)
    }

    file = insertar_parada(file, nueva, linea_ganadora)

    arc_data = {'x': x_arc.tolist(), 'y': y_arc.tolist()}
    opt_data = {'x': float(x_opt), 'y': float(y_opt)}

    return generate_map(file, nueva_parada=nueva, arc=arc_data, opt=opt_data)

# --- Endpoint para obtener mapa actual ---
@app.get("/map")
def get_map():
    return generate_map(file)
