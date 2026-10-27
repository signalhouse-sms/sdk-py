#!/usr/bin/env python3
"""Regenerate the vendored copy of the Signal House agent skills.

The agent-skills repo is the single source of truth. This SDK ships a VENDORED copy so the wheel
carries the skills with it and ``signalhouse-skills`` needs no network. A vendored copy is only
safe while it is generated rather than hand-edited, so everything under ``signalhouse_sms/skills/`` is
written by this script and must not be edited in place.

Usage::

    python scripts/sync_skills.py --from ../../../agent-skills --ref v0.2.0
    python scripts/sync_skills.py --from <agent-skills git URL> --ref v0.2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parent.parent
DEST = SDK_ROOT / "signalhouse_sms" / "skills"


def _sha256(path: Path) -> str:
    """Hex sha256 of a file.

    :param path: File to hash.
    :returns: Hex digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    """Run git and return trimmed stdout.

    :param args: Arguments passed to git.
    :returns: Command output.
    """
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def main() -> int:
    """Vendor the skills at a tag and write the manifest.

    :returns: Process exit code.
    """
    parser = argparse.ArgumentParser(prog="sync_skills")
    parser.add_argument("--from", dest="source", required=True, help="Local checkout path or git URL")
    parser.add_argument("--ref", required=True, help="Tag to vendor, recorded in the manifest")
    args = parser.parse_args()

    checkout = None
    if args.source.startswith(("http", "git@")):
        checkout = Path(tempfile.mkdtemp(prefix="sh-skills-"))
        subprocess.run(
            ["git", "clone", "--quiet", "--depth", "1", "--branch", args.ref, args.source, str(checkout)],
            check=True,
        )
        source_root = checkout
    else:
        source_root = (SDK_ROOT / args.source).resolve()
        # A local checkout is an authoring convenience, so confirm it is actually AT the ref being
        # recorded. Recording a tag while copying whatever is checked out makes the manifest lie.
        try:
            ref_commit = _git("-C", str(source_root), "rev-parse", f"{args.ref}^{{commit}}")
        except subprocess.CalledProcessError:
            print(f"x {source_root} has no ref {args.ref!r}. Tag the release first, then sync.", file=sys.stderr)
            return 1
        head = _git("-C", str(source_root), "rev-parse", "HEAD")
        if head != ref_commit:
            print(f"x {source_root} is at {head[:8]}, not {args.ref} ({ref_commit[:8]}).", file=sys.stderr)
            return 1

    skills_src = source_root / "skills"
    if not skills_src.is_dir():
        print(f"x no skills/ directory in {source_root}", file=sys.stderr)
        return 1

    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)

    names = sorted(p.name for p in skills_src.iterdir() if p.is_dir())
    for name in names:
        shutil.copytree(skills_src / name, DEST / name)

    files = {
        str(path.relative_to(DEST)): _sha256(path)
        for path in sorted(DEST.rglob("*"))
        if path.is_file()
    }

    (DEST / "VENDORED.json").write_text(
        json.dumps({"source": "agent-skills", "ref": args.ref, "skills": names, "files": files}, indent=2) + "\n"
    )

    if checkout:
        shutil.rmtree(checkout, ignore_errors=True)

    print(f"OK vendored {len(names)} skill(s) at {args.ref}: {', '.join(names)}")
    print(f"  {DEST.relative_to(SDK_ROOT)}/ is generated. Do not edit it by hand.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
