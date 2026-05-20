#!/bin/sh
set -e

echo "[facebouk] Seeding database..."
python seed.py

echo "[facebouk] Starting application..."
exec python -c "from app import app; app.run(host='0.0.0.0', port=5000)"
