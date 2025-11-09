// src/pages/MapPage.jsx
import React, { useState, useEffect, useRef } from "react";
import MapPlot from "../components/MapPlot";

const default_weights = {
  w_dist: 0.2,
  w_conc: 0.3,
  w_pobl: 0.3,
  w_diff: 0.15,
};

const labels = {
  w_dist: "Weight Distance",
  w_conc: "Weight Concurrency",
  w_pobl: "Weight Density",
  w_diff: "Weight Difficulty",
};

const MapPage = () => {
  const [weights, setWeights] = useState(default_weights);
  const [figData, setFigData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Ref para almacenar el timer del debounce
  const debounceRef = useRef(null);

  const fetchMap = async (currentWeights) => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(currentWeights),
      });
      const data = await response.json();
      setFigData(data);
    } catch (err) {
      console.error("Error fetching map:", err);
    } finally {
      setLoading(false);
    }
  };

  // Primera carga
  useEffect(() => {
    fetchMap(weights);
  }, []);

  const handleChangeLocal = (key, value) => {
    const newWeights = { ...weights, [key]: parseFloat(value) };
    setWeights(newWeights);

    // Limpiar timer anterior si existía
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Crear nuevo timer para llamar al backend después de 300ms
    debounceRef.current = setTimeout(() => {
      fetchMap(newWeights);
    }, 300);
  };

  const handleReset = () => {
    setWeights(default_weights);

    // Cancelar debounce pendiente
    if (debounceRef.current) clearTimeout(debounceRef.current);

    fetchMap(default_weights);
  };

  return (
    <div className="map-page">
      <div className="controls">
        <h2>Heuristic Weights</h2>
        {Object.entries(weights).map(([key, value]) => (
          <div key={key} className="slider-container">
            <label>
              {labels[key]}: <strong>{value.toFixed(2)}</strong>
            </label>
           <input
  type="range"
  min="0"
  max="1"
  step="0.01"
  value={value}
  onChange={(e) => handleChangeLocal(key, e.target.value)}
  style={{
    background: `linear-gradient(to right, var(--secondary) 0%, var(--secondary) ${
      value * 100
    }%, #ddd ${value * 100}%, #ddd 100%)`,
  }}
/>

          </div>
        ))}
        <button className="reset-btn" onClick={handleReset}>
          {loading ? "Cargando..." : "Reset"}
        </button>
       
      </div>

      <div className="map-container">
        {figData && <MapPlot figData={figData} />}
      </div>
    </div>

  );
};

export default MapPage;
