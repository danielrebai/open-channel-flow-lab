
import streamlit as st

from modules.gradually_varied_flow import toy as gvf_toy
from modules.gradually_varied_flow import theory as gvf_theory
from modules.gradually_varied_flow import exercise as gvf_exercise

from modules.module_02_specific_energy import toy as energy_toy
from modules.module_02_specific_energy import theory as energy_theory
from modules.module_02_specific_energy import exercise as energy_exercise

from modules.module_03_specific_force import toy as force_toy
from modules.module_03_specific_force import theory as force_theory
from modules.module_03_specific_force import exercise as force_exercise


st.set_page_config(
    page_title="Open Channel Flow Lab",
    page_icon="🌊",
    layout="wide",
)

st.title("Open Channel Flow Lab")

module = st.sidebar.selectbox(
    "Select module",
    [
        "Module 01 — Gradually Varied Flow",
        "Module 02 — Specific Energy",
        "Module 03 — Specific Force",
    ],
)

if module.startswith("Module 01"):
    st.caption(
        "Module 01 · Prismatic rectangular channel · "
        "Steady gradually varied flow"
    )
    toy, theory, exercise = gvf_toy, gvf_theory, gvf_exercise

elif module.startswith("Module 02"):
    st.caption(
        "Module 02 · Prismatic rectangular channel · "
        "Specific energy"
    )
    toy, theory, exercise = energy_toy, energy_theory, energy_exercise

else:
    st.caption(
        "Module 03 · Prismatic rectangular channel · "
        "Specific force"
    )
    toy, theory, exercise = force_toy, force_theory, force_exercise


toy_tab, theory_tab, exercise_tab = st.tabs(
    ["Toy", "Theory", "Exercise"]
)

with toy_tab:
    toy.render()

with theory_tab:
    theory.render()

with exercise_tab:
    exercise.render()
