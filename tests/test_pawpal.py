"""Tests for core PawPal+ behaviors."""

from pawpal_system import Pet, Priority, Task


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips the task's status."""
    task = Task("Morning walk", 30, Priority.HIGH)
    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet increases its task count."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed Mochi", 10, Priority.HIGH))

    assert len(pet.tasks) == 1
