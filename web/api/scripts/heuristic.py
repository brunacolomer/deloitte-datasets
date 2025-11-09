import math
import random
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from scipy.optimize import minimize_scalar
import plotly.graph_objects as go

# --- Archivos ---
url_lineas = "datasets/lineas_fuzzy.csv"
url_poblacion = "datasets/regions.csv"

# --- Lectura de datos ---
file = pd.read_csv(url_lineas)
poblacion = pd.read_csv(url_poblacion, sep=';')
poblacion = poblacion.rename(columns={"lon": "lon", "lat": "lat"})


# --- Función original calculate() ---
def calculate(w_dist=0.2, w_conc=0.3, w_pobl=0.3, w_diff=0.15):
    """
    Calcula la mejor estación según los pesos heurísticos
    y devuelve un JSON Plotly con la visualización.
    """
    file = pd.read_csv("datasets/lineas_fuzzy.csv")
    poblacion = pd.read_csv("datasets/regions.csv", sep=";")

    score_ganador = -math.inf
    estacion_anterior_ganadora = None
    linea_ganadora = None
    distancias_ganadoras = []

    first = True

    for idx, fin in file[file["final"] == 1].iterrows():
        if first:
            estacion_anterior = file.iloc[idx + 1]
            first = False
        else:
            estacion_anterior = file.iloc[idx - 1]
            first = True

        lx, ly = float(fin["lon"]), float(fin["lat"])

        distancias = []
        for region in poblacion.itertuples():
            distancia = geodesic((ly, lx), (float(region.lat), float(region.lon))).meters
            distancias.append({
                "distancia": float(distancia),
                "poblacion": float(region.densitat),
                "dificultad": float(region.dificultad),
                "lon": float(region.lon),
                "lat": float(region.lat),
            })

        distancias.sort(key=lambda x: x["distancia"])
        distancias = distancias[:5]

        distAux = poblAux = diffAux = 0
        for punt in distancias:
            distAux += (10000 - punt["distancia"]) / (10000 - 500)
            poblAux += (punt["poblacion"] - 10) / (1500 - 10)
            diffAux += (100 - punt["dificultad"]) / 100

        concPond = (float(fin["concurrencia"]) - 100000) / (5000000 - 100000)
        distAux /= 5
        poblAux /= 5
        diffAux /= 5

        score_actual = (w_dist * distAux) + (w_conc * concPond) + (w_pobl * poblAux) - (w_diff * diffAux)

        if score_actual > score_ganador:
            score_ganador = score_actual
            linea_ganadora = fin
            distancias_ganadoras = distancias
            estacion_anterior_ganadora = estacion_anterior

    # --- Generar figura Plotly ---
    fig = go.Figure()
    for linea, df_linea in file.groupby("linea"):
        fig.add_trace(
            go.Scattermapbox(
                lat=df_linea["lat"].astype(float).tolist(),
                lon=df_linea["lon"].astype(float).tolist(),
                mode="markers+lines",
                marker=dict(size=8),
                name=str(linea),
                text=df_linea["estacion"].astype(str).tolist(),
                hoverinfo="text",
                line=dict(width=4)
            )
        )

    if linea_ganadora is not None:
        fig.add_trace(
            go.Scattermapbox(
                lat=[float(linea_ganadora["lat"])],
                lon=[float(linea_ganadora["lon"])],
                mode="markers+text",
                marker=dict(size=14, color="gold", symbol="star"),
                text=["Nueva estación sugerida"],
                textposition="bottom right",
                name="Nueva parada"
            )
        )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=12,
        mapbox_center={"lat": 41.38, "lon": 2.16},
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig.to_plotly_json()


# --- Función para encontrar la mejor estación (find_best_end) ---
def find_best_end(w_dist=0.2, w_conc=0.3, w_pobl=0.3, w_diff=0.15):
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
                'distancia': distancia,
                'poblacion': region.densitat,
                'dificultad': region.dificultad,
                'lon': region.lon,
                'lat': region.lat
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

    print(f"La mejor estación es {linea_ganadora['estacion']} con score {score_ganador}, y la estación anterior es {estacion_anterior_ganadora['estacion']}")
    return linea_ganadora, distancias_ganadoras, estacion_anterior_ganadora, direccio_lat, direccio_lon


# --- Función para insertar parada ---
def insertar_parada(df, nueva_parada, parada_anterior):
    linea = nueva_parada["linea"]
    df_linea = df[df["linea"] == linea].copy().reset_index(drop=True)

    matches = df_linea[df_linea["estacion"] == parada_anterior["estacion"]]
    if matches.empty:
        print(f"No se encontró la parada {parada_anterior['estacion']} en la línea {linea}")
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
    df = pd.concat([df_restante, df_linea], ignore_index=True)
    df.to_csv(url_lineas, index=False)
    return df_linea


# --- Función para mostrar gráfico ---
def show_plot(file, x0, y0, dx, dy, x_arc, y_arc, x_opt, y_opt):
    fig = go.Figure()
    for linea, df_linea in file.groupby('linea'):
        fig.add_trace(go.Scattermapbox(
            lat=df_linea['lat'],
            lon=df_linea['lon'],
            mode='markers+lines',
            marker=dict(size=8),
            name=str(linea),
            text=df_linea['estacion'],
            line=dict(width=4)
        ))

    fig.add_trace(go.Scattermapbox(lat=[y0], lon=[x0], mode='markers', marker=dict(size=12, color='red')))
    fig.add_trace(go.Scattermapbox(lat=[y0, y0 + dy], lon=[x0, x0 + dx], mode='lines+markers', line=dict(color='lime', width=3), marker=dict(size=8, color='lime')))
    fig.add_trace(go.Scattermapbox(lat=y_arc, lon=x_arc, mode='lines', line=dict(color='cyan', width=3), name='Arc'))
    fig.add_trace(go.Scattermapbox(lat=[y_opt], lon=[x_opt], mode='markers', marker=dict(size=12, color='blue')))
    
    fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=12, mapbox_center={"lat": 41.38, "lon": 2.16},
                      margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


# --- Función principal para calcular nueva parada ---
def find_nova_parada():
    file = pd.read_csv(url_lineas)
    linea_ganadora, distanciasGanadoras, estacion_anterior_ganadora, dy, dx = find_best_end()

    x0, y0 = linea_ganadora.lon, linea_ganadora.lat
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

    nueva = pd.Series({
        "linea": linea_ganadora["linea"],
        "estacion": "NUEVA_PARADA" + str(random.randint(1,100000)),
        "concurrencia": 0,
        "final": 1,
        "lon": x_opt,
        "lat": y_opt
    })

    insertar_parada(file, nueva, linea_ganadora)
    show_plot(file, x0, y0, dx, dy, x_arc, y_arc, x_opt, y_opt)


if __name__ == "__main__":
    import json
    # JSON Plotly de la función calculate
    fig_json = calculate()
    print(json.dumps(fig_json, indent=2))
    # Encontrar nueva parada y mostrar mapa
    find_nova_parada()
