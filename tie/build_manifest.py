#!/usr/bin/env python3
"""
build_manifest.py

Build a manifest of files for a template directory and its parent templates.

- Loads `template.yaml` from the input template directory and recursively from parent templates.
- Consolidates `template_files` with correct precedence (earlier parents < later parents < child).
- Expands directories to all files recursively (skips `.git`).
- Writes `<input_dir>/manifest.json` with POSIX-style keys relative to the chosen root (cwd by default).
- For each file, includes {"md5": "...", "last_commit": "... or null"} using local Git to resolve last commit.

Requires Python 3.10+ and PyYAML (`yaml`). If PyYAML is missing, the script exits with a friendly message.
"""

from __future__ import annotations

# standard library
import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence

try:
    # third-party
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    print(
        "ERROR: PyYAML is required. Install with:\n\n  pip install pyyaml\n",
        file=sys.stderr,
    )
    sys.exit(1)

LOG = logging.getLogger("build_manifest")


# -------------------------------
# Data helpers
# -------------------------------


@dataclass(frozen=True)
class TemplateInfo:
    """Information about a template directory and its parsed config."""

    dir_path: Path
    config: dict


# -------------------------------
# YAML / Template resolution
# -------------------------------


def load_template_yaml(dir_path: Path) -> TemplateInfo:
    """
    Load and parse `template.yaml` from a template directory.

    Raises:
        SystemExit: if the file is missing or unreadable.
    """
    yaml_path = dir_path / "template.yaml"
    if not yaml_path.is_file():
        LOG.error("Missing template.yaml: %s", yaml_path)
        raise SystemExit(f"Missing template.yaml: {yaml_path}")

    try:
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as e:
        LOG.error("Failed to parse %s: %s", yaml_path, e)
        raise SystemExit(f"Failed to parse {yaml_path}: {e}")

    return TemplateInfo(dir_path=dir_path, config=data)


def _resolve_chain(template_dir: Path, root_dir: Path, stack: List[Path], acc: List[Path]) -> None:
    """
    Depth-first resolution: earlier parents first, later parents next, then the current template last.
    Detects cycles using `stack`.
    """
    info = load_template_yaml(template_dir)
    parents: Sequence[str] = info.config.get("template_parents", []) or []

    # Cycle detection
    if template_dir in stack:
        cycle = " -> ".join(p.as_posix() for p in (*stack, template_dir))
        raise SystemExit(f"Cycle detected in template_parents: {cycle}")

    stack.append(template_dir)
    try:
        for parent_name in parents:
            parent_dir = (root_dir / parent_name).resolve()
            if not parent_dir.is_dir():
                raise SystemExit(f"Parent template directory not found: {parent_dir}")
            _resolve_chain(parent_dir, root_dir, stack, acc)
        acc.append(template_dir)
    finally:
        stack.pop()


def resolve_templates(input_dir: Path, root_dir: Path) -> List[Path]:
    """
    Return template directories in precedence order:
        [earliest_parent, ..., latest_parent, child_template]
    """
    acc: List[Path] = []
    _resolve_chain(input_dir.resolve(), root_dir.resolve(), [], acc)
    return acc


# -------------------------------
# File iteration / expansion
# -------------------------------


def iter_template_files(template_dir: Path, relative_paths: Sequence[str]) -> Iterator[Path]:
    """
    Yield absolute file Paths for each entry:
      - If entry is a file: yield it.
      - If entry is a directory: recursively yield all contained files.
    Skips any `.git` directories.
    """
    for rel in relative_paths:
        src = (template_dir / rel).resolve()
        if src.is_file():
            yield src
        elif src.is_dir():
            for root, dirs, files in os.walk(src, topdown=True):
                # prune .git from traversal
                dirs[:] = [d for d in dirs if d != ".git"]
                for fn in files:
                    yield Path(root) / fn
        else:
            LOG.warning("Referenced path does not exist (skipping): %s", src)


# -------------------------------
# Hashing / Git helpers
# -------------------------------


