// src/components/MapPlot.jsx
import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

const MapPlot = ({ weights }) => {
  const [fig, setFig] = useState({ data: [], layout: {} });
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/map");
      const rawData = await response.json();
      setFig({ data: rawData.data || [], layout: rawData.layout || {} });
    } catch (err) {
      console.error("Error cargando los datos del mapa:", err);
    } finally {
      setLoading(false);
    }
  };

  // Cuando cambien los pesos, los mandamos al backend y recargamos el mapa
  useEffect(() => {
    const updateWeights = async () => {
      try {
        await fetch("http://localhost:8000/weights", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(weights),
        });
        await fetchData();
      } catch (err) {
        console.error("Error actualizando pesos:", err);
      }
    };
    updateWeights();
  }, [weights]);

  return (
    <div className="map-wrapper">
      <Plot
        data={fig.data}
        layout={{
          ...fig.layout,
          autosize: true,
          margin: { t: 10, b: 10, l: 10, r: 10 },
        }}
        style={{
          width: "100%",
          height: "500px",
          borderRadius: "15px",
        }}
        config={{ responsive: true }}
      />
      <button
        className="refresh-btn"
        onClick={fetchData}
        disabled={loading}
      >
        {loading ? "Cargando..." : "Refrescar"}
      </button>
      <button
        className="refresh-btn"
        onClick={fetchData}
        disabled={loading}
      >
        {loading ? "Cargando..." : "Refrescar"}
      </button>
    </div>
  );
};

export default MapPlot;
