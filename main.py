"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's generated schedule.
Run with:  python main.py
"""

from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler, Category, Priority


def build_owner() -> Owner:
    """Create an owner with two pets and a few tasks at different times."""
    owner = Owner(
        name="Alex",
        available_start=time(8, 0),
        available_end=time(11, 0),
    )

    # --- Pet 1 ---
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=4)
    biscuit.add_task(
        Task("Morning walk", Category.WALK, 30, Priority.HIGH, preferred_time=time(8, 0))
    )
    biscuit.add_task(
        Task("Breakfast", Category.FEEDING, 10, Priority.HIGH, preferred_time=time(8, 30))
    )
    biscuit.add_task(
        Task("Grooming", Category.GROOMING, 45, Priority.LOW)
    )

    # --- Pet 2 ---
    whiskers = Pet(name="Whiskers", species="Cat", breed="Tabby", age=2)
    whiskers.add_task(
        Task("Feeding", Category.FEEDING, 10, Priority.HIGH, preferred_time=time(9, 0))
    )
    whiskers.add_task(
        Task("Medication", Category.MEDS, 5, Priority.HIGH, preferred_time=time(9, 15))
    )
    whiskers.add_task(
        Task("Play time", Category.ENRICHMENT, 20, Priority.MEDIUM)
    )

    owner.add_pet(biscuit)
    owner.add_pet(whiskers)
    return owner


def main() -> None:
    owner = build_owner()

    print(owner.describe())
    print(f"Pets: {', '.join(p.describe() for p in owner.pets)}")
    print()

    scheduler = Scheduler(owner, available_minutes=120, strategy="priority")
    plan = scheduler.generate_plan()

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    print(plan.to_display())
    print()
    print(f"Total scheduled time: {plan.total_time()} min")
    print()
    print("Why this plan:")
    print(scheduler.explain())


if __name__ == "__main__":
    main()
