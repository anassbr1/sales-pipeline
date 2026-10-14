import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ============================
# 1. CONFIG
# ============================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ============================
# 2. EXTRACT
# ============================
print("⏳ Lecture du CSV...")
df = pd.read_csv("data/online_retail_real.csv", encoding="utf-8-sig")
print(f"✅ {len(df)} lignes brutes chargées")

# ============================
# 3. TRANSFORM
# ============================
print("🧹 Nettoyage...")

# 3.1 Renommer les colonnes (espaces → underscore)
df.columns = ["invoice", "stock_code", "description", "quantity",
              "invoice_date", "price", "customer_id", "country"]

# 3.2 Convertir la date
df["invoice_date"] = pd.to_datetime(df["invoice_date"])

# 3.3 Supprimer les retours (Invoice commençant par 'C')
df = df[~df["invoice"].astype(str).str.startswith("C")]

# 3.4 Supprimer quantités négatives ou nulles
df = df[df["quantity"] > 0]

# 3.5 Supprimer prix négatifs ou nuls
df = df[df["price"] > 0]

# 3.6 Supprimer les Customer ID manquants
df = df.dropna(subset=["customer_id"])

# 3.7 Convertir customer_id en entier
df["customer_id"] = df["customer_id"].astype(int)

# 3.8 Ajouter colonne total_amount (CA par ligne)
df["total_amount"] = df["quantity"] * df["price"]

# 3.9 LOCALISATION MAROCAINE : remplacer Country par villes marocaines
import numpy as np
np.random.seed(42)
villes_maroc = ['Casablanca', 'Rabat', 'Marrakech', 'Fès',
                'Tanger', 'Agadir', 'Meknès', 'Oujda']
df["city"] = np.random.choice(villes_maroc, size=len(df))
df = df.drop(columns=["country"])

# 3.10 Supprimer les doublons
df = df.drop_duplicates()

print(f"✅ {len(df)} lignes après nettoyage")
print(f"   - Retours supprimés")
print(f"   - Quantités/prix négatifs supprimés")
print(f"   - CustomerID manquants supprimés")
print(f"   - Villes marocaines assignées")

# ============================
# 4. LOAD
# ============================
print("📤 Chargement dans PostgreSQL...")
df.to_sql(
    "sales_clean",
    engine,
    if_exists="replace",
    index=False,
    method="multi",
    chunksize=5000
)

print("✅ Table 'sales_clean' créée dans sales_db")

# ============================
# 5. VÉRIFICATION
# ============================
with engine.connect() as conn:
    result = pd.read_sql("SELECT COUNT(*) AS total FROM sales_clean", conn)
    print(f"🔍 Vérification : {result['total'][0]} lignes dans sales_clean")

# ============================
# 6. APPEL populate_star.py
# ============================
print("\n🚀 Lancement du schéma en étoile...")
import subprocess
subprocess.run(["python", "scripts/populate_star.py"], check=True)