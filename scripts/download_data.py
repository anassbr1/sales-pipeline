import kagglehub
import pandas as pd
import shutil
import os

print("⏳ Téléchargement depuis Kaggle...")

# Télécharger le dataset
path = kagglehub.dataset_download("mashlyn/online-retail-ii-uci")
print(f"✅ Téléchargé dans : {path}")

# Trouver le fichier CSV
csv_file = None
for file in os.listdir(path):
    if file.endswith('.csv'):
        csv_file = os.path.join(path, file)
        break

if csv_file is None:
    raise FileNotFoundError("Aucun CSV trouvé dans le dossier téléchargé")

# Charger et sauvegarder dans data/
df = pd.read_csv(csv_file, encoding='ISO-8859-1')

# Sauvegarder dans le projet
output_path = 'data/online_retail_real.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"✅ {len(df)} lignes → {output_path}")
print(f"\nColonnes : {df.columns.tolist()}")
print(f"\nAperçu :\n{df.head()}")