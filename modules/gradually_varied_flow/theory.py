"""Render the entire theory from one editable Markdown file.

Move the <!-- PLOT: name --> markers within theory.md to position figures.
Available names: energy, signs, profiles, waves.
"""
from pathlib import Path
import re
import streamlit as st
from .figures import plots

PLOT_FUNCTIONS = {
    "energy": plots.plot_energy,
    "signs": plots.plot_signs,
    "profiles": plots.plot_profiles,
    "waves": plots.plot_waves,
}
PLOT_PATTERN = re.compile(r"<!--\s*PLOT:\s*([a-z_]+)\s*-->")


def render():
    st.header("Theory · Gradually Varied Flow")
    st.caption("One editable file: modules/gradually_varied_flow/theory.md")
    source = Path(__file__).with_name("theory.md")
    content = source.read_text(encoding="utf-8")
    pieces = PLOT_PATTERN.split(content)
    for index, piece in enumerate(pieces):
        if index % 2 == 0:
            if piece.strip():
                st.markdown(piece)
        else:
            draw = PLOT_FUNCTIONS.get(piece)
            if draw is None:
                st.warning(f"Unknown figure marker: {piece}")
            else:
                draw()
