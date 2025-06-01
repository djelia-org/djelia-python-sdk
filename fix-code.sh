#!/bin/bash
set -e

echo "🔧 Running code style fix..."

ruff check djelia cookbook test setup.py --fix
ruff check djelia cookbook test setup.py
isort check djelia cookbook test setup.py
black .

git add check djelia cookbook test setup.py
git commit -m "code style ✅ : auto format (ruff, isort, black)" || echo "✅ Nothing to commit"

echo "✅ Done!"