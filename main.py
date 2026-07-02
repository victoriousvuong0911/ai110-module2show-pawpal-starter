"""PawPal+ demo script.

Builds a small owner/pet/task setup and exercises the scheduling, sorting,
and filtering methods in the terminal.
Run with:  python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler, Category, Priority


def build_owner() -> Owner:
    """Create an owner with two pets whose tasks are added OUT OF ORDER."""
    owner = Owner(
        name="Alex",
        available_start=time(8, 0),
        available_end=time(11, 0),
    )

    # --- Pet 1 --- (deliberately not in time order)
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=4)
    biscuit.add_task(
        Task("Breakfast", Category.FEEDING, 10, Priority.HIGH, preferred_time=time(8, 30))
    )
    biscuit.add_task(
        Task("Grooming", Category.GROOMING, 45, Priority.LOW)  # no preferred time
    )
    biscuit.add_task(
        Task("Morning walk", Category.WALK, 30, Priority.HIGH, preferred_time=time(8, 0))
    )

    # --- Pet 2 --- (also scrambled)
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby", age=2)
    whiskers.add_task(
        Task("Medication", Category.MEDS, 5, Priority.HIGH, preferred_time=time(9, 15))
    )
    whiskers.add_task(
        Task("Play time", Category.ENRICHMENT, 20, Priority.MEDIUM)  # no preferred time
    )
    whiskers.add_task(
        Task("Feeding", Category.FEEDING, 10, Priority.HIGH, preferred_time=time(9, 0))
    )

    # CONFLICT: Biscuit's vitamins are requested at 09:00 — the same time as
    # Whiskers' feeding above. The scheduler should warn about this clash.
    biscuit.add_task(
        Task("Vitamins", Category.MEDS, 10, Priority.MEDIUM, preferred_time=time(9, 0))
    )

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    # Mark a couple of tasks done so the completion filter has something to show.
    biscuit.tasks[2].mark_complete()   # Morning walk
    whiskers.tasks[0].mark_complete()  # Medication

    return owner


def main() -> None:
    owner = build_owner()
    scheduler = Scheduler(owner, available_minutes=120, strategy="priority")

    print(owner.describe())
    print(f"Pets: {', '.join(p.describe() for p in owner.pets)}")

    # --- Sorting: tasks were added scrambled; show them in time order ---
    print("\n" + "=" * 44)
    print("Tasks added (insertion order):")
    print("=" * 44)
    for t in owner.all_tasks():
        stamp = t.preferred_time.strftime("%H:%M") if t.preferred_time else "  —  "
        print(f"  {stamp}  {t.name}")

    print("\n" + "=" * 44)
    print("Sorted by time (sort_by_time):")
    print("=" * 44)
    for t in scheduler.sort_by_time(owner.all_tasks()):
        stamp = t.preferred_time.strftime("%H:%M") if t.preferred_time else "  —  "
        print(f"  {stamp}  {t.name}")

    # --- Filtering: completion status and pet name (find_tasks) ---
    print("\n" + "=" * 44)
    print("Filtering (find_tasks):")
    print("=" * 44)
    print("  Completed :", [t.name for t in owner.find_tasks(completed=True)])
    print("  Pending   :", [t.name for t in owner.find_tasks(completed=False)])
    print("  Biscuit's :", [t.name for t in owner.find_tasks(pet_name="Biscuit")])
    print(
        "  Whiskers pending:",
        [t.name for t in owner.find_tasks(completed=False, pet_name="Whiskers")],
    )

    # --- Conflict detection (two tasks at the same time) ---
    plan = scheduler.generate_plan()

    print("\n" + "=" * 44)
    print("Conflict detection (detect_conflicts):")
    print("=" * 44)
    if plan.warnings:
        for warning in plan.warnings:
            print("  WARNING: " + warning)
    else:
        print("  No conflicts detected.")

    # --- The generated plan (skips completed tasks automatically) ---
    print("\n" + "=" * 44)
    print("Today's Schedule")
    print("=" * 44)
    print(plan.to_display())
    print(f"\nTotal scheduled time: {plan.total_time()} min")


if __name__ == "__main__":
    main()
