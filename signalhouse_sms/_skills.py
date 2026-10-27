"""Install the bundled Signal House agent skills into a project.

Exposed as the ``signalhouse-skills`` console script.

Why this is a command and not automatic: a pip wheel has no post-install hook. That is deliberate
on packaging's part, and there is no supported way around it that does not involve shipping an
sdist and forcing a source build on every user. So where the npm package can offer to place the
skills during ``npm install``, the Python package ships them and the developer runs one command.

The safety rules match the npm installer, because the risk is the same:

* PROJECT scope by default. It writes under the current directory, not the home directory.
* It never overwrites a file whose contents differ from what a previous run wrote. An edited skill
  belongs to the developer.
* It reports what it changed, including which version it moved from.

The skills are bundled in the wheel, so this does no network access.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath

# Project-scope paths, from the `skills` CLI agent table (vercel-labs/skills).
# Claude Code reads .claude/skills/; Cursor and GitHub Copilot both read .agents/skills/.
AGENT_DIRS = [
    (".claude", Path(".claude") / "skills", "Claude Code"),
    (".agents", Path(".agents") / "skills", "Cursor / Copilot"),
]

RECEIPT = ".signalhouse-skills.json"


def _bundled_root() -> Path:
    """Locate the skills bundled inside the installed package.

    :returns: Path to the bundled ``skills`` directory.
    """
    return Path(__file__).resolve().parent / "skills"


def _sha256(path: Path) -> str:
    """Hex sha256 of a file.

    :param path: File to hash.
    :returns: Hex digest.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _install_to(project: Path, dest: Path, receipt: dict) -> tuple[list[str], list[str]]:
    """Copy every bundled skill into one agent directory.

    :param project: Project root being installed into.
    :param dest: Agent-relative destination, e.g. ``.claude/skills``.
    :param receipt: Path-to-hash map from the previous run, mutated in place.
    :returns: ``(written, skipped)`` relative file paths.
    """
    written: list[str] = []
    skipped: list[str] = []
    root = _bundled_root()

    for skill_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for src in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
            rel = src.relative_to(root)
            dst = project / dest / rel
            key = str(dest / rel)

            if dst.exists():
                current = _sha256(dst)
                if current == _sha256(src):
                    continue
                # Present, different, and not what we last wrote: leave the developer's edit alone.
                # An absent entry reads the same way: get() returns None, which already differs.
                if receipt.get(key) != current:
                    skipped.append(str(rel))
                    continue

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            receipt[key] = _sha256(dst)
            written.append(str(rel))

    return written, skipped


def _is_unsafe_key(key: str) -> bool:
    """True when a receipt key must never be turned into a filesystem path.

    :param key: Receipt key, expected to be a project-relative path we wrote.
    :returns: Whether the key is absolute or contains a parent-directory segment.
    """
    if not isinstance(key, str) or not key:
        return True
    candidate = PurePosixPath(key.replace("\\", "/"))
    return candidate.is_absolute() or ".." in candidate.parts


def _prune_obsolete(project: Path, receipt: dict, current_keys: set[str]) -> tuple[list[str], list[str], list[str]]:
    """Remove skill files a previous run wrote that the current bundle no longer contains.

    Upgrades are otherwise additive: a file dropped or renamed upstream stays on disk forever and
    keeps feeding an agent instructions the release deliberately withdrew. Only files whose hash
    still matches the receipt are provably ours and unmodified; a developer's edit is reported.

    :param project: Project root.
    :param receipt: Path-to-hash map from the previous run, mutated in place.
    :param current_keys: Receipt keys the current bundle just wrote or verified.
    :returns: ``(removed, orphaned, refused)`` relative paths.
    """
    removed: list[str] = []
    orphaned: list[str] = []
    refused: list[str] = []

    for key in [k for k in receipt if k != "_ref" and k not in current_keys]:
        # The receipt is a file on disk, so its keys are untrusted input to a delete. An absolute
        # key is especially dangerous here: `Path("/proj") / "/etc/passwd"` discards the project
        # entirely and yields `/etc/passwd`. A climbing key does the same with `..`. Either is
        # dropped, never followed.
        if _is_unsafe_key(key):
            del receipt[key]
            refused.append(key)
            continue
        dst = project / key
        if not _resolves_inside_project(project, dst):
            del receipt[key]
            refused.append(key)
            continue
        if not dst.exists():
            del receipt[key]
            continue
        if _sha256(dst) != receipt[key]:
            orphaned.append(key)
            continue
        dst.unlink()
        del receipt[key]
        removed.append(key)

    return removed, orphaned, refused


