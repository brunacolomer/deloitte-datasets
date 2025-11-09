from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn
import json
import numpy as np


app = FastAPI()

# Permitir peticiones desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o pon "http://localhost:5173" si usas Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/map")
async def get_map():
    with open("map.json", "r", encoding="utf-8") as f:
        map_data = json.load(f)
    return JSONResponse(content=map_data)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
