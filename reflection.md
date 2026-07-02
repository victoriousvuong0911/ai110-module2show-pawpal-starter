# PawPal+ Project Reflection

## 1. System Design

- Add a pet info
- Schedule a plan
- Display the plan

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

I chose `Owner`, `Pet`, and `Task` as data holders, a `Scheduler` engine that sorts/filters/resolves conflicts to produce a `DailyPlan` made of `ScheduledTask` time slots, with `Priority` and `Category` enums for type safety.

**b. Design changes**

- My design did not change

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers the owner's available time window, each task's priority and duration, and optional preferred times, and I prioritized time and priority most because a busy owner's biggest limit is fitting the essential tasks into a fixed window.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler uses a greedy fill that packs tasks by priority until the time budget runs out, so it can skip a large high-priority task in favor of smaller lower-priority ones that happen to fit. This is reasonable here because a pet owner benefits more from completing several quick essential tasks than from spending the whole window on one long one.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used AI to brainstorm and graph out requirements and to debug
- AI was most helpful in explaining code and reasoning

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When the AI suggested using an emoji in the conflict warning, I rejected it because it crashed on the Windows terminal, and I verified the fix by running `main.py` and the tests to confirm the warning printed without errors.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested task completion, adding tasks, chronological sorting, daily recurrence, and conflict detection, because those are the core behaviors a wrong result would quietly break the whole plan.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm moderately confident (3/5) since the core logic passes its tests, and next I would test end-to-end plan packing when tasks exceed the time window and weekly recurrence.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the conflict detection, which cleanly warns the owner about overlapping tasks instead of silently dropping one or crashing.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign the scheduler to actually place fixed-time tasks at their preferred times instead of packing everything sequentially from the start of the window.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that designing the classes and relationships up front (UML) made it far easier to build features incrementally and to direct the AI toward the right method to change.