def compute_md5(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute MD5 hash of a file."""
    md5 = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            md5.update(chunk)
    return md5.hexdigest()


def git_repo_root(start_dir: Path) -> Optional[Path]:
    """Return the Git repository root, or None if not in a repo."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(start_dir), "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        return Path(out.strip())
    except Exception:
        return None


def git_last_commit(repo_root: Path, file_path: Path) -> Optional[str]:
    """
    Return last commit SHA for file_path using local Git, or None if unavailable.
    file_path must be inside repo_root.
    """
    try:
        rel = file_path.resolve().relative_to(repo_root.resolve())
    except Exception:
        return None

    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_root), "log", "-n", "1", "--pretty=format:%H", "--", str(rel)],
            text=True,
            stderr=subprocess.STDOUT,
        )
        sha = out.strip()
        return sha or None
    except Exception:
        return None


# -------------------------------
# Manifest builder
# -------------------------------


def build_manifest_map(files: List[Path], root_dir: Path) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Build a map:
      key   -> POSIX relative path from root_dir
      value -> {"md5": <md5>, "last_commit": <sha or None>}
    """
    root_dir = root_dir.resolve()
    repo_root = git_repo_root(root_dir)

    manifest: Dict[str, Dict[str, Optional[str]]] = {}
    for abs_path in files:
        try:
            key_path = abs_path.resolve().relative_to(root_dir)
        except Exception:
            LOG.warning("File is outside root_dir, skipping: %s", abs_path)
            continue

        key = key_path.as_posix()
        md5 = compute_md5(abs_path)
        last_commit = git_last_commit(repo_root, abs_path) if repo_root else None

        manifest[key] = {"md5": md5, "last_commit": last_commit}

    # stable order
    return {k: manifest[k] for k in sorted(manifest.keys())}


# -------------------------------
# Orchestration
# -------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build manifest.json for a template directory and its parent templates."
    )
    ap.add_argument("input_dir", help="Child template directory (e.g., tcv)")
    ap.add_argument(
        "--root", default=".", help="Templates root (default: current working directory)"
    )
    ap.add_argument("--debug", action="store_true", help="Enable DEBUG logging")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    root_dir = Path(args.root).resolve()
    input_dir = Path(args.input_dir).resolve()

    if not (input_dir / "template.yaml").is_file():
        raise SystemExit(f"Missing template.yaml: {input_dir / 'template.yaml'}")

    # Resolve templates with precedence order
    LOG.debug("Resolving templates from: %s (root=%s)", input_dir, root_dir)
    chain = resolve_templates(input_dir, root_dir)
    LOG.info("Template order (low -> high precedence): %s", " -> ".join(p.name for p in chain))

    # Consolidate files with precedence:
    # earlier parents first, later parents next, child last — later entries override earlier ones
    consolidated: Dict[str, Path] = {}

    for tmpl_dir in chain:
        info = load_template_yaml(tmpl_dir)
        rel_paths: Sequence[str] = info.config.get("template_files", []) or []

        LOG.debug("Collecting from %s: %d entries", tmpl_dir, len(rel_paths))
        for abs_file in iter_template_files(tmpl_dir, rel_paths):
            try:
                # Manifest keys must be POSIX paths relative to root_dir
                key = abs_file.resolve().relative_to(root_dir.resolve()).as_posix()
            except Exception:
                LOG.warning("Skipping file outside root_dir: %s", abs_file)
                continue
            # Precedence: later templates overwrite the same key
            consolidated[key] = abs_file

    # Build manifest map
    print("Consolidated files:", len(consolidated))
    # Write consolidated keys to a file for inspection
    files_ordered = [consolidated[k] for k in sorted(consolidated.keys())]
    manifest = build_manifest_map(files_ordered, root_dir=root_dir)
    # Remove the first directory from each key in the manifest
    manifest = {
        "/".join(k.split("/")[1:]): v
        for k, v in manifest.items()
        if len(k.split("/")) > 1
    }


    # Write manifest.json inside input directory
    output_path = input_dir / "manifest.json"
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    LOG.info("Wrote %s (%d entries)", output_path, len(manifest))


if __name__ == "__main__":
    main()


# -------------------------------
# Usage
# -------------------------------
# Example:
#   python build_manifest.py tcv
#   python build_manifest.py tcv --root .
#   python build_manifest.py tcv --debug
#
# Output is written to: tcv/manifest.json
