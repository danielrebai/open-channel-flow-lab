# Open Channel Flow Lab — v16

## Write all theory in one file

Open **`modules/gradually_varied_flow/theory.md`** on GitHub and click the pencil icon to edit. This is the complete theory for the Gradually Varied Flow module, in one continuous Markdown file with LaTeX equations.

To insert or reposition an interactive figure, put one of these markers on its own line:

```markdown
<!-- PLOT: energy -->
<!-- PLOT: signs -->
<!-- PLOT: profiles -->
<!-- PLOT: waves -->
```

The Streamlit renderer in `modules/gradually_varied_flow/theory.py` replaces each marker with the matching Plotly figure from `figures/plots.py`. You can edit the prose without editing Python.

## Structure

- `app.py` — navigation (Toy / Theory / Exercise)
- `modules/gradually_varied_flow/toy.py` — interactive simulator
- `modules/gradually_varied_flow/theory.md` — **all theory in one file**
- `modules/gradually_varied_flow/theory.py` — Markdown and figure renderer
- `modules/gradually_varied_flow/exercise.py` — exercise generator and solutions
- `modules/gradually_varied_flow/hydraulics.py` — shared hydraulic formulas for future refactoring
- `modules/gradually_varied_flow/figures/plots.py` — independent figure functions

## Deploy

Upload the **entire folder tree** to GitHub, retaining the paths. Delete the obsolete `modules/gradually_varied_flow/theory/` folder from the old v15 repository, so there are no confusing duplicate theory files. Streamlit entry point: `app.py`.

The Toy and Exercise code is unchanged from v15; the Theory now displays in a single scrolling page. This release has been syntax-checked but not deployed to Streamlit Cloud.
