# ThinkStats Project Board

Numbered tasks for tracking work. Each task has a permanent number; add new tasks at the end. Update status as work progresses.

### Current focus (2026-08-27)

- **Task 1:** Chapter 12 intermittent missing values in Exercise 12.1 — investigating.
- **Task 2:** Redesign release tooling (GitHub canonical + SSH rsync to GTP) — not started.
- **Task 3:** Markdown-first authoring workflow (jupytext + documented build) — not started.

---

## Task 1: Chapter 12 intermittent missing values error in Exercise 12.1

**Status:** Investigating

**Context:** [GitHub issues](https://github.com/AllenDowney/ThinkStats/issues) report an intermittent failure when running tests with `pytest --nbmake` on the Chapter 12 solution notebook. The notebook runs successfully when executed manually.

**Location:** `soln/chap12.ipynb`, Exercise 12.1, cell with `seasonal_decompose(temp_series, ...)`

**Error:** `ValueError: This function does not handle missing values`

**Observations:**

- Error occurs when running tests with `pytest --nbmake`, but notebook runs successfully when executed manually
- The error happens in the solution cell that calls `seasonal_decompose(temp_series, model="additive", period=12)`
- `temp_series` is created from temperature data by transposing and stacking: `temp_us.loc[:, columns].transpose().stack()`
- When checking locally, both `data/` and `soln/` versions of the CSV file have no missing values
- Fresh download from GitHub also shows no missing values
- Current test run passes without error

**Possible causes:**

- Different pandas versions or parsing behavior between environments

**Next steps:**

- Monitor for recurrence, consider adding `.dropna()` as defensive programming if error persists

---

## Task 2: Redesign release tooling (GitHub canonical + SSH to GTP)

**Status:** Not started

**Context:** ThinkStats v3 releases today are driven by `build.sh`: commit/push solution notebooks, run `nb/build.sh` (student notebooks + `ThinkStats.zip`), then `jb/build.sh` (Jupyter Book HTML → GitHub Pages). That already makes **GitHub** the canonical host for HTML and the zip download. Older GTP-hosted books (including `thinkstats/` and `thinkstats2/` on [greenteapress.com](https://greenteapress.com)) still used bob-local staging paths like `/home/downey/public_html/greenteapress/...` + `sh back`, which cannot run from other machines. ThinkJava2 and ThinkDSP moved to a repeatable pattern: build → commit artifacts to GitHub → optional `rsync` to GTP via `Host gtp` ([ThinkJava2 Task 6](https://github.com/ChrisMayfield/ThinkJava2/blob/master/PROJECT_BOARD.md), [ThinkDSP Task 10–11](https://github.com/AllenDowney/ThinkDSP/blob/master/PROJECT_BOARD.md)).

**ThinkJava2 / ThinkDSP pattern:**

| Layer | Role |
|-------|------|
| **GitHub** | Canonical release artifacts (PDF/EPUB/zips; committed after build) |
| **GitHub Pages** | Canonical HTML for ThinkStats v3 (`allendowney.github.io/ThinkStats/`) |
| **GTP** `greenteapress.com/...` | Stable old URLs; `rsync` via `Host gtp` (`make publish-gtp`) |

**Goal:** Replace any bob-only release assumptions with: build → commit release artifacts to GitHub → optional `rsync` to GTP from any machine with SSH access.

### Scope

- [ ] Add Makefile targets: `distrib` (stage/check artifacts for GitHub commit), `publish-gtp-dry`, `publish-gtp` (rsync to GTP via `Host gtp`; no `--delete`)
- [ ] Decide which artifacts belong in the GitHub release ritual (`ThinkStats.zip`, `ThinkStatsSolutions.zip`, and any future PDF)
- [ ] Refactor or document `build.sh` / `nb/build.sh` / `jb/build.sh` so the publish steps are explicit and repeatable off bob
- [ ] README: GitHub download links as canonical; document optional GTP mirror and `~/.ssh/config` `Host gtp`
- [ ] Inventory live GTP paths for Think Stats (1e/2e static trees vs [WP landing for 3e](https://greenteapress.com/wp/think-stats-3e/))

### Deliverables

1. New distrib docs + Makefile targets (ThinkJava2-style)
2. Release artifacts committed on GitHub; optional GTP mirror documented
3. Board note on canonical vs mirrored paths

### Out of scope (for first pass)

- Rebuilding legacy Hevea HTML on GTP
- GitHub Actions deploy (direct rsync from a trusted laptop is enough for now)

---

## Task 3: Markdown-first authoring workflow

**Status:** Not started

**Context:** Today the canonical source for book content is the `.ipynb` files in `soln/` (and, for supplementary material, `.ipynb` in `examples/`). Edits happen in notebooks; `nb/build.sh` copies from `soln/` and strips solutions into `nb/`; `jb/build.sh` copies from `soln/` (and `examples/`) for the Jupyter Book HTML build. Some `.md` files already exist (partial jupytext exports in `soln/` and `examples/`), and `jupytext` is in `environment-dev.yml`, but there is no single documented pipeline and markdown is not yet authoritative.

**Goal:** Make `.md` the canonical source in `soln/` and `examples/`. Add a workflow file that records how to update the book after a fix. Generated `.ipynb` files become build artifacts, not the place to edit.

### Target pipeline

```text
Edit soln/*.md or examples/*.md
    ↓
jupytext → soln/*.ipynb (and examples/*.ipynb)
    ↓
nbconvert --execute (run notebooks; refresh outputs)
    ↓
prep / strip solutions → nb/*.ipynb (student notebooks, no solutions)
    ↓
(existing downstream: jb/build.sh → GitHub Pages, zip, tests)
```

**Authoring rule:** commit changes to `.md`; treat paired `.ipynb` as generated unless we adopt explicit jupytext pairing metadata.

### Scope

- [ ] Workflow file (e.g. `book-update.md`) documenting the edit → build → test → publish steps
- [ ] One-time or scripted jupytext conversion: ensure every chapter in `soln/` and every example in `examples/` has a canonical `.md` (jupytext front matter, consistent kernelspec)
- [ ] Build script(s) or Makefile targets: `md → ipynb` (jupytext), `execute` (nbconvert), `nb/` generation (adapt `prep_notebooks.py` / replace ad-hoc copy in `nb/build.sh`)
- [ ] jupytext pairing strategy : `.md` canonical, `.ipynb` generated and committed for convenience)
- [ ] Update `build.sh`, `Makefile`, and README so the documented workflow matches what we run
- [ ] Wire `pytest --nbmake` / CI to run against executed notebooks derived from markdown

### Deliverables

1. Workflow file a contributor can follow after fixing a chapter or example
2. Repeatable build commands (`make notebooks` or similar) implementing the pipeline above
3. `soln/` and `examples/` edited as markdown going forward; `nb/` remains solution-free output

### Out of scope (for first pass)

- Migrating `jb/` or `quarto/` to read `.md` directly (they can keep copying/converting from `soln/` for now)
- Retrofitting every historical notebook output into markdown (execute fresh on first migration)
- Replacing Jupyter Book with another HTML builder
