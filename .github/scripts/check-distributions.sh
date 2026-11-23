#!/usr/bin/env bash
set -euo pipefail
dist_dir=$(realpath "$1")
expected_version=$2
script_dir=$(cd "$(dirname "$0")" && pwd)
workdir=$(mktemp -d)
trap 'rm -rf -- "$workdir"' EXIT
cd "$workdir"

for file in "python_loading_sdk-${expected_version}-py3-none-any.whl" "python_loading_sdk-${expected_version}.tar.gz"; do
    env_dir="$workdir/env-${file##*.}"
    uv venv "$env_dir"
    uv pip install --python "$env_dir/bin/python" "$dist_dir/$file"
    "$env_dir/bin/python" -I "$script_dir/smoke_release.py" "$expected_version"
done
