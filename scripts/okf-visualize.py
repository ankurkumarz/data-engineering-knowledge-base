#!/usr/bin/env python3
"""Generate Google's OKF graph viewer for this repository's concept pages."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


UPSTREAM_REPOSITORY = "https://github.com/GoogleCloudPlatform/open-knowledge-format.git"
UPSTREAM_COMMIT = "ad30107c31c06aec8a7d5636e0d1058118604e6f"
RESERVED_FILENAMES = {"index.md", "log.md", "ingest-log.md", "graph.md"}


def run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def output(command: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.check_output(
        command, cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def ensure_upstream(checkout: Path, *, offline: bool) -> Path:
    generator = checkout / "src/reference_agent/viewer/generator.py"
    if not checkout.exists():
        if offline:
            raise SystemExit(
                f"Pinned OKF visualizer is not cached at {checkout}; "
                "run once without --offline."
            )
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "--quiet", str(checkout)])
        run(["git", "remote", "add", "origin", UPSTREAM_REPOSITORY], cwd=checkout)

    if not (checkout / ".git").is_dir():
        raise SystemExit(f"Upstream path is not a Git checkout: {checkout}")

    revision = ""
    try:
        revision = output(["git", "rev-parse", "HEAD"], cwd=checkout)
    except subprocess.CalledProcessError:
        pass

    if revision != UPSTREAM_COMMIT:
        if offline:
            raise SystemExit(
                f"Cached OKF visualizer is at {revision or 'no revision'}, "
                f"not pinned commit {UPSTREAM_COMMIT}."
            )
        run(["git", "fetch", "--depth", "1", "origin", UPSTREAM_COMMIT], cwd=checkout)
        run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], cwd=checkout)

    if not generator.is_file():
        raise SystemExit(f"Google OKF visualizer module not found at {generator}")
    return checkout / "src"


def frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return {}
    data = yaml.safe_load("\n".join(lines[1:end])) or {}
    return data if isinstance(data, dict) else {}


def stage_concepts(bundle: Path, staging: Path) -> int:
    count = 0
    for source in sorted(bundle.rglob("*.md")):
        if source.name in RESERVED_FILENAMES:
            continue
        if not frontmatter(source).get("type"):
            continue
        destination = staging / source.relative_to(bundle)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        count += 1
    return count


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate docs and generate Google's interactive OKF graph viewer."
    )
    parser.add_argument("--bundle", type=Path, default=Path("docs"))
    parser.add_argument("--out", type=Path, default=Path("html/okf-viz.html"))
    parser.add_argument("--name", default="Data Engineering Knowledge Base")
    parser.add_argument(
        "--upstream-dir",
        type=Path,
        default=Path(".okf-tools/open-knowledge-format"),
        help="Pinned upstream checkout/cache path.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Fail instead of fetching the pinned upstream revision when it is absent.",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Generate without first running scripts/okf-verify.py.",
    )
    return parser.parse_args()


def main() -> int:
    args = arguments()
    repository_root = Path(__file__).resolve().parent.parent
    bundle = (repository_root / args.bundle).resolve()
    out_path = (repository_root / args.out).resolve()
    upstream_dir = (repository_root / args.upstream_dir).resolve()

    if not bundle.is_dir():
        raise SystemExit(f"Bundle directory not found: {bundle}")

    if not args.skip_verify:
        run([sys.executable, str(repository_root / "scripts/okf-verify.py")], cwd=repository_root)

    upstream_source = ensure_upstream(upstream_dir, offline=args.offline)
    sys.path.insert(0, str(upstream_source))
    from reference_agent.viewer import generate_visualization

    with tempfile.TemporaryDirectory(prefix="okf-visualizer-") as temporary:
        staged_bundle = Path(temporary) / "bundle"
        staged_bundle.mkdir()
        staged = stage_concepts(bundle, staged_bundle)
        if not staged:
            raise SystemExit(f"No OKF concept pages found under {bundle}")
        stats = generate_visualization(
            staged_bundle,
            out_path,
            bundle_name=args.name,
        )

    print(
        f"Wrote {stats['concepts']} concepts and {stats['edges']} links "
        f"to {out_path.relative_to(repository_root)} "
        f"using Google OKF {UPSTREAM_COMMIT[:12]}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
