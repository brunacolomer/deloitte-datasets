import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

const MapPlot = ({ weights }) => {
  const [fig, setFig] = useState({ data: [], layout: {} });
  const [loading, setLoading] = useState(false);
  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/reset_map");
      const rawData = await response.json();
      setFig({ data: rawData.data || [], layout: rawData.layout || {} });
    } catch (err) {
      console.error("Error cargando los datos del mapa:", err);
    } finally {
      setLoading(false);
    }
  };

  const addStation = async () => {
    try {
      setLoading(true);
      const payload = {
        w_dist: weights.w_dist,
        w_conc: weights.w_conc,
        w_pobl: weights.w_pobl,
        w_diff: weights.w_diff,
      };
      console.log(payload)
      const response = await fetch("http://localhost:8000/add_stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const rawData = await response.json();
      setFig({ data: rawData.data || [], layout: rawData.layout || {} });
    } catch (err) {
      console.error("Error cargando los datos del mapa:", err);
    } finally {
      setLoading(false);
    }
  };
  const fetchResetMap = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/reset");
      const rawData = await response.json();
      setFig({ data: rawData.data || [], layout: rawData.layout || {} });
      fetchData()
    } catch (err) {
      console.error("Error cargando los datos del mapa:", err);
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="map-wrapper">
      <Plot
        data={fig.data}
        layout={{ ...fig.layout, autosize: true, margin: { t: 10, b: 10, l: 10, r: 10 } }}
        style={{ width: "100%", height: "500px", borderRadius: "15px" }}
        config={{ responsive: true }}
      />
      <button className="refresh-btn" onClick={fetchData} disabled={loading}>
        {loading ? "Cargando..." : "Refrescar"}
      </button>
      <button className="refresh-btn" onClick={addStation} disabled={loading}>
        {loading ? "Cargando..." : "Add Station"}
      </button>
      <button className="reset-btn" onClick={fetchResetMap} disabled={loading}>
        {loading ? "Cargando..." : "Reset Stops"}
      </button>
    </div>
  );
};

export default MapPlot;
