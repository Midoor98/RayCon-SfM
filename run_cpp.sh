#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cmake -S "$project_dir" -B "$project_dir/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$project_dir/build" --parallel "${BUILD_JOBS:-32}"
if [[ "${1:-}" == "--version" || "${1:-}" == "--help" ]]; then
    exec "$project_dir/build/raycon_sfm_preview" "$@"
fi
output="$project_dir/result/cpp-$(date -u +%Y%m%dT%H%M%S)-$$"
exec "$project_dir/build/raycon_sfm_preview" --input "$project_dir/data/pair_matches.csv" --output "$output" "$@"
