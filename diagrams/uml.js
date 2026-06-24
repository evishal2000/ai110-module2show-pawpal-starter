// PawPal+ — UML class diagram definition (Mermaid.js)
// Import this string and pass it to mermaid.render(), or reuse it across pages.
//
//   import { umlDiagram } from "./uml.js";
//   import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
//   const { svg } = await mermaid.render("pawpal-uml", umlDiagram);
//   document.getElementById("target").innerHTML = svg;

export const umlDiagram = `
classDiagram
    %% PawPal+ class design
    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        +int weight
    }

    class Task {
        +str title
        +int duration_minutes
        +Priority priority
        +str species_requirement
        +str preferred_time
        +str recurrence
        +is_applicable_to(pet) bool
        +sort_key() tuple
        +__repr__() str
    }

    class Pet {
        +str name
        +str species
        +list~str~ preferences
        +add_preference(pref) None
        +matches(task) bool
    }

    class Owner {
        +str name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet) None
        +time_budget() int
    }

    class Scheduler {
        +Owner owner
        +list~Task~ tasks
        +add_task(task) None
        +remove_task(task) None
        +build_plan() DailyPlan
        +explain() str
    }

    class ScheduledTask {
        +Task task
        +str start_time
    }

    class DailyPlan {
        +list~ScheduledTask~ scheduled
        +list~Task~ skipped
        +int total_minutes_used
        +to_table() list
        +summary() str
    }

    Task --> Priority : has a
    Owner "1" o-- "*" Pet : has many
    Owner "1" o-- "*" Task : candidate tasks
    Scheduler --> Owner : uses
    Scheduler --> Task : schedules
    Scheduler ..> DailyPlan : produces
    DailyPlan "1" *-- "*" ScheduledTask : contains
    ScheduledTask --> Task : wraps
`;

export default umlDiagram;
