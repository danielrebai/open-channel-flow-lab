"""Theory reader: edit the Markdown files, not this Python module."""
from pathlib import Path
import streamlit as st
from .figures import plots

CHAPTERS = [
    ('Governing equation', '01_governing_equation.md'),
    ('Specific energy and characteristic depths', '02_specific_energy.md'),
    ('Signs and asymptotes', '03_sign_analysis.md'),
    ('Mild-slope profiles', '04_mild_slope.md'),
    ('Steep-slope profiles', '05_steep_slope.md'),
    ('Horizontal and adverse slopes', '06_horizontal_adverse.md'),
    ('Perturbations and boundary conditions', '07_boundary_conditions.md'),
    ('Numerical integration', '08_numerical_integration.md'),
]
FIGURES = {
    1: plots.plot_energy,
    2: plots.plot_signs,
    4: plots.plot_profiles,
    6: plots.plot_waves,
}


def render():
    st.header("Theory · Gradually Varied Flow")
    st.caption("Edit individual .md files in modules/gradually_varied_flow/theory/ on GitHub.")
    titles = [title for title, _ in CHAPTERS]
    selected = st.selectbox("Chapter", titles, key="gvf_theory_chapter")
    index = titles.index(selected)
    filename = CHAPTERS[index][1]
    path = Path(__file__).parent / "theory" / filename
    st.markdown(path.read_text(encoding="utf-8"))
    if index in FIGURES:
        FIGURES[index]()
