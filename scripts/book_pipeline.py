#!/usr/bin/env python3
"""Build soln/ and nb/ notebooks from canonical markdown sources."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOLN_DIR = REPO_ROOT / "soln"
NB_DIR = REPO_ROOT / "nb"
EXAMPLES_DIR = REPO_ROOT / "examples"
PREP_SCRIPT = REPO_ROOT / "nb" / "prep_notebooks.py"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd or REPO_ROOT, check=True)


def chapter_stem(name: str) -> str:
    stem = Path(name).stem
    if not stem.startswith("chap"):
        raise ValueError(f"Expected chapter name like chap07, got {name!r}")
    return stem


def md_to_ipynb(md_path: Path) -> Path:
    ipynb_path = md_path.with_suffix(".ipynb")
    run(["jupytext", "--to", "ipynb", str(md_path)], cwd=md_path.parent)
    return ipynb_path


def execute_notebook(ipynb_path: Path) -> None:
    run(
        [
            "jupyter",
            "nbconvert",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=600",
            str(ipynb_path.name),
        ],
        cwd=ipynb_path.parent,
    )


def build_student_notebook(stem: str) -> Path:
    soln_ipynb = SOLN_DIR / f"{stem}.ipynb"
    if not soln_ipynb.exists():
        raise FileNotFoundError(soln_ipynb)

    NB_DIR.mkdir(exist_ok=True)
    student_ipynb = NB_DIR / f"{stem}.ipynb"
    shutil.copy2(soln_ipynb, student_ipynb)
    run([sys.executable, str(PREP_SCRIPT), str(student_ipynb)])
    return student_ipynb


def build_chapter(stem: str, *, execute: bool = True, student: bool = True) -> None:
    md_path = SOLN_DIR / f"{stem}.md"
    if not md_path.exists():
        raise FileNotFoundError(f"Missing canonical source: {md_path}")

    print(f"\n=== {stem}: md → ipynb ===")
    ipynb_path = md_to_ipynb(md_path)

    if execute:
        print(f"\n=== {stem}: execute ===")
        execute_notebook(ipynb_path)

    if student:
        print(f"\n=== {stem}: student notebook ===")
        build_student_notebook(stem)


def build_example(stem: str, *, execute: bool = True) -> None:
    md_path = EXAMPLES_DIR / f"{stem}.md"
    if not md_path.exists():
        raise FileNotFoundError(f"Missing canonical source: {md_path}")

    print(f"\n=== example {stem}: md → ipynb ===")
    ipynb_path = md_to_ipynb(md_path)

    if execute:
        print(f"\n=== example {stem}: execute ===")
        execute_notebook(ipynb_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update notebooks from canonical markdown.")
    parser.add_argument(
        "chapters",
        nargs="+",
        help="Chapter stems (e.g. chap07) or example:name (e.g. example:binom_skeet)",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Convert markdown to ipynb without executing",
    )
    parser.add_argument(
        "--no-student",
        action="store_true",
        help="Skip generating the solution-stripped nb/ copy",
    )
    args = parser.parse_args()

    for item in args.chapters:
        if item.startswith("example:"):
            build_example(item.split(":", 1)[1], execute=not args.no_execute)
        else:
            build_chapter(
                chapter_stem(item),
                execute=not args.no_execute,
                student=not args.no_student,
            )


if __name__ == "__main__":
    main()
