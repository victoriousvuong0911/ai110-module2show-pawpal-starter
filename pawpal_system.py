"""PawPal+ system implementation.

Classes generated from the UML draft (diagrams/uml_draft.mmd) and fleshed out
with scheduling logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from enum import Enum


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


# Lower number == more important, so tasks sort HIGH -> MEDIUM -> LOW.
_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


def _to_minutes(t: time) -> int:
    """Convert a time-of-day into minutes since midnight."""
    return t.hour * 60 + t.minute


def _to_time(minutes: int) -> time:
    """Convert minutes since midnight back into a time-of-day (wraps at 24h)."""
    minutes %= 24 * 60
    return time(hour=minutes // 60, minute=minutes % 60)


@dataclass
class Task:
    """A single pet care activity."""

    name: str
    category: Category
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    recurrence: str = "daily"          # "daily" | "weekly" | "once"
    preferred_time: time | None = None
    completed: bool = False
    due_date: date | None = None       # the specific day this instance is for

    def is_due_today(self, day: date) -> bool:
        """Return True if this task is due on the given day."""
        if self.due_date is not None:
            return self.due_date == day
        # Undated template: fall back to the recurrence rule.
        if self.recurrence == "daily":
            return True
        if self.recurrence == "once":
            return True
        if self.recurrence == "weekly":
            # Simple rule: weekly tasks land on Mondays.
            return day.weekday() == 0
        return True

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Build the next scheduled instance of a recurring task.

        Copies this task with ``completed`` reset to False and ``due_date``
        advanced by the recurrence interval (daily = +1 day, weekly = +7 days).
        The advance is measured from ``due_date`` if set, otherwise from today.

        Returns:
            A new Task for the next occurrence, or None for a "once" task
            (or any non-recurring value) since it does not repeat.
        """
        if self.recurrence == "daily":
            step = 1
        elif self.recurrence == "weekly":
            step = 7
        else:  # "once" or unknown — does not repeat
            return None
        base = self.due_date or date.today()
        return replace(self, completed=False, due_date=base + timedelta(days=step))

    def describe(self) -> str:
        """Return a human-readable summary of the task."""
        return f"{self.name} ({self.duration_minutes} min) [priority: {self.priority.value}]"


@dataclass
class Pet:
    """An animal being cared for."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and roll a recurring task forward.

        Flips the task's status, then asks it for its next occurrence; if one
        exists (daily/weekly), it is appended to this pet's task list so the
        chore reappears on its next date.

        Args:
            task: A task already belonging to this pet.

        Returns:
            The newly created next-occurrence Task, or None if the task does
            not repeat.
        """
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.add_task(upcoming)
        return upcoming

    def remove_task(self, task: Task) -> None:
        """Detach a care task from this pet (no-op if not present)."""
        if task in self.tasks:
            self.tasks.remove(task)

    def tasks_by_priority(self) -> list[Task]:
        """Return this pet's tasks ordered by priority, then duration."""
        return sorted(
            self.tasks,
            key=lambda t: (_PRIORITY_ORDER[t.priority], t.duration_minutes),
        )

    def describe(self) -> str:
        """Return a human-readable summary of the pet."""
        kind = self.breed or self.species
        return f"{self.name} the {kind} ({len(self.tasks)} task(s))"


@dataclass
class Owner:
    """The person the daily plan is built for."""

    name: str
    available_start: time
    available_end: time
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def find_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return this owner's tasks, optionally filtered by status and/or pet.

        Both filters are independent and compose; a value of None means "do not
        filter on this field". Note that ``completed=False`` is a real filter
        (pending tasks only), which is why membership is tested with ``is not
        None`` rather than truthiness.

        Args:
            completed: If set, keep only tasks whose ``completed`` flag matches.
            pet_name: If set, keep only tasks belonging to the pet with this name.

        Returns:
            A flat list of matching Task objects across all pets.
        """
        result: list[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                result.append(task)
        return result

    def total_available_minutes(self) -> int:
        """Return the size of the owner's daily availability window in minutes."""
        return _to_minutes(self.available_end) - _to_minutes(self.available_start)

    def describe(self) -> str:
        """Return a human-readable summary of the owner."""
        start = self.available_start.strftime("%H:%M")
        end = self.available_end.strftime("%H:%M")
        return f"{self.name} — {len(self.pets)} pet(s), available {start}–{end}"


@dataclass
class ScheduledTask:
    """A task placed into a concrete time slot within a plan."""

    task: Task
    start_time: time
    end_time: time

    def overlaps(self, other: "ScheduledTask") -> bool:
        """Return True if this slot overlaps another scheduled task."""
        return self.start_time < other.end_time and other.start_time < self.end_time

    def describe(self) -> str:
        """Return a formatted line, e.g. '08:00 — Morning walk (30 min) [priority: high]'."""
        return (
            f"{self.start_time.strftime('%H:%M')} — {self.task.name} "
            f"({self.task.duration_minutes} min) [priority: {self.task.priority.value}]"
        )


@dataclass
class DailyPlan:
    """The generated, time-stamped schedule for a single day."""

    date: date
    entries: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reasoning: str = ""

    def add_entry(self, entry: ScheduledTask) -> None:
        """Add a scheduled task to the plan."""
        self.entries.append(entry)

    def total_time(self) -> int:
        """Return the total scheduled minutes across all entries."""
        return sum(e.task.duration_minutes for e in self.entries)

    def unscheduled(self) -> list[Task]:
        """Return tasks that could not be scheduled."""
        return self.skipped_tasks

    def to_display(self) -> str:
        """Return a display-ready representation of the plan for the UI."""
        lines = [f"Daily plan for {self.date.isoformat()}:"]
        if self.entries:
            for entry in self.entries:
                lines.append("  " + entry.describe())
        else:
            lines.append("  (nothing scheduled)")
        if self.skipped_tasks:
            lines.append("Skipped:")
            for task in self.skipped_tasks:
                lines.append("  - " + task.name)
        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append("  - " + warning)
        return "\n".join(lines)


