"""PawPal+ demo script.

Builds a small owner/pet/task setup and prints today's schedule to the terminal.
Run it with:  python main.py
"""

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    # 1. Create an owner with a daily time budget, and at least two pets.
    owner = Owner(name="Jordan", available_minutes=90)
    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # 2. Add tasks of differing durations and priorities for those pets.
    scheduler = Scheduler(owner)
    scheduler.add_task(Task("Morning walk", 30, Priority.HIGH, pet_name="Mochi"))
    scheduler.add_task(Task("Feed Mochi", 10, Priority.HIGH, pet_name="Mochi"))
    scheduler.add_task(Task("Clean litter box", 15, Priority.MEDIUM, pet_name="Whiskers"))
    scheduler.add_task(Task("Play with Whiskers", 20, Priority.LOW, pet_name="Whiskers"))

    # 3. Build the plan and print today's schedule.
    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    print(scheduler.explain())


if __name__ == "__main__":
    main()
