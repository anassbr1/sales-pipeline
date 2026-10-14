-- Vue 1 : CA mensuel par ville
CREATE OR REPLACE VIEW v_ca_mensuel_ville AS
SELECT d.year, d.month, d.month_name, c.city_name,
       SUM(f.total_amount) AS ca,
       COUNT(DISTINCT f.invoice) AS nb_commandes
FROM fact_sales f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_city c ON f.city_id = c.city_id
GROUP BY d.year, d.month, d.month_name, c.city_name;

-- Vue 2 : Top produits
CREATE OR REPLACE VIEW v_top_produits AS
SELECT p.stock_code, p.description,
       SUM(f.quantity) AS qte_vendue,
       SUM(f.total_amount) AS ca
FROM fact_sales f
JOIN dim_product p ON f.stock_code = p.stock_code
GROUP BY p.stock_code, p.description
ORDER BY ca DESC;

-- Vue 3 : KPIs globaux
CREATE OR REPLACE VIEW v_kpis_globaux AS
SELECT
    COUNT(DISTINCT invoice) AS nb_commandes,
    COUNT(DISTINCT customer_id) AS nb_clients,
    SUM(total_amount) AS ca_total,
    AVG(total_amount) AS panier_moyen
FROM fact_sales;