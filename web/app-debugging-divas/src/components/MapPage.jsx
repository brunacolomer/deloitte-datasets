import React, { useState, useRef } from "react";
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
  const debounceRef = useRef(null);

  const handleChangeLocal = (key, value) => {
    const newWeights = { ...weights, [key]: parseFloat(value) };
    setWeights(newWeights);

    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      // Nada aquí, MapPlot tomará los weights directamente
    }, 300);
  };

  const handleReset = () => {
    setWeights(default_weights);
    if (debounceRef.current) clearTimeout(debounceRef.current);
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
          Reset
        </button>
      </div>

      <div className="map-container">
        <MapPlot weights={weights} />
      </div>
    </div>
  );
};

export default MapPage;
