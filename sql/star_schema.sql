-- =====================================================
-- SCHÉMA EN ÉTOILE - Sales & Market Analytics
-- =====================================================

-- 1. DIM CLIENT
DROP TABLE IF EXISTS dim_customer CASCADE;
CREATE TABLE dim_customer (
    customer_id     INT PRIMARY KEY,
    customer_name   VARCHAR(100),
    city            VARCHAR(50),
    segment         VARCHAR(20)
);

-- 2. DIM PRODUIT
DROP TABLE IF EXISTS dim_product CASCADE;
CREATE TABLE dim_product (
    stock_code      VARCHAR(20) PRIMARY KEY,
    description     VARCHAR(200)
);

-- 3. DIM DATE
DROP TABLE IF EXISTS dim_date CASCADE;
CREATE TABLE dim_date (
    date_id         INT PRIMARY KEY,           -- ex: 20091201
    full_date       DATE NOT NULL,
    year            INT,
    month           INT,
    month_name      VARCHAR(20),
    quarter         INT,
    day             INT,
    day_of_week     VARCHAR(20),
    is_weekend      BOOLEAN
);

-- 4. DIM VILLE
DROP TABLE IF EXISTS dim_city CASCADE;
CREATE TABLE dim_city (
    city_id         SERIAL PRIMARY KEY,
    city_name       VARCHAR(50) UNIQUE,
    region          VARCHAR(50)
);

-- 5. FACT SALES
DROP TABLE IF EXISTS fact_sales CASCADE;
CREATE TABLE fact_sales (
    sale_id         SERIAL PRIMARY KEY,
    invoice         VARCHAR(20),
    customer_id     INT REFERENCES dim_customer(customer_id),
    stock_code      VARCHAR(20) REFERENCES dim_product(stock_code),
    date_id         INT REFERENCES dim_date(date_id),
    city_id         INT REFERENCES dim_city(city_id),
    quantity        INT NOT NULL,
    price           NUMERIC(10,2) NOT NULL,
    total_amount    NUMERIC(12,2) NOT NULL
);

-- =====================================================
-- INDEX (performance analytique)
-- =====================================================
CREATE INDEX idx_fact_customer ON fact_sales(customer_id);
CREATE INDEX idx_fact_product  ON fact_sales(stock_code);
CREATE INDEX idx_fact_date     ON fact_sales(date_id);
CREATE INDEX idx_fact_city     ON fact_sales(city_id);
CREATE INDEX idx_fact_invoice  ON fact_sales(invoice);