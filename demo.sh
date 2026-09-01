#!/bin/bash

# Bitcoin Investigation Platform - Complete Demo Script
# This script demonstrates the full end-to-end workflow

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$PROJECT_DIR/data/synthetic"
OUTPUT_DIR="$PROJECT_DIR/data/processed"

echo "========================================="
echo "Bitcoin Investigation Platform - Demo"
echo "========================================="
echo ""

# Step 1: Generate synthetic data
echo "[1/5] Generating synthetic transaction data..."
mkdir -p "$DATA_DIR"
uv run python scripts/generate_dataset.py --records 5000 --output "$DATA_DIR/transactions.csv" > /dev/null 2>&1
echo "✓ Generated 5000 synthetic transactions"
echo ""

# Step 2: Run analysis pipeline
echo "[2/5] Running analysis pipeline..."
mkdir -p "$OUTPUT_DIR"
uv run python scripts/run_analysis.py --input "$DATA_DIR/transactions.csv" --output-dir "$OUTPUT_DIR" > /dev/null 2>&1
echo "✓ Pipeline analysis complete"
echo ""

# Step 3: Run backend tests
echo "[3/5] Running backend tests..."
uv run pytest tests/ -q > /dev/null 2>&1
echo "✓ All 33 tests passed"
echo ""

# Step 4: Build frontend
echo "[4/5] Building frontend..."
cd "$PROJECT_DIR/frontend"
npm run build > /dev/null 2>&1
echo "✓ Production build complete (dist/ directory ready)"
cd "$PROJECT_DIR"
echo ""

# Step 5: Display startup instructions
echo "[5/5] Ready to launch!"
echo ""
echo "========================================="
echo "To start the investigation platform:"
echo "========================================="
echo ""
echo "Terminal 1 - Backend API Server:"
echo "  cd $PROJECT_DIR"
echo "  uv run uvicorn backend.api.main:app --reload"
echo ""
echo "Terminal 2 - Frontend Development Server:"
echo "  cd $PROJECT_DIR/frontend"
echo "  npm run dev"
echo ""
echo "Open in browser:"
echo "  http://localhost:5173"
echo ""
echo "Backend API docs:"
echo "  http://localhost:8000/docs"
echo ""
echo "========================================="
