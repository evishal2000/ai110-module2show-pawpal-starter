"""PawPal+ system classes.

Implements the model from diagrams/uml_draft.mmd: data objects, a scheduling
engine, and the plan it produces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# Plans start at 08:00 by default (minutes from midnight).
DAY_START_MINUTE = 8 * 60


class Priority(Enum):
    """Task priority levels. The value doubles as a sort weight."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @property
    def weight(self) -> int:
        """Numeric sort weight for this priority (HIGH is largest)."""
        return self.value


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: Priority
    pet_name: str | None = None  # which pet this task is for (disambiguates multi-pet homes)
    species_requirement: str | None = None
    preferred_time: str | None = None
    recurrence: str | None = None  # advisory only in v1 -- not yet resolved against a date
    status: str = "pending"  # "pending" until completed

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.status = "complete"

    def is_applicable_to(self, pet: "Pet") -> bool:
        """True if this task can be performed for the given pet.

        Single owner of applicability logic: a named task must match the pet's
        name, and a species-specific task must match the pet's species.
        """
        if self.pet_name is not None and self.pet_name != pet.name:
            return False
        if self.species_requirement is not None and self.species_requirement != pet.species:
            return False
        return True

    def sort_key(self) -> tuple:
        """Stable ordering key: highest priority first, then shortest duration.

        Priority weight is negated so a normal ascending sort puts HIGH first;
        duration breaks ties so quick wins are scheduled before long tasks.
        """
        return (-self.priority.weight, self.duration_minutes, self.title)


@dataclass
class Pet:
    """A pet the owner is caring for."""

    name: str
    species: str
    preferences: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_preference(self, pref: str) -> None:
        """Add a care preference, ignoring duplicates."""
        if pref not in self.preferences:
            self.preferences.append(pref)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The pet owner, with a daily time budget and one or more pets."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def time_budget(self) -> int:
        """Return the minutes available for care today."""
        return self.available_minutes


@dataclass
class ScheduledTask:
    """A task that has been placed in the plan at a specific start time."""

    task: Task
    start_minute: int  # minutes from midnight; format to a clock string only for display

    def start_time(self) -> str:
        """Render start_minute as a 'HH:MM' clock string."""
        hours, minutes = divmod(self.start_minute, 60)
        return f"{hours:02d}:{minutes:02d}"


@dataclass
class SkippedTask:
    """A task that was left out of the plan, with the reason why."""

    task: Task
    reason: str


@dataclass
class DailyPlan:
    """The output of the scheduler: chosen tasks, skipped tasks, and totals."""

    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[SkippedTask] = field(default_factory=list)
    total_minutes_used: int = 0

    def to_table(self) -> list:
        """Flat list of row dicts for display (e.g. Streamlit st.table)."""
        return [
            {
                "time": item.start_time(),
                "task": item.task.title,
                "pet": item.task.pet_name or "-",
                "duration_min": item.task.duration_minutes,
                "priority": item.task.priority.name.lower(),
            }
            for item in self.scheduled
        ]

    def summary(self) -> str:
        """One-line overview of the plan."""
        return (
            f"{len(self.scheduled)} task(s) scheduled "
            f"({self.total_minutes_used} min used), "
            f"{len(self.skipped)} skipped."
        )


@dataclass
class Scheduler:
    """Builds a daily plan from candidate tasks under the owner's constraints."""

    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pool of candidates to schedule."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the candidate pool if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def _applies_to_any_pet(self, task: Task) -> bool:
        """True if at least one of the owner's pets can receive this task."""
        return any(task.is_applicable_to(pet) for pet in self.owner.pets)

    def build_plan(self) -> DailyPlan:
        """Filter, sort by priority, then greedily fit tasks into the budget.

        Tasks that match no pet are skipped first; the rest are scheduled in
        priority order, back to back from DAY_START_MINUTE, until the owner's
        time budget is exhausted. Tasks that don't fit are skipped with a reason.
        """
        plan = DailyPlan()
        budget = self.owner.time_budget()

        applicable: list[Task] = []
        for task in self.tasks:
            if self._applies_to_any_pet(task):
                applicable.append(task)
            else:
                plan.skipped.append(SkippedTask(task, "no matching pet"))

        cursor = DAY_START_MINUTE
        used = 0
        for task in sorted(applicable, key=Task.sort_key):
            if used + task.duration_minutes <= budget:
                plan.scheduled.append(ScheduledTask(task, cursor))
                cursor += task.duration_minutes
                used += task.duration_minutes
            else:
                remaining = budget - used
                plan.skipped.append(
                    SkippedTask(
                        task,
                        f"not enough time: needs {task.duration_minutes} min, "
                        f"{remaining} min left",
                    )
                )

        plan.total_minutes_used = used
        return plan

    def explain(self) -> str:
        """Human-readable account of the plan and the reasoning behind it."""
        plan = self.build_plan()
        lines = [f"Daily plan for {self.owner.name}:", plan.summary(), ""]

        if plan.scheduled:
            lines.append("Scheduled (highest priority first, fit into the time budget):")
            for item in plan.scheduled:
                lines.append(
                    f"  {item.start_time()} - {item.task.title} "
                    f"({item.task.duration_minutes} min) "
                    f"[priority: {item.task.priority.name.lower()}]"
                )

        if plan.skipped:
            lines.append("")
            lines.append("Skipped:")
            for s in plan.skipped:
                lines.append(f"  {s.task.title} - {s.reason}")

        return "\n".join(lines)
