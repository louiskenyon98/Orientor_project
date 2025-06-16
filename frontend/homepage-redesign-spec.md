# Homepage UI Redesign Specification

## Overview
Redesign the Orientor homepage to match the reference layout while maintaining the Navigo brand identity and color palette.

## Component Specifications

### 1. Top Navigation Bar Updates
- **Left Side**:
  - Navigo logo (existing)
  - User greeting: "Hey {userName}" (large font)
  - Motivational message: Dynamic based on time/weather
- **Right Side**:
  - Chat icon (existing)
  - XP level display (existing)
  - User profile icon (relocate to page body)

### 2. Sidebar Updates
- Add two new navigation icons:
  - Education icon (book-style) - Route: `/education`
  - Dashboard icon (grid-style) - Route: `/dashboard`
- Maintain existing icon order and styling

### 3. First Section Layout (3 columns)
#### Column 1: User Avatar Card
- Display user profile picture
- Add mood/badge indicator
- Title: "My Progress"
- Compact card design

#### Column 2: Personality Card
- Integrate existing personality card
- Include all personality test results
- Display top 5 skills from homepage
- Maintain current styling

#### Column 3: Calendar Component
- Interactive monthly view
- Color-coded events:
  - Tests (blue)
  - Challenges (orange)
  - Events (green)
- Click to view/add events

### 4. Second Section Layout (3 columns)
#### Column 1: Top Peers
- Title: "Top Peers"
- Vertical scrollable list
- Mini cards with:
  - Profile image
  - Name
  - Compatibility score
  - Brief description

#### Column 2: Recommended Jobs
- Title: "Recommended Jobs"
- Convert from grid to vertical list
- Each card includes:
  - Job title
  - Brief description
  - Key skills/tags
  - Save/Explore buttons

#### Column 3: Upcoming Events & Notes
- Stack vertically:
  - **Upcoming Events** section
  - **User Notes** section
- Show title, date, associated tags
- Quick action buttons

## Technical Requirements

### Styling
- Maintain existing Navigo color palette
- Use rounded cards with soft shadows
- Responsive design for desktop
- Consistent spacing and padding

### Data Integration
- Fetch peer recommendations from embedding service
- Pull user notes from `user_notes` table
- Integrate with existing job recommendation system
- Calendar events from user journey data

### Component Migration
- Move all tree-related sections to `/competence-tree` tab
- Preserve existing component functionality
- Maintain state management patterns

## Implementation Priority
1. Layout restructuring
2. New component creation (Calendar)
3. Existing component updates
4. Data integration
5. Testing and refinement