"""Strip solutions from executed notebooks for the student nb/ tree."""

import argparse
from glob import glob
from pathlib import Path

import nbformat as nbf

SOLUTION_PREFIX = "# Solution"
SOLUTION_REPLACEMENT = "# Solution goes here"


def strip_notebook(path: Path) -> None:
    ntbk = nbf.read(path, nbf.NO_CONVERT)

    for cell in ntbk.cells:
        if "tags" in cell["metadata"]:
            tags = cell["metadata"]["tags"]
            cell["metadata"]["tags"] = []
        else:
            tags = []

        if "outputs" in cell:
            cell["outputs"] = []

        if cell["source"].startswith(SOLUTION_PREFIX):
            cell["source"] = SOLUTION_REPLACEMENT

        if "solution" in tags:
            cell["source"] = SOLUTION_REPLACEMENT

        for tag in tags:
            if tag.startswith("chapter") or tag.startswith("section"):
                label = f"({tag})=\n"
                cell["source"] = label + cell["source"]

    nbf.write(ntbk, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Strip solutions from chapter notebooks.")
    parser.add_argument(
        "notebooks",
        nargs="*",
        help="Notebook paths (default: chap*.ipynb in current directory)",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in args.notebooks] if args.notebooks else sorted(Path(".").glob("chap*.ipynb"))
    for path in paths:
        print("Removing solutions from", path)
        strip_notebook(path)


if __name__ == "__main__":
    main()
