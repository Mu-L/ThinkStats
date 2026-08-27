# Book update workflow

Canonical source for chapter and example content is **Markdown** (`.md`), not Jupyter notebooks. Edit the `.md` files in `soln/` and `examples/`, then run the build pipeline to regenerate executed notebooks and student copies.

## Prerequisites

```bash
conda activate ThinkStats
# Dev tools (jupytext, nbmake, …) from environment-dev.yml
make create_environment_dev   # first time only
```

## When you fix a typo or revise a chapter

Example: typo in Chapter 7, section 7.5 Rank Correlation.

### 1. Edit the markdown source

```bash
$EDITOR soln/chap07.md
```

Commit the `.md` change. Do **not** hand-edit `soln/chap07.ipynb` or `nb/chap07.ipynb`.

### 2. Run the pipeline for that chapter

```bash
make update-chapter CHAPTER=chap07
```

This runs `scripts/book_pipeline.py`, which:

1. **jupytext** — `soln/chap07.md` → `soln/chap07.ipynb`
2. **nbconvert** — executes the notebook in place (refreshes outputs)
3. **strip solutions** — copies to `nb/chap07.ipynb` and removes solution cells

Equivalent direct invocation:

```bash
python scripts/book_pipeline.py chap07
```

### 3. Test

```bash
cd soln && pytest --nbmake chap07.ipynb
```

Or test all chapters:

```bash
make tests
```

### 4. Publish (when ready)

The full release still uses the top-level build scripts:

```bash
./build.sh          # soln → nb zip → Jupyter Book → gh-pages
```

Future work ([Task 2](../PROJECT_BOARD.md)): wire `build.sh` to call this markdown-first pipeline instead of copying `.ipynb` directly from `soln/`.

## Examples

Examples in `examples/` follow the same pattern:

```bash
python scripts/book_pipeline.py example:binom_skeet
```

## Generating markdown from existing notebooks (one-time migration)

If a chapter has `.ipynb` but no `.md` yet:

```bash
cd soln
jupytext --to md chap07.ipynb
```

After that, treat the `.md` file as canonical.

## File roles

| Path | Role |
|------|------|
| `soln/*.md` | **Canonical** chapter source (edit here) |
| `soln/*.ipynb` | Generated + executed solution notebooks |
| `nb/*.ipynb` | Generated student notebooks (solutions stripped) |
| `examples/*.md` | **Canonical** example source |
| `examples/*.ipynb` | Generated + executed example notebooks |

## Makefile targets

| Target | Purpose |
|--------|---------|
| `make update-chapter CHAPTER=chap07` | Rebuild one chapter from markdown |
| `make md-from-ipynb` | One-time jupytext export for chapters missing `.md` |
| `make tests` | Run nbmake on all solution notebooks |
