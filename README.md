# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:



Alex — 2 pet(s), available 08:00–11:00
Pets: Biscuit the Golden Retriever (3 task(s)), Whiskers the Tabby (3 task(s))

========================================
Today's Schedule
========================================
Daily plan for 2026-07-02:
  08:00 — Medication (5 min) [priority: high]
  08:05 — Breakfast (10 min) [priority: high]
  08:15 — Feeding (10 min) [priority: high]
  08:25 — Morning walk (30 min) [priority: high]
  08:55 — Play time (20 min) [priority: medium]
  09:15 — Grooming (45 min) [priority: low]

Total scheduled time: 120 min

Why this plan:
Scheduled Medication at 08:00 (5 min, high).
Scheduled Breakfast at 08:05 (10 min, high).
Scheduled Feeding at 08:15 (10 min, high).
Scheduled Morning walk at 08:25 (30 min, high).
Scheduled Play time at 08:55 (20 min, medium).
Scheduled Grooming at 09:15 (45 min, low).
```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. The table below maps each
implemented feature to the method that provides it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | Order by priority-then-duration (or by duration), or chronologically by preferred time. |
| Filtering | `Owner.find_tasks()`, `Scheduler.filter_tasks()` | Filter by pet name and/or completion status; drop tasks that exceed the time budget. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.resolve_conflicts()`, `ScheduledTask.overlaps()` | Warn on overlapping fixed-time tasks; keep the higher-priority one when packing. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()`, `Task.is_due_today()` | Completing a daily/weekly task auto-creates the next dated occurrence. |

### Sorting behavior

- **`Scheduler.sort_tasks(tasks)`** orders tasks by the active strategy: `"priority"` (most important first, then shortest, then earliest preferred time) or `"duration"` (shortest first to fit more in).
- **`Scheduler.sort_by_time(tasks)`** orders tasks chronologically by `preferred_time` (converted to minutes since midnight); tasks with no preferred time sort last instead of raising on a `None` comparison.

### Filtering behavior

- **`Owner.find_tasks(completed=None, pet_name=None)`** returns tasks filtered by completion status and/or pet name. Both filters compose, and `None` means "no filter" (so `completed=False` correctly returns only pending tasks).
- **`Scheduler.filter_tasks(tasks)`** greedily keeps, in order, only the tasks that fit within `available_minutes`.

### Conflict detection logic

- **`Scheduler.detect_conflicts(tasks)`** does a lightweight O(n²) pairwise scan of fixed-time tasks. Two tasks conflict when their `[start, start + duration)` intervals overlap — catching both exact matches and partial overlaps, within one pet or across pets. It **returns warning strings rather than raising**, so a clash never crashes plan generation; warnings surface in `DailyPlan.warnings` and `to_display()`.
- **`Scheduler.resolve_conflicts(tasks)`** then drops overlapping fixed-time tasks, keeping the higher-priority one, before the plan is packed.

### Recurring task logic

- **`Task.next_occurrence()`** returns a fresh, uncompleted copy with `due_date` advanced by the recurrence interval (daily = +1 day, weekly = +7 days), or `None` for a `"once"` task.
- **`Pet.complete_task(task)`** marks a task complete and, if it recurs, automatically appends its next occurrence to the pet's list.
- **`Task.is_due_today(day)`** honors a task's `due_date` when set, so a regenerated instance is only scheduled on its actual day.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
