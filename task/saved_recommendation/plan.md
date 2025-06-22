### 🧠 Claude Prompt: Redesign and Rework the `/space` Tab as a Career Fit Analyzer

#### Objective

Redesign the `/space` tab to serve as a **Career Fit Analyzer**. This tab should help users compare themselves to saved jobs, understand day-to-day realities of these roles, and request LLM-based analysis in context. The goal is to turn job exploration into a **feasibility evaluation and fit check** based on the user's academic profile, skills, and psychology.

---

### 🔧 Tasks for Claude-Code

Make sure to spawn a TDD agent, so that test are done extensively, and iterated on, until all step complete. 

#### 1. Audit & Enhance Field Mapping

**ESCO Jobs**

* Go through the codebase and list all available ESCO fields used in saved recommendations (these reside in the `saved_recommendations` table with attributes like `role_critical_thinking`, `description`, etc.).
* Identify and confirm which **student profile fields** must be matched against them (draw from `user_profiles`, `users_skills`, `gca_results` tables).
* Add any **missing user-side fields** to the `user_profiles` schema, enabling symmetric comparisons (e.g., `minimum_gpa`, `required_courses`, etc.).

**OaSIS Jobs**

* For jobs sourced via `SwipeMyWay`, use GraphSAGE embeddings to extract **top 5 high-relevance skills** per job.
* Display these skills on the card but do not attempt full ESCO-style analysis.

---

#### 2. Build Dual Source Rendering Logic

In the `/space` frontend:

* **Display both ESCO and OaSIS saved jobs** using a unified card layout, but distinguish the data source.
* For ESCO jobs: show full comparative breakdown (e.g., skill-by-skill score deltas, job requirements, etc.).
* For OaSIS jobs: show top 5 GraphSAGE-ranked skills and key soft skill strengths.

---

#### 3. Embed an LLM Window on Each Job Card

* Add an LLM chat interface directly on each job card.
* User can ask:

  * “Why would I want to do this job?”
  * “What are the 3 biggest barriers between me and this role?”
  * “How long would it realistically take to qualify?”
  * “Do I need a PhD for this?”
  * “What are the actual qualifications?”

Use Langchain with the ESCO/OaSIS formatter logic (see `Langchain_PromptTemplate.pdf`):

* ESCO: Use `ESCO-OccupationFormatter`
* OaSIS: Use `OaSIS-RoleFormatter`

Inject user context from their profile and skills as prompt variables.

---

#### 4. Highlight Career Constraints Visually

On each card (especially for ESCO jobs), visually surface:

* **Entry Qualifications**

  * GPA requirements, prerequisites, portfolio/certification needs
* **Timeline**

  * Years to entry-level job
  * Income start date
  * Period with zero income
* **Degree Requirements**

  * Bachelor's vs Master's vs PhD
  * Total cost of education
  * Estimated debt

Implement these as a **“Feasibility Box”** or **“Time-Cost-Fit Summary”**.

---

#### 5. Investigate and Recommend Key ESCO Fields

Research and select only the **critical ESCO fields** that aid student decision-making (avoid full data dump). For each, justify:

* How it contributes to psychological or practical career fit
* How it supports LLM-based feasibility queries
* How it enhances the recommendation engine (e.g., through graph-based subgraph reasoning)

Examples to prioritize:

* Entry conditions
* Typical education level
* Essential vs optional skills
* Sector/industry
* ISCO lineage (for generalized category insights)

---

#### 6. Output Format and UX Behavior

* When `/space` is loaded:

  * Fetch all saved jobs (`GET /careers/saved`)
  * Render using their source (`esco` vs `oasis`)
  * Display matched fields and context-aware LLM suggestions

---

#### 🚨 Final Note

Students don't save jobs because they understand them—they save them *because they resonate*, but often don’t know why. Your mission is to explain this *fit* clearly, and expose **cost, barriers, and timelines** with brutal honesty.

Your guiding principle:

> “The question isn’t ‘Do I need a PhD?’—it’s ‘Can I survive 8 years of study while my friends start earning?’”
