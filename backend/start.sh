#!/bin/sh
set -e

python -m app.database.session init_db
python -m app.scripts.seed_users
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
