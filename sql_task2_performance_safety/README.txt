# Task 2 - Performance and Safety

## Files
- `performance_safety.sql`: loads 200,000 rows, runs EXPLAIN ANALYZE before/after an index, and demonstrates four constraint violations.
- `get_orders.py`: Python `get_orders(customer_id)` using a parameterized psycopg2 query.
- `screenshots/`: save your own pgAdmin and terminal screenshots here.

## Run SQL in pgAdmin
1. Connect to your practice database and open Query Tool.
2. Open and execute `performance_safety.sql`.
3. Confirm `COUNT(*)` is 200000.
4. Record the `Execution Time` line from each EXPLAIN ANALYZE result.
5. Check the Messages tab for NOT NULL, UNIQUE, FOREIGN KEY, and CHECK NOTICE messages.

## Install and run Python (VS Code terminal)
    py -m pip install psycopg2-binary

The script defaults to localhost:5432, database `venkatesh`, user `postgres`.
Set your password in PowerShell:
    $env:PGPASSWORD="your_postgres_password"
    py get_orders.py

Expected:
- Input 1 returns matching rows.
- Input '1 OR 1=1' returns 0 rows. It is bound as a literal value, not executed as SQL.

## Performance note
The expected ~40 ms Seq Scan and ~0.1 ms Index Scan are examples, not guaranteed timings. Actual timings depend on hardware, PostgreSQL settings, and cache. Record the actual timings from your machine. If the planner chooses Seq Scan after indexing, confirm ANALYZE ran and inspect the plan.

## Screenshot checklist
1. `01_row_count.png` - count of 200000.
2. `02_before_index.png` - before-index plan and Execution Time.
3. `03_after_index.png` - after-index plan and Execution Time.
4. `04_constraint_errors.png` - Messages showing all four NOTICE messages.
5. `05_python_parameterized_query.png` - terminal showing both Python tests.
