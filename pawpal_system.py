"""PawPal+ system classes.

Skeleton generated from diagrams/uml_draft.mmd.
Data-holding objects use dataclasses; method bodies are stubs (no logic yet).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    """Task priority levels. The value doubles as a sort weight."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @property
    def weight(self) -> int:
        ...


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: Priority
    species_requirement: str | None = None
    preferred_time: str | None = None
    recurrence: str | None = None

    def is_applicable_to(self, pet: "Pet") -> bool:
        ...

    def sort_key(self) -> tuple:
        ...


@dataclass
class Pet:
    """A pet the owner is caring for."""

    name: str
    species: str
    preferences: list[str] = field(default_factory=list)

    def add_preference(self, pref: str) -> None:
        ...

    def matches(self, task: "Task") -> bool:
        ...


@dataclass
class Owner:
    """The pet owner, with a daily time budget and one or more pets."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        ...

    def time_budget(self) -> int:
        ...


@dataclass
class ScheduledTask:
    """A task that has been placed in the plan at a specific start time."""

    task: Task
    start_time: str


@dataclass
class DailyPlan:
    """The output of the scheduler: chosen tasks, skipped tasks, and totals."""

    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    total_minutes_used: int = 0

    def to_table(self) -> list:
        ...

    def summary(self) -> str:
        ...


@dataclass
class Scheduler:
    """Builds a daily plan from candidate tasks under the owner's constraints."""

    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        ...

    def remove_task(self, task: Task) -> None:
        ...

    def build_plan(self) -> DailyPlan:
        ...

    def explain(self) -> str:
        ...
