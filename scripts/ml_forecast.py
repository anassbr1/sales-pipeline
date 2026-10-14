import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

load_dotenv()
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# =====================================================
# 1. Agrégation mensuelle par ville
# =====================================================
print("⏳ Agrégation des ventes mensuelles...")
query = """
SELECT d.year, d.month, c.city_name,
       SUM(f.total_amount) AS ca
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_city c ON f.city_id = c.city_id
GROUP BY d.year, d.month, c.city_name
ORDER BY c.city_name, d.year, d.month
"""
df = pd.read_sql(query, engine)
print(f"✅ {len(df)} lignes d'agrégation mensuelle")

df["time_index"] = df.groupby("city_name").cumcount() + 1

# =====================================================
# 2. Entraînement par ville — Random Forest
# =====================================================
print("\n🤖 Entraînement des modèles (Random Forest)...")
resultats = []
predictions_futures = []

for city in df["city_name"].unique():
    city_df = df[df["city_name"] == city].sort_values("time_index").reset_index(drop=True)

    if len(city_df) < 12:
        print(f"⚠️ {city} : pas assez de données, ignoré")
        continue

    city_df["month_sin"] = np.sin(2 * np.pi * city_df["month"] / 12)
    city_df["month_cos"] = np.cos(2 * np.pi * city_df["month"] / 12)

    X = city_df[["time_index", "month_sin", "month_cos"]].values
    y = city_df["ca"].values

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=6,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    resultats.append({
        "city": city,
        "mae": round(mae, 2),
        "r2": round(r2, 3),
        "nb_mois": len(X)
    })

    # Prédire 6 mois futurs
    last_index = city_df["time_index"].max()
    last_month = int(city_df["month"].iloc[-1])

    future_rows = []
    for i in range(1, 7):
        future_month = ((last_month + i - 1) % 12) + 1
        future_rows.append({
            "time_index": last_index + i,
            "month_sin": np.sin(2 * np.pi * future_month / 12),
            "month_cos": np.cos(2 * np.pi * future_month / 12),
            "mois_futur": i,
            "mois_calendaire": future_month
        })

    future_df = pd.DataFrame(future_rows)
    future_X = future_df[["time_index", "month_sin", "month_cos"]].values
    future_y = model.predict(future_X)

    for i, row in future_df.iterrows():
        predictions_futures.append({
            "city_name": city,
            "mois_futur": int(row["mois_futur"]),
            "mois_calendaire": int(row["mois_calendaire"]),
            "ca_predit": round(float(future_y[i]), 2)
        })

resultats_df = pd.DataFrame(resultats)
print("\n📊 Performance des modèles :")
print(resultats_df.to_string(index=False))

# =====================================================
# 3. Sauvegarder (IDEMPOTENT : DROP puis CREATE)
# =====================================================
print("\n📤 Sauvegarde dans sales_forecast...")
pred_df = pd.DataFrame(predictions_futures)

# ⚠️ ÉTAPE CLÉ : on supprime la table AVANT d'insérer
# → jamais de doublons, même si le script tourne 100 fois
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS sales_forecast"))

pred_df.to_sql("sales_forecast", engine, if_exists="replace", index=False)
print(f"✅ {len(pred_df)} prédictions → table sales_forecast (sans doublons)")

print("\n🎉 Prévisions terminées !")