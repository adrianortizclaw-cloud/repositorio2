#!/bin/sh
set -e

cd "$(dirname "$0")"

python3 -m app.database.session init_db
python3 -m app.scripts.seed_users
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
