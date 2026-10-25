import streamlit as st
from modules.gradually_varied_flow import toy, theory, exercise

st.set_page_config(page_title="Open Channel Flow Lab", page_icon="🌊", layout="wide")
st.title("🌊 Open Channel Flow Lab · v15")
st.caption("Module 01 · Prismatic rectangular channel · Steady gradually varied flow")

toy_tab, theory_tab, exercise_tab = st.tabs(["Toy", "Theory", "Exercise"])
with toy_tab:
    toy.render()
with theory_tab:
    theory.render()
with exercise_tab:
    exercise.render()
