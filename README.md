# 📊 Enterprise Sales & Market Analytics Pipeline

Pipeline ETL automatisé pour l'analyse des ventes, la prévision ML et la visualisation via Power BI — entièrement conteneurisé avec Docker.

[https://img.shields.io/badge/Python-3.11-blue]
[https://img.shields.io/badge/PostgreSQL-16-blue]
[https://img.shields.io/badge/Docker-Compose-blue]
[https://img.shields.io/badge/PowerBI-Desktop-yellow]
[https://img.shields.io/badge/Scikit--Learn-ML-orange]

---

## 🎯 Objectif

Construire un pipeline de données de bout en bout qui :
- Ingère et nettoie **+800 000 transactions** réelles de e-commerce
- Modélise un **schéma en étoile** optimisé pour l'analyse
- Entraîne un **modèle ML** pour prévoir les ventes sur 6 mois
- Expose un **dashboard Power BI** interactif
- Tourne **automatiquement chaque jour** via Docker + cron

---

## 🏗️ Architecture

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  CSV brut   │────▶│  ETL Python  │────▶│ PostgreSQL  │
│ (1M lignes) │     │   (Pandas)   │     │  (étoile)   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │     ML      │
                                         │ RandomForest│
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  Power BI   │
                                         │  Dashboard  │
                                         └─────────────┘
```

---

## 📂 Structure du projet

```text
sales/
├── data/                  # Données brutes (CSV)
├── scripts/
│   ├── download_data.py   # Téléchargement depuis Kaggle
│   ├── etl.py             # Pipeline ETL (extract → transform → load)
│   ├── populate_star.py   # Remplissage schéma en étoile
│   └── ml_forecast.py     # Entraînement ML + prévisions
├── sql/
│   ├── star_schema.sql    # Tables + index
│   └── views.sql          # Vues analytiques
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── crontab            # Planification quotidienne
├── dashboard/             # Fichier Power BI (.pbix)
├── notebooks/             # Exploration
├── .env                   # Secrets (non versionné)
├── requirements.txt
└── README.md
```

---

## ⚙️ Stack technique

| Composant | Technologie | Rôle |
|---|---|---|
| Langage | Python 3.11 | ETL + ML |
| Manipulation | Pandas, NumPy | Nettoyage, agrégation |
| Base de données | PostgreSQL 16 | Stockage analytique |
| ORM | SQLAlchemy + psycopg2 | Connexion DB |
| ML | Scikit-Learn (RandomForest) | Prévisions |
| Conteneurisation | Docker + Compose | Orchestration |
| Planification | Cron (dans container) | Actualisation quotidienne |
| Visualisation | Power BI Desktop | Dashboards |

---

## 🚀 Installation

### Prérequis
- Docker Desktop
- Power BI Desktop
- Python 3.11+ (pour exécution locale)

### Lancement rapide

```bash
git clone <ton-repo>
cd sales/docker
docker-compose up --build
```

Le pipeline s'exécute automatiquement :
1. Postgres démarre
2. ETL tourne → 801 994 lignes dans `fact_sales`
3. ML tourne → 48 prédictions dans `sales_forecast`
4. Scheduler reste actif → relance quotidienne à 2h

### Vérification

```bash
docker exec -it sales_postgres psql -U postgres -d sales_db \
  -c "SELECT COUNT(*) FROM fact_sales;"
# → 801994
```

---

## 📈 Résultats

### Pipeline

| Métrique | Valeur |
|---|---|
| Lignes brutes ingérées | 1 067 371 |
| Lignes après nettoyage | 801 994 |
| Clients uniques | 5 878 |
| Produits uniques | 4 631 |
| Villes (Maroc) | 8 |
| Prédictions générées | 48 (8 villes × 6 mois) |

### Performance ML (Random Forest)

| Ville | MAE (MAD) | R² |
|---|---|---|
| Casablanca | 25 044 | 0.31 |
| Fès | 25 742 | 0.34 |
| Marrakech | 27 990 | 0.30 |
| Meknès | 21 299 | 0.49 |
| Oujda | 29 100 | 0.19 |
| Rabat | 20 348 | 0.53 |
| Tanger | 25 229 | 0.32 |
| Agadir | 34 114 | -0.26 ⚠️ |

> **Note** : Agadir présente un R² faible à cause d'une forte variance mensuelle. Piste d'amélioration : ajouter des features externes (saison touristique, événements locaux).

---

## 🔄 Automatisation

Le fichier `docker/crontab` planifie :
- 02h00 → ETL (extraction + nettoyage + schéma en étoile)
- 02h30 → ML (entraînement + prédictions)

Logs disponibles dans `/var/log/pipeline.log` du conteneur scheduler.

---

## 🎓 Compétences démontrées

- **Data Engineering** : ETL, modélisation dimensionnelle, indexation
- **Data Science** : feature engineering, régression, évaluation (MAE, R²)
- **DevOps** : Dockerisation, orchestration multi-services, cron
- **BI** : connexion PostgreSQL, mesures DAX, dashboards interactifs

---

## 👤 Contact

- **LinkedIn** : [Anass Bouras](https://www.linkedin.com/in/anass-bouras-0b0361285/)