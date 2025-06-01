#!/bin/bash
set -e

echo "🔧 Running code style fix..."

ruff check caytu_ai telegram test setup.py --fix
ruff format caytu_ai telegram test setup.py
isort caytu_ai telegram test setup.py
black caytu_ai telegram test setup.py

git add caytu_ai telegram
git commit -m "code style ✅ : auto format (ruff, isort, black)" || echo "✅ Nothing to commit"

echo "✅ Done!"
