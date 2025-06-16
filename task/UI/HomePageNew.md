
**Prompt for Claude Code — Homepage UI Redesign**

---

Hi Claude,
Please help me rework my current homepage UI to match the visual layout of the attached image (`frontend/public/image/HomePageUI.png`), while keeping the **existing Navigo color palette and styles**. The goal is to align the disposition and structure exactly like the image, but keep our brand identity.

Here are the specific tasks and layout instructions:

---

### 🔧 GLOBAL LAYOUT

#### Sidebar (Left Vertical Navigation)

* Leave the current **left-hand navigation bar as-is**.
* **Add two new icons**:

  * An **Education icon** (book-style) near the top.
  * A **Dashboard icon** (grid-style) above or below the existing icons.

---

### 🔝 Top Navigation Bar

* Rework the top navigation to match the layout in the reference image:

  * On the **left side**, show:

    * The **Navigo logo**.
    * The **user’s name**, in large font (e.g. "Hey Phil").
    * A **motivational sentence** below, like “It’s sunny today and it’s time to explore 🌞”
  * On the **right side**, include:

    * The **chat icon** (already exists).
    * The **XP level** (already implemented).
    * The **user profile icon** (avatar) — position this in the **top-left corner of the page body**, just under the top bar, like in the image.

---

### 🧠 First Section (Horizontal row: 3 parts)

This section will have 3 key horizontal parts from left to right:

1. **User Avatar**

   * Show the avatar/profile picture card in the **far left** of the page body.
   * It should appear **under the "My Progress" title**, replacing the “completed lessons” box from the image.
   * If possible, add a fun tag or icon (emoji, badge, mood label).

2. **Personality Card**

   * To the **right of the avatar**, display the current "Personalité" card that already exists in the codebase.
   * Do not modify its content, just adopt the card's styling to match the surrounding design.
   * Put all the personality test and the results of these test on the Personality tab (related to that card)
   * Put all the top 5 skills currently on the home page, on this personnality cards.

3. **Calendar Component**

   * On the **far right**, insert a **calendar component** styled similarly to the image.
   * It should allow interaction (clickable days, upcoming events highlight).
   * Include color tags for “Test”, “Challenge”, and “Event”.

---

### 👥 Second Section (Horizontal row under the top row)

This section is a **three-column layout** as follows:

1. **Top Peers List (left)**

   * Title: `Top Peers`
   * Claude, use the peer recommendation feature that’s already being implemented (based on embeddings).
   * Each peer should be a mini card (image, name, short note).
   * Format the list in a **vertical scrollable list**, exactly like the course list in the reference image.

2. **Recommended Jobs List (center)**

   * Title: `Recommended Jobs`
   * Use the **existing "Recommended Jobs" cards** on the homepage, but display them as a **vertical list** instead of a grid.
   * Each card should show:

     * Job title
     * Short description
     * Icons/tags for key soft skills or domains
     * Optionally, a "Save" or "Explore" button.

3. **Upcoming Events + Notes (right)**

   * Stack vertically:

     * **Upcoming Events**: from the calendar or user's journey.
     * **User Notes**: Fetch from `user_notes` and show the **note title** on the card.
   * Follow the right-hand list formatting from the image.
   * Each note card should:

     * Show title, date/time if available
     * A small tag for the associated Tree node or Job if exists

---

### 🌲 Tree Sections

* All current tree-related sections on the homepage (e.g., skill ladders, career tree previews, etc.) should now be **moved into the `compétence-Tree` tab**.
* Nothing tree-related should remain on the homepage.

---

### 📌 Style & Interactions

* Maintain your current Navigo **color palette**, button styles, and font families.
* All components should remain responsive for desktop.
* Use **rounded cards**, soft shadows, and pastel background areas (similar in feel to the reference).
* Match the card padding, spacing, and column alignment closely to the reference image.

---

