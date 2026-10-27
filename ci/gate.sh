#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

SDK=python

# >>> version-files (S3; must match versionFiles("python") in ci/sdk-mirror/set-version.mjs)
VERSION_FILES=(
	pyproject.toml
	signalhouse_sms/__init__.py
	legacy/pyproject.toml
)
# <<< version-files

fail() { echo "::error::$SDK: $1" >&2; exit 1; }
check() { local name=$1; shift; "$@" || fail "$name"; }
quiet() { "$@" >"$T/quiet.log" 2>&1 || { cat "$T/quiet.log" >&2; return 1; }; }

T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
PY=${PYTHON:-python3}
export PYTHONDONTWRITEBYTECODE=1
VENV=$T/venv
VPY=$VENV/bin/python

# Prints "<file> <field> <value>" per version field.
read_versions() {
	local f
	for f in "${VERSION_FILES[@]}"; do
		case $f in
			pyproject.toml) "$VPY" -c 'import sys, tomllib; print(sys.argv[1], "version", tomllib.load(open(sys.argv[1], "rb"))["project"]["version"])' "$f" ;;
			signalhouse_sms/__init__.py) sed -nE "s/^__version__ = \"([^\"]+)\"$/$(sed 's#/#\\/#g' <<<"$f") __version__ \1/p" "$f" ;;
			legacy/pyproject.toml) "$VPY" -c '
import re, sys, tomllib
p = tomllib.load(open(sys.argv[1], "rb"))["project"]
print(sys.argv[1], "version", p["version"])
pins = [m.group(1) for d in p["dependencies"] for m in [re.fullmatch(r"signalhouse-sms==(\S+)", d)] if m]
print(sys.argv[1], "signalhouse-sms==", pins[0] if len(pins) == 1 else "<missing>")' "$f" ;;
			*) fail "version-files: no reader for $f" ;;
		esac
	done
}

check_versions() {
	local lines want
	lines=$(read_versions) || return 1
	[ "$(wc -l <<<"$lines")" -eq 4 ] || { echo "  expected 4 version fields, got: $lines" >&2; return 1; }
	if [ -n "${EXPECTED_VERSION:-}" ]; then
		want=$("$VPY" -c 'import sys; from packaging.version import Version; print(Version(sys.argv[1]))' "$EXPECTED_VERSION") || return 1
	else
		want=$(head -1 <<<"$lines" | awk '{print $NF}')
	fi
	echo "$lines" | awk -v want="$want" '$NF != want { print "  " $0 " != " want; bad=1 } END { exit bad }'
}

check_legacy_readme() {
	cmp -s LEGACY_README.md <(cat LEGACY_NOTICE.md README.md) && cmp -s legacy/README.md LEGACY_NOTICE.md
}

build_dists() {
	"$VPY" -m build --outdir "$T/dist" . >"$T/build.log" 2>&1 \
		&& "$VPY" -m build --outdir "$T/legacy-dist" legacy >>"$T/build.log" 2>&1 \
		|| { cat "$T/build.log" >&2; return 1; }
}

wheel_meta() { unzip -p "$1" '*.dist-info/METADATA'; }

