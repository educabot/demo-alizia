#!/bin/bash
set -e

DB_URL="postgresql://postgres:postgres@localhost:5480/av3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Resetting database..."
psql "$DB_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo "Running migrations..."
psql "$DB_URL" -f "$PROJECT_DIR/migrations/001_initial.sql"

echo "Running seeds..."
psql "$DB_URL" -f "$PROJECT_DIR/seeds/seed.sql"

echo "Database reset complete!"
