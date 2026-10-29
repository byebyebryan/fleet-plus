#!/usr/bin/env bash
set -euo pipefail

# Opt-in media recipe. It builds a temporary environment from public pinned
# packages and uses only the committed fictional cache fixture. It does not
# inspect native providers, configured user sources, or live sessions.
#
# Usage:
#   bash scripts/capture-terminal-media.sh [output-directory]
#   FLEET_CAPTURE_RECEIPT=/tmp/capture.json bash scripts/capture-terminal-media.sh /tmp/previews

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="${1:-$repo_root/assets}"
python_bin="${PYTHON:-python3}"
observer_wheel='agent_observer-0.7.0a14-py3-none-any.whl'
mesh_wheel='mesh_plus-0.1.0a25-py3-none-any.whl'
release_url='https://github.com/byebyebryan/agent-observer/releases/download/v0.7.0a14'
observer_sha='46a1158023023b60d9b839184a45f7b7eeb21b04dce67aad808fa8277522518f'
mesh_sha='0055e42162827744add4f817d3918cfc20471e5ec5a3cdf0840d254f76f5dc3a'
tmp_dir="$(mktemp -d)"
trap 'rm -rf -- "$tmp_dir"' EXIT INT TERM

for command in curl sha256sum ffmpeg ffprobe rsvg-convert fc-match; do
  command -v "$command" >/dev/null || {
    printf 'Missing required capture command: %s\n' "$command" >&2
    exit 2
  }
done

"$python_bin" -m venv "$tmp_dir/venv"
capture_python="$tmp_dir/venv/bin/python"
"$capture_python" -m pip install --disable-pip-version-check --requirement \
  "$repo_root/scripts/terminal-capture-requirements.txt"

curl --fail --location --silent --show-error \
  "$release_url/$observer_wheel" --output "$tmp_dir/$observer_wheel"
curl --fail --location --silent --show-error \
  "$release_url/$mesh_wheel" --output "$tmp_dir/$mesh_wheel"
printf '%s  %s\n' "$observer_sha" "$tmp_dir/$observer_wheel" | sha256sum --check --status
printf '%s  %s\n' "$mesh_sha" "$tmp_dir/$mesh_wheel" | sha256sum --check --status

"$capture_python" -m pip install --disable-pip-version-check --no-deps \
  "$tmp_dir/$observer_wheel" "$tmp_dir/$mesh_wheel"

PYTHONPATH="$repo_root" "$capture_python" -m unittest discover \
  -s "$repo_root/tests" -p 'test_terminal_colors.py' -v

capture_args=(
  --python "$capture_python"
  --observer-wheel "$tmp_dir/$observer_wheel"
  --mesh-wheel "$tmp_dir/$mesh_wheel"
  --scenario "$repo_root/fixtures/terminal-dashboard-scenario.json"
  --output-dir "$output_dir"
)
if [[ "$(cd -- "$output_dir" 2>/dev/null && pwd || true)" == "$repo_root/assets" ]]; then
  capture_args+=(--provenance "$repo_root/assets/provenance.json")
fi
if [[ -n "${FLEET_CAPTURE_RECEIPT:-}" ]]; then
  capture_args+=(--receipt "$FLEET_CAPTURE_RECEIPT")
fi
"$capture_python" "$repo_root/scripts/capture_terminal_media.py" "${capture_args[@]}"
