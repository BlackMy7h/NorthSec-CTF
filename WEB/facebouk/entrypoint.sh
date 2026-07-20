#!/bin/sh
set -e

echo "[facebouk] Seeding database..."
python seed.py

echo "[facebouk] Starting application..."
# IMPORTANT: inside Docker, bind to 0.0.0.0 so port publishing works.
# Access from host via http://127.0.0.1:5000
exec python -c "from app import app; app.run(host='0.0.0.0', port=5000)"