def _resolves_inside_project(project: Path, candidate: Path) -> bool:
    """True when a path really lands inside the project, following symlinks.

    ``Path.resolve`` on a non-existent path only normalises text, so it cannot see that ``.claude``
    is a symlink elsewhere. Walks up to the nearest existing ancestor and resolves that.

    :param project: Project root.
    :param candidate: Path the installer wants to write under.
    :returns: Whether the real destination is contained by the real project root.
    """
    probe = candidate
    while not probe.exists():
        if probe.parent == probe:
            return False
        probe = probe.parent
    try:
        real_probe = probe.resolve(strict=True)
        real_root = project.resolve(strict=True)
    except OSError:
        return False
    return real_probe == real_root or real_root in real_probe.parents


def install(project: Path, force: bool = False) -> int:
    """Install the bundled skills into whichever agent directories the project uses.

    :param project: Project root.
    :param force: Create the agent directories even when the project has none.
    :returns: Process exit code.
    """
    root = _bundled_root()
    manifest_path = root / "VENDORED.json"
    if not manifest_path.exists():
        print("No skills are bundled in this build of the signalhouse-sms package.", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text())
    candidates = [(d, label) for marker, d, label in AGENT_DIRS if force or (project / marker).exists()]
    # A marker that resolves outside the project is skipped rather than followed, matching the JS
    # installer. Symlinking an agent directory to a shared or home config is a normal setup, and
    # writing through it would break this installer's project-scope guarantee.
    targets = []
    for dest, label in candidates:
        if _resolves_inside_project(project, project / dest):
            targets.append((dest, label))
        else:
            print(f"Skipping {label}: {dest} resolves outside this project.")

    if not targets:
        print(
            f"This package bundles {len(manifest['skills'])} agent skills "
            f"({', '.join(manifest['skills'])}).\n"
            f"No agent directory found in {project}. Re-run with --force to create one."
        )
        return 0

    receipt_path = project / RECEIPT
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    previous_ref = receipt.get("_ref")

    written_total = 0
    skipped_all: set[str] = set()
    labels: list[str] = []

    root = _bundled_root()
    current_keys: set[str] = set()
    for dest, label in targets:
        written, skipped = _install_to(project, dest, receipt)
        written_total += len(written)
        skipped_all.update(skipped)
        if written:
            labels.append(label)
        for skill_dir in sorted(q for q in root.iterdir() if q.is_dir()):
            for src in sorted(q for q in skill_dir.rglob("*") if q.is_file()):
                current_keys.add(str(dest / src.relative_to(root)))

    removed, orphaned, refused = _prune_obsolete(project, receipt, current_keys)
    if removed:
        print(f"Removed {len(removed)} skill file(s) withdrawn upstream.")
    if orphaned:
        print(f"Left {len(orphaned)} edited file(s) no longer bundled: {', '.join(orphaned)}")
    if refused:
        print(f"Ignored {len(refused)} receipt entr(ies) pointing outside this project.")

    receipt["_ref"] = manifest["ref"]
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")

    if written_total:
        moved = (
            f"updated {previous_ref} -> {manifest['ref']}"
            if previous_ref and previous_ref != manifest["ref"]
            else f"installed {manifest['ref']}"
        )
        print(f"Signal House agent skills {moved} for {' and '.join(labels)}.")
        print(f"  {', '.join(manifest['skills'])}")
    elif not skipped_all:
        print(f"Already up to date at {manifest['ref']}.")

    if skipped_all:
        print(f"  Left {len(skipped_all)} locally modified file(s) alone: {', '.join(sorted(skipped_all))}")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Console-script entry point for ``signalhouse-skills``.

    :param argv: Argument list, defaulting to ``sys.argv[1:]``.
    :returns: Process exit code.
    """
    parser = argparse.ArgumentParser(
        prog="signalhouse-skills",
        description="Install the bundled Signal House agent skills into this project.",
    )
    parser.add_argument("--path", default=".", help="Project directory (default: current directory)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Create the agent directories even if the project has none yet",
    )
    parser.add_argument("--list", action="store_true", help="List the bundled skills and exit")
    args = parser.parse_args(argv)

    if args.list:
        manifest_path = _bundled_root() / "VENDORED.json"
        if not manifest_path.exists():
            print("No skills bundled in this build.", file=sys.stderr)
            return 1
        manifest = json.loads(manifest_path.read_text())
        print(f"{manifest['ref']} from {manifest['source']}")
        for name in manifest["skills"]:
            print(f"  {name}")
        return 0

    return install(Path(args.path).resolve(), force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
