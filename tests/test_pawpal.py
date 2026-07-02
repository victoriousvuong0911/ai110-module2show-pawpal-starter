"""Basic unit tests for PawPal+ core objects."""

import sys
from pathlib import Path

# pawpal_system.py lives in the project root (one level up from tests/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Pet, Task, Category, Priority


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
