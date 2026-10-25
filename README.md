# Open Channel Flow Lab — v15

## Editing the theory

Each chapter lives in `modules/gradually_varied_flow/theory/*.md`.
Open the file on GitHub, click the pencil icon, edit Markdown and LaTeX (`$...$` or `$$...$$`), and commit.
The Theory tab uses a chapter selector. No Python editing is needed for text or equations.

## Editing figures

Plotly figures live in `modules/gradually_varied_flow/figures/plots.py`, with one function per figure. The Theory reader maps them to chapters in `theory.py`.

## Code organization

- `app.py`: navigation only
- `toy.py`: interactive hydraulic plot
- `exercise.py`: random exercise generator and worked solutions
- `hydraulics.py`: shared formulas available for future refactoring
- `theory.py`: chapter reader

The Toy and Exercise implementations were moved from v14 without intentional numerical changes. The formulas in `hydraulics.py` are a reusable API; migration of all existing calculations to it is deferred to avoid changing results during this structural refactor.

Deploy with `app.py` as the Streamlit entry point. Upload the **entire folder tree**, not just `app.py`.
