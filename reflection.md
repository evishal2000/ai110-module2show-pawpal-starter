# PawPal+ Project Reflection

## 1. System Design

Core action of the user

- Add a pet
- Add tasks and priorities
- view the schedule/daily tasks

**a. Initial design**

My initial UML splits the system into three groups: **data objects**, a **scheduling engine**, and the **plan output**. This keeps each class focused on a single responsibility, so the scheduling algorithm can change without touching the data model.

Classes and responsibilities:

- **`Priority` (enum)** — `LOW`, `MEDIUM`, `HIGH` with an integer `weight`. Used instead of raw strings so priorities are type-safe and naturally sortable.
- **`Task`** — holds the details of one care item (`title`, `duration_minutes`, `priority`, optional `species_requirement`, `preferred_time`, `recurrence`). Responsible for self-queries like `is_applicable_to(pet)` and providing a `sort_key()` so ordering logic lives on the data, not in the scheduler.
- **`Pet`** — holds `name`, `species`, and `preferences`; can `add_preference()` and report whether it `matches(task)`.
- **`Owner`** — holds `name`, the daily time budget (`available_minutes`), and the list of `pets`. Can `add_pet()` and report its `time_budget()`. Owner *composes* Pets and candidate Tasks.
- **`Scheduler`** — the engine. Takes the `Owner` and candidate `tasks`, and `build_plan()` filters inapplicable tasks, sorts by priority, and greedily fits them into the time budget. `explain()` justifies the choices.
- **`ScheduledTask`** — wraps a `Task` with an assigned `start_time`.
- **`DailyPlan`** — the output: the ordered `scheduled` tasks, the `skipped` tasks (with reasons), and `total_minutes_used`. Knows how to present itself via `to_table()` and `summary()`.

I deliberately separated the **engine** (`Scheduler`) from the **result** (`DailyPlan`) so the planning output is easy to display in Streamlit and easy to assert on in tests without involving the UI.

**b. Design changes**

Yes. Reviewing the skeleton against the scenario surfaced several gaps in the data model, so I revised it before writing logic:

- **Added `pet_name` to `Task`.** Originally a task only had a `species_requirement`, so in a multi-pet home (e.g. two dogs) the scheduler couldn't tell whose walk it was. Linking each task to a specific pet makes the generated plan attributable.
- **Moved candidate `tasks` onto `Scheduler` (not `Owner`).** My first UML had the owner own the task list. Keeping tasks on the engine keeps `Owner` a pure data object and matches how the scheduler actually consumes them.
- **Consolidated applicability logic.** I had both `Task.is_applicable_to(pet)` and `Pet.matches(task)` — two methods doing the same species check from opposite sides, which would inevitably drift. I removed `Pet.matches()` and made `Task.is_applicable_to()` the single owner of that rule.
- **Gave skipped tasks a reason.** `DailyPlan.skipped` was just `list[Task]`, which couldn't explain *why* a task was dropped. I introduced a `SkippedTask` dataclass (`task` + `reason`) so `explain()` can justify the plan, which the scenario explicitly asks for.
- **Changed time to integer minutes.** `ScheduledTask.start_time` was a string, which is awkward to sort and to check for overlaps. I switched to `start_minute` (minutes from midnight) and added a `start_time()` helper that formats to `"HH:MM"` only for display.
- **Documented deferred features.** `recurrence` and slot-based `preferred_time` windows are kept as advisory fields for v1 — `build_plan()` doesn't yet resolve recurrence against a date or model per-slot budgets. I flagged these so the scope stays honest rather than half-implementing them.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
