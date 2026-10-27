#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SDK=python
BUILD_VERSION=1.6.1
TWINE_VERSION=7.0.0
fail() { echo "::error::$SDK: $1" >&2; exit 1; }
run() { if [ "${PUBLISH_DRY_RUN:-}" = 1 ]; then printf '+ (dry run) would run:'; printf ' %q' "$@"; echo; else "$@"; fi; }

# Exit 0 = both the sdist and the wheel are published, 1 = absent or incomplete; anything else fails.
# PyPI records a release on its first upload, so a version lookup alone would skip a half-uploaded release.
published() {
	local out code body
	out=$(curl -sS --retry 3 -w '\n%{http_code}' "https://pypi.org/pypi/$1/$2/json") || fail "registry check $1==$2"
	code=${out##*$'\n'}
	body=${out%$'\n'*}
	case $code in
		200) ;;
		404) return 1 ;;
		*) fail "registry check $1==$2: HTTP $code" ;;
	esac
	printf '%s' "$body" | "$PY" -c 'import json, sys; kinds = {u["packagetype"] for u in json.load(sys.stdin)["urls"]}; sys.exit(0 if {"sdist", "bdist_wheel"} <= kinds else 1)'
}

# Tells the workflow's PyPI action steps which dists to upload.
output() { [ -n "${GITHUB_OUTPUT:-}" ] && echo "$1=$2" >>"$GITHUB_OUTPUT" || true; }

PY=${PYTHON:-python3}
V=$("$PY" -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')
LV=$("$PY" -c 'import tomllib; print(tomllib.load(open("legacy/pyproject.toml", "rb"))["project"]["version"])')
[ "$LV" = "$V" ] || fail "legacy version $LV differs from $V"

NEED_ROOT=true NEED_LEGACY=true
if published signalhouse-sms "$V"; then echo "signalhouse-sms==$V exists, skipping"; NEED_ROOT=false; fi
if published signalhouse "$V"; then echo "signalhouse==$V exists, skipping"; NEED_LEGACY=false; fi
output root "$NEED_ROOT"
output legacy "$NEED_LEGACY"
[ "$NEED_ROOT" = true ] || [ "$NEED_LEGACY" = true ] || exit 0

run "$PY" -m pip install -q --disable-pip-version-check "build==$BUILD_VERSION" "twine==$TWINE_VERSION" || fail "install build tools"
run rm -rf dist legacy/dist
if [ "$NEED_ROOT" = true ]; then
	run "$PY" -m build --outdir dist . || fail "build signalhouse-sms"
	run "$PY" -m twine check --strict dist/* || fail "twine check signalhouse-sms"
fi
if [ "$NEED_LEGACY" = true ]; then
	run "$PY" -m build --outdir legacy/dist legacy || fail "build signalhouse"
	run "$PY" -m twine check --strict legacy/dist/* || fail "twine check signalhouse"
fi

if [ -n "${TWINE_PASSWORD:-}" ]; then
	export TWINE_USERNAME=${TWINE_USERNAME:-__token__}
	# Root first: the shim pins it.
	if [ "$NEED_ROOT" = true ]; then run "$PY" -m twine upload --skip-existing --non-interactive dist/* || fail "twine upload signalhouse-sms"; fi
	if [ "$NEED_LEGACY" = true ]; then run "$PY" -m twine upload --skip-existing --non-interactive legacy/dist/* || fail "twine upload signalhouse"; fi
else
	echo "TWINE_PASSWORD unset: leaving dist/ and legacy/dist/ for the PyPI publish action"
fi
