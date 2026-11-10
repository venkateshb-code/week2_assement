DROP TABLE IF EXISTS performance_orders;
CREATE TABLE performance_orders (
    id BIGINT PRIMARY KEY,
    customer_id INT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,;
    created_at DATE NOT NULL
);

INSERT INTO performance_orders (id, customer_id, amount, created_at)
SELECT gs, (gs % 10000)::INT + 1,
       ((gs % 5000) + 100)::NUMERIC(10,2),
       DATE '2026-01-01' + (gs % 365)::INT
FROM generate_series(1, 200000) AS gs;

ANALYZE performance_orders;

SELECT COUNT(*) AS total_rows FROM performance_orders -- Expected: 200000

-- 2. Performance BEFORE index: record Execution Time
EXPLAIN ANALYZE
SELECT id, customer_id, amount
FROM performance_orders
WHERE customer_id = 12345;

-- 3. Create index and run same query AFTER index
CREATE INDEX idx_performance_orders_customer_id
ON performance_orders(customer_id);

ANALYZE performance_orders;

EXPLAIN ANALYZE
SELECT id, customer_id, amount
FROM performance_orders
WHERE customer_id = 12345;

-- Note: timings vary by machine, PostgreSQL version, and cache.
-- Record the actual Execution Time shown by your PostgreSQL instance.

-- 4. Constraints: NOT NULL, UNIQUE, FOREIGN KEY, CHECK
DROP TABLE IF EXISTS safety_orders;
DROP TABLE IF EXISTS safety_customers;

CREATE TABLE safety_customers (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE safety_orders (
    id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    CONSTRAINT fk_safety_customer
        FOREIGN KEY (customer_id) REFERENCES safety_customers(id)
);

INSERT INTO safety_customers (id, name, email)
VALUES (1, 'Arun', 'arun@example.com');

INSERT INTO safety_orders (id, customer_id, amount)
VALUES (101, 1, 500.00);

-- Each invalid INSERT is caught separately so the script continues.
DO $$
BEGIN
    BEGIN
        INSERT INTO safety_customers (id, name, email)
        VALUES (2, NULL, 'null-name@example.com');
    EXCEPTION WHEN not_null_violation THEN
        RAISE NOTICE 'NOT NULL violation caught: %', SQLERRM;
    END;

    BEGIN
        INSERT INTO safety_customers (id, name, email)
        VALUES (3, 'Duplicate Email', 'arun@example.com');
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'UNIQUE violation caught: %', SQLERRM;
    END;

    BEGIN
        INSERT INTO safety_orders (id, customer_id, amount)
        VALUES (102, 9999, 250.00);
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'FOREIGN KEY violation caught: %', SQLERRM;
    END;

    BEGIN
        INSERT INTO safety_orders (id, customer_id, amount)
        VALUES (103, 1, -50.00);
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'CHECK violation caught: %', SQLERRM;
    END;
END $$;

-- Verify only valid rows remain
SELECT id, name, email FROM safety_customers ORDER BY id;
SELECT id, customer_id, amount FROM safety_orders ORDER BY id;
