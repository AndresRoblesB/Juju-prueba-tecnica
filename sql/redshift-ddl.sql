-- Dimension: Users
CREATE TABLE dim_user (
    user_id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255),
    country VARCHAR(8),
    created_at DATE
)
DISTSTYLE ALL
SORTKEY(user_id);

-- Dimension: Products
CREATE TABLE dim_product (
    sku VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(12,2)
)
DISTSTYLE ALL
SORTKEY(sku);

-- Fact: Order Header
CREATE TABLE fact_order_header (
    order_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64),
    amount DECIMAL(12,2),
    currency VARCHAR(8),
    order_date DATE,
    created_at TIMESTAMP,
    source VARCHAR(50),
    promo VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES dim_user(user_id)
)
DISTKEY(user_id)
SORTKEY(order_date);

-- Fact: Order Items (Detail)
CREATE TABLE fact_order_details (
    order_id VARCHAR(64),
    sku VARCHAR(64),
    qty INT,
    price DECIMAL(12,2),
    order_date DATE,
    FOREIGN KEY (order_id) REFERENCES fact_order_header(order_id),
    FOREIGN KEY (sku) REFERENCES dim_product(sku)
)
DISTKEY(order_id)
SORTKEY(order_date);