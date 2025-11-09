import plotly.graph_objects as go
import pandas as pd
from typing import Dict


def generate(csv_path: str = "datasets/lineas_fuzzy.csv"):
    # Diccionario de colores por línea
    colores: Dict[str, str] = {
        'L1': "#E41A1C",
        'L2': "#A91ED3",  
        'L3': "#389C34",  
        'L4': "#FFD61F",  
        'L5': "#0051FF",
        'L6': "#EB55FF",
        'L7': '#A65628',
        'L8': "#FF8DCA",  
        'L9N': "#FF9901",
        'L9S': "#FF9901",  
        'L10N': "#2FE7FF",
        'L10S': "#2FE7FF",
        'L11': "#74F320",
        'L13': "#FFFC2F" 
    }

    """
    Genera y devuelve un JSON con los datos de la figura Plotly.
    """
    try:
        file = pd.read_csv(csv_path)
    except Exception as e:
        raise RuntimeError(f"Error leyendo el CSV: {e}")

    fig = go.Figure()

    # Agrupar por línea y agregar cada una con su color
    for linea, df_linea in file.groupby("linea"):
        linea_str = str(linea)  # aseguramos string
        colorL = colores.get(linea_str, "#000000")  # default negro si no existe

        fig.add_trace(
            go.Scattermapbox(
                lat=df_linea["lat"].astype(float).tolist(),
                lon=df_linea["lon"].astype(float).tolist(),
                mode="markers+lines",
                marker=dict(size=10, color=colorL),
                line=dict(width=5, color=colorL),
                name=linea_str,
                text=df_linea["estacion"].astype(str).tolist(),
                hoverinfo="text"
            )
        )

    # Configuración del mapa
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=12,
        mapbox_center={"lat": 41.38, "lon": 2.16},
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig.to_plotly_json()


if __name__ == "__main__":
    import json
    fig_json = generate()
    print(json.dumps(fig_json, indent=2))
