import plotly.graph_objects as go
import pandas as pd

file = pd.read_csv('scripts/datasets/lineas_fuzzy.csv')

fig = go.Figure()

for linea, df_linea in file.groupby('linea'):
    
    fig.add_trace(go.Scattermapbox(
        lat=df_linea['lat'],
        lon=df_linea['lon'],
        mode='markers+lines',
        marker=dict(size=10),
        name=df_linea['linea'].iloc[0],
        text=df_linea['estacion'],
        hoverinfo='text',
        line=dict(width=5)
    ))

fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_zoom=12,
    mapbox_center={"lat": 41.38, "lon": 2.16},
    margin={"r":0,"t":0,"l":0,"b":0}
)

fig.show()
fig.write_json("map.json")
