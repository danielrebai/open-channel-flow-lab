import streamlit as st

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Open Channel Flow Lab",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# MODULE IMPORTS
# ============================================================
from modules.module_02_specific_energy import (
    toy as energy_toy, theory as energy_theory, exercise as energy_exercise,
)
from modules.module_03_specific_force import (
    toy as force_toy, theory as force_theory, exercise as force_exercise,
)
from modules.module_04_uniform_flow import (
    toy as uniform_toy, theory as uniform_theory, exercise as uniform_exercise,
)
from modules.gradually_varied_flow import (
    toy as gvf_toy, theory as gvf_theory, exercise as gvf_exercise,
)
from modules.module_05_slope_roughness_transitions import (
    toy as transitions_toy, theory as transitions_theory, exercise as transitions_exercise,
)
from modules.module_06_intake_from_reservoir import (
    toy as intake_toy, theory as intake_theory, exercise as intake_exercise,
)

from modules.module_07_outflow_into_reservoir import (
    toy as outflow_toy, theory as outflow_theory, exercise as outflow_exercise,
)

from modules.module_08_gate import (
    toy as gate_toy, theory as gate_theory, exercise as gate_exercise,
)

from modules.module_09_downward_facing_step import (
    toy as step_toy, theory as step_theory, exercise as step_exercise,
)

