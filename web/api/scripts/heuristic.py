import math
import pandas as pd
from geopy.distance import geodesic
import plotly.graph_objects as go

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


if __name__ == "__main__":
    import json
    fig_json = calculate()
    print(json.dumps(fig_json, indent=2))