class Scheduler:
    """Engine that turns an owner's tasks + constraints into a DailyPlan."""

    def __init__(self, owner: Owner, available_minutes: int, strategy: str = "priority"):
        """Set up the scheduler for an owner with a time budget and sort strategy."""
        self.owner = owner
        self.available_minutes = available_minutes
        self.strategy = strategy
        self._last_plan: DailyPlan | None = None

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by the active strategy (shortest-first, or priority then duration)."""
        if self.strategy == "duration":
            return sorted(tasks, key=lambda t: t.duration_minutes)
        return sorted(
            tasks,
            key=lambda t: (
                _PRIORITY_ORDER[t.priority],
                t.duration_minutes,
                _to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
            ),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Order tasks chronologically by their preferred start time.

        Uses ``sorted`` with a key that converts each ``preferred_time`` to
        minutes-since-midnight. Tasks without a preferred time get a sentinel
        key (end of day) so they sort last instead of raising when compared
        against None.

        Args:
            tasks: The tasks to order (not mutated).

        Returns:
            A new list sorted earliest-first, untimed tasks trailing.
        """
        return sorted(
            tasks,
            key=lambda t: _to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
        )

    def filter_tasks(self, tasks: list[Task]) -> list[Task]:
        """Keep, in order, only the tasks that fit the available-minutes budget."""
        kept: list[Task] = []
        used = 0
        for task in tasks:
            if used + task.duration_minutes <= self.available_minutes:
                kept.append(task)
                used += task.duration_minutes
        return kept

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Drop overlapping fixed-time tasks (keeping higher priority); pass untimed tasks through."""
        timed = sorted(
            (t for t in tasks if t.preferred_time is not None),
            key=lambda t: _to_minutes(t.preferred_time),
        )
        untimed = [t for t in tasks if t.preferred_time is None]

        kept: list[Task] = []
        for task in timed:
            if kept:
                prev = kept[-1]
                prev_end = _to_minutes(prev.preferred_time) + prev.duration_minutes
                if _to_minutes(task.preferred_time) < prev_end:
                    # Conflict: keep whichever has the higher priority.
                    if _PRIORITY_ORDER[task.priority] < _PRIORITY_ORDER[prev.priority]:
                        kept[-1] = task
                    continue
            kept.append(task)

        return kept + untimed

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect fixed-time tasks whose slots overlap and describe each clash.

        A lightweight O(n^2) pairwise scan over only the tasks that have a
        ``preferred_time``. Two tasks conflict when their
        ``[start, start + duration)`` minute-intervals overlap, so it catches
        both exact matches and partial overlaps, within a pet or across pets.
        It reports problems as text rather than raising, so a clash never
        crashes plan generation.

        Args:
            tasks: The candidate tasks to check for time collisions.

        Returns:
            A list of human-readable warning strings (empty if none conflict).
        """
        timed = [t for t in tasks if t.preferred_time is not None]

        def pet_of(task: Task) -> str:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    return pet.name
            return "?"

        warnings: list[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]
                a_start = _to_minutes(a.preferred_time)
                a_end = a_start + a.duration_minutes
                b_start = _to_minutes(b.preferred_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"'{a.name}' ({pet_of(a)}) at {a.preferred_time.strftime('%H:%M')} "
                        f"overlaps '{b.name}' ({pet_of(b)}) at {b.preferred_time.strftime('%H:%M')}."
                    )
        return warnings

    def generate_plan(self) -> DailyPlan:
        """Build and return the daily plan for the owner's pets."""
        day = date.today()
        due = [
            t
            for t in self.owner.all_tasks()
            if not t.completed and t.is_due_today(day)
        ]

        plan = DailyPlan(date=day)
        # Flag clashing fixed-time requests before we resolve/serialize them.
        plan.warnings = self.detect_conflicts(due)

        resolved = self.resolve_conflicts(due)
        ordered = self.sort_tasks(resolved)

        reasons: list[str] = []

        current = _to_minutes(self.owner.available_start)
        window_end = _to_minutes(self.owner.available_end)
        used = 0

        for task in ordered:
            fits_budget = used + task.duration_minutes <= self.available_minutes
            fits_window = current + task.duration_minutes <= window_end

            if fits_budget and fits_window:
                entry = ScheduledTask(
                    task=task,
                    start_time=_to_time(current),
                    end_time=_to_time(current + task.duration_minutes),
                )
                plan.add_entry(entry)
                reasons.append(
                    f"Scheduled {task.name} at {entry.start_time.strftime('%H:%M')} "
                    f"({task.duration_minutes} min, {task.priority.value})."
                )
                current += task.duration_minutes
                used += task.duration_minutes
            else:
                plan.skipped_tasks.append(task)
                why = "daily time budget reached" if not fits_budget else "no time left in window"
                reasons.append(f"Skipped {task.name}: {why}.")

        plan.reasoning = "\n".join(reasons)
        self._last_plan = plan
        return plan

    def explain(self) -> str:
        """Return an explanation of why tasks were included, ordered, or skipped."""
        if self._last_plan is None:
            self.generate_plan()
        return self._last_plan.reasoning
