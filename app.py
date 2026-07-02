from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler, Category, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner + availability (created once, kept in session_state) ---
st.sidebar.header("Owner & availability")
owner_name = st.sidebar.text_input("Owner name", value="Jordan")
avail_start = st.sidebar.time_input("Available from", value=time(8, 0))
avail_end = st.sidebar.time_input("Available until", value=time(20, 0))
strategy = st.sidebar.selectbox("Scheduling strategy", ["priority", "duration"])

# Build the persistent Owner on first load; on later reruns keep its settings
# in sync with the sidebar widgets (mutating the stored object is enough).
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, avail_start, avail_end)

owner = st.session_state.owner
owner.name = owner_name
owner.available_start = avail_start
owner.available_end = avail_end

# --- Add a Pet ---
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    if st.form_submit_button("Add pet") and pet_name:
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed))
        st.success(f"Added {pet_name}.")

if owner.pets:
    st.caption("Pets: " + ", ".join(p.describe() for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a Task ---
st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet before adding tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        which = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.selectbox("Category", [c.value for c in Category])
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        use_pref = st.checkbox("Set a preferred start time")
        pref_time = st.time_input("Preferred time", value=time(8, 0))
        if st.form_submit_button("Add task") and task_title:
            pet = next(p for p in owner.pets if p.name == which)
            pet.add_task(
                Task(
                    name=task_title,
                    category=Category(category),
                    duration_minutes=int(duration),
                    priority=Priority(priority),
                    preferred_time=pref_time if use_pref else None,
                )
            )
            st.success(f"Added '{task_title}' for {which}.")

# Show every task across all pets.
rows = [
    {
        "pet": p.name,
        "task": t.name,
        "category": t.category.value,
        "min": t.duration_minutes,
        "priority": t.priority.value,
        "preferred": t.preferred_time.strftime("%H:%M") if t.preferred_time else "—",
    }
    for p in owner.pets
    for t in p.tasks
]
if rows:
    st.caption("Current tasks:")
    st.table(rows)

st.divider()

# --- Build Schedule ---
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if not owner.all_tasks():
        st.warning("No tasks to schedule yet. Add a pet and some tasks first.")
    else:
        scheduler = Scheduler(
            owner,
            available_minutes=owner.total_available_minutes(),
            strategy=strategy,
        )
        plan = scheduler.generate_plan()
        st.text(plan.to_display())
        st.caption(f"Total scheduled: {plan.total_time()} min")
        with st.expander("Why this plan?"):
            st.text(scheduler.explain())
