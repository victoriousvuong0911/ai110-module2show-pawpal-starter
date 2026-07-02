"""Basic unit tests for PawPal+ core objects."""

import sys
from datetime import date, time, timedelta
from pathlib import Path

# pawpal_system.py lives in the project root (one level up from tests/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Owner, Pet, Task, Scheduler, Category, Priority


def test_task_completion():
    # Verify that mark_complete() actually changes the task's status.
    task = Task("Morning walk", Category.WALK, 30, Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition_increases_count():
    # Verify that adding a task to a Pet increases that pet's task count.
    pet = Pet(name="Biscuit", species="Dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", Category.FEEDING, 10, Priority.HIGH))

    assert len(pet.tasks) == 1


def _make_scheduler(*pets: Pet) -> Scheduler:
    """Helper: build an Owner with the given pets and a scheduler over them."""
    owner = Owner("Alex", available_start=time(8, 0), available_end=time(20, 0))
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner, available_minutes=owner.total_available_minutes())


def test_sorting_returns_chronological_order():
    # Sorting correctness: tasks come back ordered by preferred_time (untimed last).
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task("Feeding", Category.FEEDING, 10, preferred_time=time(9, 0)))
    pet.add_task(Task("Grooming", Category.GROOMING, 30))  # no preferred time
    pet.add_task(Task("Walk", Category.WALK, 30, preferred_time=time(8, 0)))
    scheduler = _make_scheduler(pet)

    ordered = scheduler.sort_by_time(pet.tasks)

    assert [t.name for t in ordered] == ["Walk", "Feeding", "Grooming"]


def test_recurrence_creates_next_day_instance():
    # Recurrence logic: completing a daily task adds a fresh one for tomorrow.
    pet = Pet(name="Biscuit", species="Dog")
    walk = Task("Walk", Category.WALK, 30, recurrence="daily", due_date=date(2026, 7, 2))
    pet.add_task(walk)

    upcoming = pet.complete_task(walk)

    assert walk.completed is True             # original marked done
    assert upcoming is not None               # a new instance was created
    assert upcoming.completed is False        # and it's pending
    assert upcoming.due_date == date(2026, 7, 3)  # scheduled for the next day
    assert len(pet.tasks) == 2                # auto-added to the pet


def test_conflict_detection_flags_duplicate_times():
    # Conflict detection: two fixed-time tasks at the same time raise a warning.
    dog = Pet(name="Biscuit", species="Dog")
    cat = Pet(name="Mochi", species="Cat")
    dog.add_task(Task("Vitamins", Category.MEDS, 10, preferred_time=time(9, 0)))
    cat.add_task(Task("Feeding", Category.FEEDING, 10, preferred_time=time(9, 0)))
    scheduler = _make_scheduler(dog, cat)

    warnings = scheduler.detect_conflicts(dog.tasks + cat.tasks)

    assert len(warnings) == 1
    assert "Vitamins" in warnings[0] and "Feeding" in warnings[0]


def test_no_conflict_when_times_do_not_overlap():
    # Sanity check: non-overlapping fixed times produce no warnings.
    pet = Pet(name="Biscuit", species="Dog")
    pet.add_task(Task("Walk", Category.WALK, 30, preferred_time=time(8, 0)))
    pet.add_task(Task("Feeding", Category.FEEDING, 10, preferred_time=time(9, 0)))
    scheduler = _make_scheduler(pet)

    assert scheduler.detect_conflicts(pet.tasks) == []
