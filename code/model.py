# --- 📦 Importar librerías ---
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt

# --- 1️⃣ Cargar los datos ---
densidad_df = pd.read_csv("csv/Densitat Poblacio Barcelona 2021.csv", encoding="latin-1")
transport_df = pd.read_csv("csv/Transport Public Barcelona.csv", encoding="latin-1")

# --- 2️⃣ Preparar los datos de densidad ---
densidad_full = densidad_df[[
    "Codi_Barri", "Nom_Barri", "Població", "Superfície (ha)", "Densitat neta (hab/ha)"
]].copy()

densidad_full.rename(columns={
    "Codi_Barri": "BARRI",
    "Nom_Barri": "NOM_BARRI",
    "Superfície (ha)": "Superficie",
    "Densitat neta (hab/ha)": "Densitat_neta"
}, inplace=True)

# --- 3️⃣ Calcular número de transportes por barrio ---
transportes_por_barri = transport_df.groupby("BARRI").size().reset_index(name="Num_transportes")

# --- 4️⃣ Combinar datasets ---
modelo_df = pd.merge(densidad_full, transportes_por_barri, on="BARRI", how="left")
modelo_df["Num_transportes"].fillna(0, inplace=True)

# --- 5️⃣ Variables independientes (X) y dependiente (y) ---
X = modelo_df[["Població", "Superficie", "Densitat_neta"]]
y = modelo_df["Num_transportes"]

# --- 6️⃣ Entrenar modelo de regresión lineal ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

# --- 7️⃣ Evaluación ---
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"R² del modelo: {r2:.3f}")
print(f"Error medio absoluto (MAE): {mae:.2f}")

# --- 8️⃣ Predicciones completas ---
modelo_df["Pred_Transportes"] = model.predict(X)
modelo_df["Deficit"] = modelo_df["Pred_Transportes"] - modelo_df["Num_transportes"]

# --- 9️⃣ Mostrar los barrios con mayor déficit ---
barrios_deficit = modelo_df.sort_values(by="Deficit", ascending=False)
print("\nTop 10 barrios con mayor déficit de transporte:")
print(barrios_deficit[["BARRI", "NOM_BARRI", "Població", "Superficie", "Densitat_neta",
                       "Num_transportes", "Pred_Transportes", "Deficit"]].head(10))

# --- 🔟 Visualización de la relación real vs predicha ---
plt.figure(figsize=(8,6))
plt.scatter(modelo_df["Num_transportes"], modelo_df["Pred_Transportes"], alpha=0.7)
plt.plot([0, max(y)], [0, max(y)], color="red", linestyle="--")
plt.title("Transportes reales vs predichos por el modelo")
plt.xlabel("Transportes reales")
plt.ylabel("Transportes predichos")
plt.grid(True)
plt.show()