check_metadata() {
	local v w lw
	v=$(sed -nE 's/^__version__ = "([^"]+)"$/\1/p' signalhouse_sms/__init__.py)
	w=$(ls "$T"/dist/*.whl) && lw=$(ls "$T"/legacy-dist/*.whl) || return 1
	wheel_meta "$w" | grep -qx "Name: signalhouse-sms" || { echo "  wheel Name" >&2; return 1; }
	wheel_meta "$w" | grep -qx "Version: $v" || { echo "  wheel Version" >&2; return 1; }
	wheel_meta "$lw" | grep -qx "Name: signalhouse" || { echo "  legacy wheel Name" >&2; return 1; }
	wheel_meta "$lw" | grep -qx "Version: $v" || { echo "  legacy wheel Version" >&2; return 1; }
	wheel_meta "$lw" | grep -qx "Requires-Dist: signalhouse-sms==$v" || { echo "  legacy Requires-Dist" >&2; return 1; }
}

# setuptools always adds setup.cfg and <pkg>.egg-info/ to an sdist; both are allowed.
check_sdist() {
	local bad
	bad=$(for f in "$T"/dist/*.tar.gz "$T"/legacy-dist/*.tar.gz; do tar tzf "$f" | sed -E 's#^[^/]+/?##'; done \
		| grep -vE '^$|^(signalhouse_sms|signalhouse|signalhouse_sms\.egg-info|signalhouse\.egg-info)/|^(README\.md|pyproject\.toml|PKG-INFO|setup\.cfg|LICENSE[^/]*)$' || true)
	[ -z "$bad" ] || { echo "  unexpected sdist entries:" >&2; echo "$bad" >&2; return 1; }
}

check_artifacts_clean() {
	local bad
	bad=$(for f in "$T"/dist/*.whl "$T"/legacy-dist/*.whl; do unzip -Z1 "$f"; done
		for f in "$T"/dist/*.tar.gz "$T"/legacy-dist/*.tar.gz; do tar tzf "$f" | sed -E 's#^[^/]+/##'; done)
	bad=$(grep -E '^(legacy|ci|\.github)/|(^|/)LEGACY_[^/]*\.md$' <<<"$bad" || true)
	[ -z "$bad" ] || { echo "$bad" >&2; return 1; }
}

check_smoke() {
	"$VPY" -c "from signalhouse_sms import SignalHouseSDK; SignalHouseSDK(api_key='x', base_url='http://127.0.0.1:9')"
}

# Installs the shim offline from the built dists plus a wheelhouse of runtime deps.
check_shim() {
	local v sv=$T/shim-venv
	v=$(sed -nE 's/^__version__ = "([^"]+)"$/\1/p' signalhouse_sms/__init__.py)
	"$VPY" -c 'import tomllib; print("\n".join(tomllib.load(open("pyproject.toml", "rb"))["project"]["dependencies"]))' >"$T/runtime-deps.txt" || return 1
	"$VPY" -m pip download -q --disable-pip-version-check --only-binary=:all: -d "$T/wheelhouse" -r "$T/runtime-deps.txt" || return 1
	"$PY" -m venv "$sv" || return 1
	"$sv/bin/pip" install -q --disable-pip-version-check --no-index --find-links "$T/dist" --find-links "$T/legacy-dist" --find-links "$T/wheelhouse" "signalhouse==$v" || return 1
	if "$sv/bin/python" -W error::DeprecationWarning -c "import signalhouse" 2>/dev/null; then
		echo "  import signalhouse did not raise DeprecationWarning" >&2; return 1
	fi
	"$sv/bin/python" -W ignore::DeprecationWarning -c "import signalhouse.exceptions, signalhouse.client, signalhouse.domains" || return 1
	"$sv/bin/signalhouse-skills" --help >/dev/null || return 1
}

echo "== $SDK: venv"; check venv "$PY" -m venv "$VENV"
check "pip install tools" "$VPY" -m pip install -q --disable-pip-version-check build twine pytest packaging
echo "== $SDK: versions"; check versions check_versions
echo "== $SDK: legacy readme"; check legacy-readme check_legacy_readme
echo "== $SDK: pip install -e ."; check "pip install -e ." "$VPY" -m pip install -q --disable-pip-version-check -e .
echo "== $SDK: tests"; check tests "$VPY" -m pytest -q -p no:cacheprovider tests
echo "== $SDK: build"; check build build_dists
echo "== $SDK: twine check"; check "twine check" quiet "$VPY" -m twine check --strict "$T"/dist/* "$T"/legacy-dist/*
echo "== $SDK: metadata"; check metadata check_metadata
echo "== $SDK: sdist contents"; check "sdist contents" check_sdist
echo "== $SDK: artifact contents"; check "artifact contents" check_artifacts_clean
echo "== $SDK: smoke"; check smoke check_smoke
echo "== $SDK: shim"; check shim check_shim
echo "gate passed: $SDK"
