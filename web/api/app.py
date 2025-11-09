from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scripts.heuristic import calculate
from scripts.paintmap import generate

app = FastAPI(title="Heuristic Map API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por la URL de tu front
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pesos iniciales
weights = {
    "w_dist": 0.2,
    "w_conc": 0.3,
    "w_pobl": 0.3,
    "w_diff": 0.15
}

class Weights(BaseModel):
    w_dist: float
    w_conc: float
    w_pobl: float
    w_diff: float

@app.get("/map")
def get_map():
    """
    Devuelve el mapa completo sin modificar pesos.
    """
    fig_json = generate()
    return fig_json

@app.post("/calculate")
def post_calculate(new_weights: Weights):
    """
    Calcula la mejor estación según los pesos enviados
    y devuelve el mapa actualizado.
    """
    calculate(
        w_dist=new_weights.w_dist,
        w_conc=new_weights.w_conc,
        w_pobl=new_weights.w_pobl,
        w_diff=new_weights.w_diff
    )
    fig_json = generate()
    return fig_json

@app.post("/weights")
def update_weights(new_weights: Weights):
    """
    Actualiza los pesos globales (opcional para persistencia)
    """
    weights.update({
        "w_dist": new_weights.w_dist,
        "w_conc": new_weights.w_conc,
        "w_pobl": new_weights.w_pobl,
        "w_diff": new_weights.w_diff
    })
    fig_json = calculate(
        w_dist=new_weights.w_dist,
        w_conc=new_weights.w_conc,
        w_pobl=new_weights.w_pobl,
        w_diff=new_weights.w_diff
    )
    return fig_json