# ============================================================
# GLOBAL STYLING
# ============================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    h1 {
        font-size: 2rem !important;
        font-weight: 750 !important;
        margin-bottom: 0.35rem !important;
    }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.25rem !important; }
    [data-testid="stCaptionContainer"] p {
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }
    div.stButton > button {
        font-size: 1.08rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    div.stButton > button p {
        font-size: 1.08rem !important;
        font-weight: 650 !important;
    }
    [data-testid="stColumn"] { min-width: 0 !important; }
    hr {
        margin-top: 0.75rem !important;
        margin-bottom: 0.75rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# MODULE DEFINITIONS
# ============================================================
MODULES = [
    "Home",
    "Module 01 — Specific Energy",
    "Module 02 — Specific Force",
    "Module 03 — Uniform Flow and Slope Classification",
    "Module 04 — Gradually Varied Flow",
    "Module 05 — Changes in Bed Slope and Roughness",
    "Module 06 — Intake from Reservoir",
    "Module 07 — Outflow into a Reservoir",
    "Module 08 — Flow Under a Sluice Gate",
    "Module 09 — Downward Facing Step",
]

MODULE_DATA = {
    MODULES[1]: {
        "title": "Module 01 · Specific Energy",
        "subtitle": "Prismatic rectangular channel · Specific energy",
        "description": "Explore specific energy, critical depth and alternate depths.",
        "toy": energy_toy, "theory": energy_theory, "exercise": energy_exercise,
    },
    MODULES[2]: {
        "title": "Module 02 · Specific Force",
        "subtitle": "Prismatic rectangular channel · Specific force",
        "description": "Investigate momentum, conjugate depths and hydraulic jumps.",
        "toy": force_toy, "theory": force_theory, "exercise": force_exercise,
    },
    MODULES[3]: {
        "title": "Module 03 · Uniform Flow and Slope Classification",
        "subtitle": "Uniform flow · Normal depth · Slope classification",
        "description": "Explore normal depth, channel roughness and bed slope.",
        "toy": uniform_toy, "theory": uniform_theory, "exercise": uniform_exercise,
    },
    MODULES[4]: {
        "title": "Module 04 · Gradually Varied Flow",
        "subtitle": "Prismatic rectangular channel · Steady gradually varied flow",
        "description": "Visualize gradually varied water-surface profiles.",
        "toy": gvf_toy, "theory": gvf_theory, "exercise": gvf_exercise,
    },
    MODULES[5]: {
        "title": "Module 05 · Changes in Bed Slope and Roughness",
        "subtitle": "Two connected channel reaches · Bed slope and roughness",
        "description": "Experiment with connected reaches and roughness transitions.",
        "toy": transitions_toy, "theory": transitions_theory, "exercise": transitions_exercise,
    },
    MODULES[6]: {
        "title": "Module 06 · Intake from Reservoir",
        "subtitle": "Reservoir-to-channel intake · Critical and normal flow controls",
        "description": "Study reservoir intakes into mild- and steep-slope channels.",
        "toy": intake_toy, "theory": intake_theory, "exercise": intake_exercise,
    },
    MODULES[7]: {
        "title": "Module 07 · Outflow into a Reservoir",
        "subtitle": "Channel outflow · Reservoir tailwater · Hydraulic jumps",
        "description": "Study downstream controls, M1/M2 profiles and hydraulic jumps.",
        "toy": outflow_toy, "theory": outflow_theory, "exercise": outflow_exercise,
    },
    MODULES[8]: {
        "title": "Module 08 · Flow Under a Sluice Gate",
        "subtitle": "Sluice gate · Vena contracta · Specific energy · Hydraulic jumps",
        "description": "Explore gate-controlled flow, contracted jets and specific-energy diagrams.",
        "toy": gate_toy, "theory": gate_theory, "exercise": gate_exercise,
    },
    MODULES[9]: {
        "title": "Module 09 · Downward Facing Step",
        "subtitle": "Downward step · Specific energy · Hydraulic jumps",
        "description": "Explore steep/mild slope combinations, energy transitions and hydraulic jumps.",
        "toy": step_toy, "theory": step_theory, "exercise": step_exercise,
    },
}

# ============================================================
# SESSION STATE
# ============================================================
if "selected_module" not in st.session_state:
    st.session_state["selected_module"] = "Home"
if "active_sections" not in st.session_state:
    st.session_state["active_sections"] = {}

# ============================================================
# NAVIGATION CALLBACKS
# ============================================================
def navigate_to(module_name):
    st.session_state["selected_module"] = module_name


def select_section(module_name, section_name):
    st.session_state["active_sections"][module_name] = section_name

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🌊 Open Channel Flow Lab")
    module = st.radio("Select module", options=MODULES, key="selected_module")
    st.divider()
    st.caption("Interactive experiments · Hydraulic theory · Exercises")

# ============================================================
# HOME PAGE
# ============================================================
if module == "Home":
    st.title("🌊 Open Channel Flow Lab")
    st.markdown(
        """
        ### Learn hydraulics by experimenting

        Explore open-channel flow through interactive numerical
        experiments, clear theoretical explanations and
        practical exercises.

        Choose a module to begin.
        """
    )
    st.divider()
    st.subheader("Explore the modules")
    module_names = MODULES[1:]
    for row_start in range(0, len(module_names), 2):
        columns = st.columns(2, gap="medium")
        for column_index, column in enumerate(columns):
            idx = row_start + column_index
            if idx >= len(module_names):
                continue
            module_name = module_names[idx]
            data = MODULE_DATA[module_name]
            with column:
                with st.container(border=True):
                    st.caption(f"MODULE {idx + 1:02d}")
                    st.markdown(f"### {data['title'].split(' · ', 1)[1]}")
                    st.write(data["description"])
                    st.caption("Toy · Theory · Exercise")
                    st.button(
                        f"Explore Module {idx + 1:02d}",
                        key=f"home_module_{idx + 1}",
                        use_container_width=True,
                        on_click=navigate_to,
                        args=(module_name,),
                    )
    st.stop()

# ============================================================
# SELECTED MODULE
# ============================================================
data = MODULE_DATA[module]
st.title(data["title"])
st.caption(data["subtitle"])

# ============================================================
# FULL-WIDTH SECTION NAVIGATION
# ============================================================
sections = ("Toy", "Theory", "Exercise")
active_section = st.session_state["active_sections"].get(module, "Toy")
columns = st.columns(3, gap="small")
for column, section in zip(columns, sections):
    with column:
        is_active = active_section == section
        st.button(
            section,
            key=f"nav_{module}_{section}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
            on_click=select_section,
            args=(module, section),
        )
st.divider()

# ============================================================
# RENDER ONLY THE SELECTED SECTION
# ============================================================
active_section = st.session_state["active_sections"].get(module, "Toy")
if active_section == "Toy":
    data["toy"].render()
elif active_section == "Theory":
    data["theory"].render()
elif active_section == "Exercise":
    data["exercise"].render()
