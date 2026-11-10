# ORM, Migrations and Transactions

## Prerequisites
- Python 3.10+
- PostgreSQL running locally
- MongoDB running locally (or update `MONGO_URI` to your MongoDB connection URI)

## Setup (Windows PowerShell / VS Code terminal)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your PostgreSQL password/database values. Create the PostgreSQL database named `venkatesh` first if it does not exist.

## Migrations

This folder includes two migration scripts so you can apply and inspect the complete schema immediately:

```powershell
alembic upgrade head
alembic history
alembic current
```

To demonstrate the requested `--autogenerate` workflow yourself:
1. Back up or remove the two supplied demo revision files from `migrations/versions/`.
2. Temporarily remove `phone` from `Customer` in `app/models.py`.
3. Run `alembic revision --autogenerate -m "create customers orders products"`.
4. Run `alembic upgrade head`.
5. Add `phone` back to `Customer`.
6. Run `alembic revision --autogenerate -m "add phone to customers"`.
7. Run `alembic upgrade head` and `alembic history`.

Do not generate duplicate revisions on top of the supplied revisions.

## Run

```powershell
py main.py
```

Expected key output:

```text
Order placed: stock 10 -> 8
Forced failure: rolled back (Forced transaction failure)
Stock before failure: 10
Stock after failure: 10
5 order events inserted successfully
MongoDB Customer Totals:
customer 1 -> 1300
  orders: 5
```

`main.py` resets the demo product stock to 10 before each demonstration. Use a dedicated training database only; do not run this demo against production data.

## Notes
- SQLAlchemy pool: `pool_size=5`, `max_overflow=2`.
- `place_order()` locks the product row with `SELECT ... FOR UPDATE`, updates stock and inserts the order in one transaction.
- The forced error occurs after `flush()` so the SQL changes are sent within the transaction before rollback.
- MongoDB events are tagged with a demo batch so aggregation only counts this exercise's five events.
