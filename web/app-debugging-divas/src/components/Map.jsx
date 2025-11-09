import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";

// Decodifica los bdata a array de floats
function decodeBData(bdata) {
  try {
    const binary = atob(bdata);
    const buffer = new ArrayBuffer(binary.length);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < binary.length; i++) {
      view[i] = binary.charCodeAt(i);
    }
    const floatArray = new Float64Array(buffer);
    return Array.from(floatArray);
  } catch (err) {
    console.error("Error decodificando bdata:", err);
    return [];
  }
}

const MapPlot = () => {
  const [fig, setFig] = useState({ data: [], layout: {} });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/api/map");
      const rawData = await response.json();

      if (!rawData.data || !Array.isArray(rawData.data)) {
        console.error("No se encontró la propiedad 'data' o no es un array");
        setLoading(false);
        return;
      }

      // Transformar datos del mapa
      const transformedData = rawData.data.map((trace) => ({
        ...trace,
        lat: trace.lat?.bdata ? decodeBData(trace.lat.bdata) : [],
        lon: trace.lon?.bdata ? decodeBData(trace.lon.bdata) : [],
      }));

      setFig({ data: transformedData, layout: rawData.layout || {} });

      // Preparar datos para el gráfico: número de estaciones por línea
      const chart = transformedData.map(trace => ({
        name: trace.name,
        value: trace.text ? trace.text.length : 0
      }));
      setChartData(chart);

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
    <div className="app-container">
      <div className="content-wrapper">
        <div className="map-wrapper">
          <Plot
            data={fig.data}
            layout={{
              ...fig.layout,
              autosize: true,
              margin: { t: 20, b: 20, l: 20, r: 20 },
            }}
            style={{ width: "100%", height: "600px", borderRadius: "15px" }}
            config={{ responsive: true }}
          />
          <button
            className="refresh-btn"
            onClick={fetchData}
            disabled={loading}
          >
            {loading ? "Cargando..." : "Refresh"}
          </button>
        </div>

              </div>
    </div>
  );
};

export default MapPlot;
