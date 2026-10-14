import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# =====================================================
# 1. Créer les tables depuis le SQL
# =====================================================
print("⏳ Création du schéma en étoile...")
with open("sql/star_schema.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

with engine.begin() as conn:
    for statement in sql_script.split(";"):
        if statement.strip():
            conn.execute(text(statement))
print("✅ Tables créées")

# =====================================================
# 2. Charger sales_clean
# =====================================================
print("⏳ Lecture de sales_clean...")
df = pd.read_sql("SELECT * FROM sales_clean", engine)
if len(df) == 0:
    print("❌ Erreur : sales_clean est vide. Lance etl.py d'abord.")
    exit(1)
print(f"✅ {len(df)} lignes lues")

# =====================================================
# 3. DIM CUSTOMER
# =====================================================
print("📤 Remplissage dim_customer...")
dim_customer = df[["customer_id", "city"]].drop_duplicates(subset=["customer_id"]).copy()
dim_customer["customer_name"] = "Client_" + dim_customer["customer_id"].astype(str)
# Segment aléatoire (B2B / B2C / VIP) - simulé
np.random.seed(42)
dim_customer["segment"] = np.random.choice(
    ["B2C", "B2B", "VIP"], size=len(dim_customer), p=[0.7, 0.25, 0.05]
)
dim_customer.to_sql("dim_customer", engine, if_exists="append", index=False)
print(f"   → {len(dim_customer)} clients")

# =====================================================
# 4. DIM PRODUCT
# =====================================================
print("📤 Remplissage dim_product...")
dim_product = df[["stock_code", "description"]].drop_duplicates(subset=["stock_code"]).copy()
dim_product = dim_product.dropna(subset=["stock_code"])
dim_product.to_sql("dim_product", engine, if_exists="append", index=False)
print(f"   → {len(dim_product)} produits")

# =====================================================
# 5. DIM DATE
# =====================================================
print("📤 Remplissage dim_date...")
dates = pd.to_datetime(df["invoice_date"]).dt.normalize().drop_duplicates().sort_values()
dim_date = pd.DataFrame({
    "date_id": dates.dt.strftime("%Y%m%d").astype(int),
    "full_date": dates.dt.date,
    "year": dates.dt.year,
    "month": dates.dt.month,
    "month_name": dates.dt.strftime("%B"),
    "quarter": dates.dt.quarter,
    "day": dates.dt.day,
    "day_of_week": dates.dt.strftime("%A"),
    "is_weekend": dates.dt.dayofweek >= 5
})
dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
print(f"   → {len(dim_date)} dates")

# =====================================================
# 6. DIM CITY
# =====================================================
print("📤 Remplissage dim_city...")
regions_ma = {
    "Casablanca": "Casablanca-Settat",
    "Rabat": "Rabat-Salé-Kénitra",
    "Marrakech": "Marrakech-Safi",
    "Fès": "Fès-Meknès",
    "Tanger": "Tanger-Tétouan-Al Hoceïma",
    "Agadir": "Souss-Massa",
    "Meknès": "Fès-Meknès",
    "Oujda": "Oriental"
}
dim_city = pd.DataFrame([
    {"city_name": city, "region": region}
    for city, region in regions_ma.items()
])
dim_city.to_sql("dim_city", engine, if_exists="append", index=False)
print(f"   → {len(dim_city)} villes")

# =====================================================
# 7. FACT SALES
# =====================================================
print("📤 Remplissage fact_sales (patience ~1 min)...")

# Récupérer les IDs de dim_city
city_map = pd.read_sql("SELECT city_id, city_name FROM dim_city", engine)
city_map = dict(zip(city_map["city_name"], city_map["city_id"]))

fact = df[["invoice", "customer_id", "stock_code", "invoice_date",
           "city", "quantity", "price", "total_amount"]].copy()

# Convertir invoice_date → date_id
fact["date_id"] = pd.to_datetime(fact["invoice_date"]).dt.strftime("%Y%m%d").astype(int)
fact["city_id"] = fact["city"].map(city_map)
fact = fact.drop(columns=["invoice_date", "city"])

# Garder uniquement les FK valides
fact = fact[fact["customer_id"].notna()]
fact = fact[fact["stock_code"].notna()]

fact.to_sql("fact_sales", engine, if_exists="append", index=False, chunksize=5000)
print(f"✅ {len(fact)} lignes dans fact_sales")

print("\n🎉 Schéma en étoile prêt !")