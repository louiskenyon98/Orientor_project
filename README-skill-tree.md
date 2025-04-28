# Skill Tree Generation System

A comprehensive system that generates personalized skill-to-career pathways using AI, visualized as an interactive tree.

## Overview

The Skill Tree Generation System:
- Accepts student profile descriptions (interests, traits, skills)
- Uses OpenAI GPT-4o to generate a structured skill-to-career pathway
- Renders an interactive visualization using ReactFlow
- Follows temporal learning progression (skills → outcomes → deeper skills → careers)

## Features

- **Backend (FastAPI)**:
  - POST `/tree` endpoint accepting profile descriptions
  - Secure OpenAI API interaction (never exposing keys)
  - Validation of generated tree structure
  - In-memory caching to reduce API costs

- **Frontend (Next.js + ReactFlow)**:
  - Interactive tree visualization
  - Color-coded node types (skills, outcomes, careers)
  - Popovers displaying recommended actions for skill nodes
  - Responsive force-directed layout

## Setup Instructions

### Prerequisites
- Node.js 18+ for frontend
- Python 3.8+ for backend
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```
   python -m uvicorn app.main:app --reload
   ```

5. The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Create a `.env.local` file with the API URL:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Install dependencies:
   ```
   npm install
   ```

4. Run the development server:
   ```
   npm run dev
   ```

5. Access the application at `http://localhost:3000/tree`

## Usage

1. Enter your profile information (interests, traits, skills) in the text area
2. Click "Generate Skill Tree"
3. Explore the generated skill tree:
   - Click on skill nodes to see recommended actions
   - Pan and zoom to navigate the tree
   - View different pathways from skills to careers

## Technical Implementation

### Tree Structure

The generated tree follows a strict pattern:
- Root Node: Student profile
- Level 1: 3 broad skill areas
- Level 2: 3 outcomes (one per broad skill)
- Level 3: 6 refined skills (2 per outcome)
- Level 4: 12 careers (2 per refined skill)

### Backend Architecture

- `app/routers/tree.py`: API endpoint definition
- `app/services/tree_service.py`: OpenAI interaction logic
- `app/schemas/tree.py`: Pydantic models for validation

### Frontend Architecture

- `src/app/tree/page.tsx`: Main page component
- `src/components/tree/SkillTree.tsx`: Main visualization component
- `src/components/tree/CustomNodes.tsx`: Node type components
- `src/utils/convertToFlowGraph.ts`: Tree-to-graph conversion utility
- `src/services/treeService.ts`: API interaction service

## Scaling Considerations

- Backend caches generated trees to reduce API costs
- ReactFlow efficiently renders large trees
- Structure follows temporal progression for learning clarity
- All interactive components are client-side rendered for performance 