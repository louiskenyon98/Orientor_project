Feature Design: Interactive Career Skill Tree
Overview
Implement an end-to-end Interactive Career Skill Tree anchored on top 5 personalized skills. Leverage LLM inference, ESCO semantic alignment, Pinecone, GraphSAGE, and dynamic LLM-generated challenges. Integrate into existing FastAPI backend and Next.js frontend with minimal disruption.

1. Skill Extraction Pipeline
1.1 Inputs
UserProfile fields: story, interests, goals, long-form reflection answers
UserSkill ratings (creativity, leadership, etc.)
RIASEC & HEXACO scores
(Optional) UserRepresentation embedding
1.2 LLM Inference Service
New service: LLMCompetenceService
Prompt: combine narrative + skills ratings + psychometric summaries + long-form answers
Task: return 5 skill labels + brief internal justification
1.3 ESCO Formatting
Use existing format_user_profile_esco_style.py template functions: format_esco_skill
Pass each inferred skill to ESCO formatter to produce consistent, action-oriented text
1.4 Pinecone Matching
Encode formatted skills via sentence-transformers/all-MiniLM-L6-v2
Query esco-368 index top 1 per skill
Result: 5 anchor ESCO node IDs + metadata
2. ESCO Integration & Graph Anchor
2.1 Anchor Preparation
Gather 5 anchor skills with: id, preferredLabel, embedding vector
2.2 Store Anchors
Persist anchor list in user_skill_trees.tree_data.anchors
3. Home Page Integration
3.1 UI Section
Below <UserCard> insert <SkillShowcase>
Cards use same layout as job recommendation cards (icon, title, description)
Each card displays:
ESCO skill label
LLM-generated friendly description
Optional icon badge
“Explore My Path” CTA navigates to /competence-tree
3.2 Frontend Component
Create components/ui/SkillCard.tsx (reuse JobCard styles)
Add SkillShowcase container in frontend/src/app/page.tsx
4. Competence Tree Overhaul
4.1 Backend Service
4.1.1 Service Class: CompetenceTreeService
Methods:
infer_anchor_skills(user_id)
build_tree(anchors, max_depth=6, max_nodes=30) (GraphSAGE traversal)
generate_challenge(skill_node, user_context) (calls LLM)
save_skill_tree(db, user_id, tree_data)
4.1.2 GraphSAGE Traversal
Load best_model_20250520_022237.pt as CareerTreeModel encoder
For each anchor, level-wise subgraph expansion up to depth 6, total nodes ≤ 30
For each candidate: compute cosine similarity via GNN encoder pairs
Prune edges with similarity < 0.3
Hidden nodes: randomly conceal ~70% of non-anchor nodes
4.1.3 Challenge Generation
Prompt LLM with: skill label, user age & profile context, desired difficulty
Return 1–2 challenge instructions + XP reward
4.2 API Endpoints
POST /competence-tree/generate
Params: user_id, optional max_depth, max_nodes_per_level
Flow:
Infer anchors
Build tree structure (nodes with {id, label, type, level, visible, revealed, state, xp_reward, challenge})
Save UserSkillTree record (competenceTree JSONB column)
Return { graph_id }
GET /competence-tree/{graph_id}
Fetch UserSkillTree by graph_id & user_id
Return full JSON tree
PATCH /competence-tree/node/{node_id}/complete
Mark node state to completed, update user_progress.total_xp, add timestamp
Reveal children nodes (set visible=true)
5. Database Updates
5.1 Table: user_skill_trees
Column rename: tree_data → competenceTree (JSONB)
Stores:
anchors: list of anchor skill IDs
nodes: array of node objects
edges: array of {source,target}
5.2 user_progress
Track completed_nodes, total_xp updates for challenge completions
6. Frontend: Competence Tree View
6.1 Page: /app/competence-tree/page.tsx
Pass URL param graph_id to CompetenceTreeView
“Generate” button triggers generateCompetenceTree(userId)
6.2 Component: CompetenceTreeView.tsx
Fetch tree data via competenceTreeService.getCompetenceTree(graphId)
Use reactflow with custom node type <CompetenceNode>
Node rendering:
If visible && revealed=true, show label & XP; clicking node shows <ChallengeCard> with LLM prompt, “Complete” button
Edges drawn top-down
Controls: pan/zoom, fit view
6.3 Styling
Reuse treestyles.css
Node color by level
Locked nodes faded/greyed
7. AI Model & Infrastructure
7.1 Custom LLM
New endpoint in LLMCompetenceService uses OpenAI or internal LLM
Maintain separate prompt templates for skill inference & challenge generation
7.2 Pinecone & ESCO
Ensure esco-368 env variables set
Reuse existing embedding & Pinecone clients
8. Testing Strategy
8.1 Backend Tests
Unit: mock DB session, test infer_anchor_skills, build_tree, save_skill_tree
Integration: simulate POST generate & GET, assert JSON schema
8.2 Frontend Tests
React Testing Library: render SkillShowcase, CompetenceTreeView with mock data
Cypress/E2E: generate tree → node complete flow
9. Deployment & Rollout
Migrate DB: add/rename competenceTree column
Backend: install new dependencies (sentence-transformers), update env
Frontend: update package, redeploy Next.js
QA: verify skill extraction, tree generation, challenge completion flows
Monitoring: logs around model calls, performance metrics