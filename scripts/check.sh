#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
"${PYTHON:-python3}" -B -m unittest discover -s "$project_dir/tests" -v
cmake -S "$project_dir" -B "$project_dir/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$project_dir/build" --parallel "${BUILD_JOBS:-32}"
ctest --test-dir "$project_dir/build" --output-on-failure
