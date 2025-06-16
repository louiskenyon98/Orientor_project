Implement career progression timeline using existing GraphSage edge scoring:

All of this implementation should render in the http://localhost:3000/goals tab in the frontend. 

PHASE 1 - GraphSage Progression Extraction:
- Modify existing GraphSage algorithm to perform recursive skill extraction
- For target occupation: get top 5 highest-scored connected skills (tier 1)
- For each tier 1 skill: get top 5 highest-scored connected skills (tier 2)
- Continue recursively up to configurable depth X (recommend X=3-4 for usability)
- Create API endpoint: GET /career-progression/{occupation_id}?depth=X

PHASE 2 - Intelligent Skill Filtering:
- Use GraphSage scores to rank skills within each tier by relevance
- Implement deduplication logic for skills appearing in multiple tiers
- Add skill type filtering (technical vs soft skills vs certifications)
- Consider user profile data to personalize GraphSage scoring if available

PHASE 3 - Timeline Visualization with Scoring:
- Render progression tiers with GraphSage confidence scores visible
- Use score intensity to determine visual prominence (higher scores = larger nodes)
- Show skill relationships/connections between tiers
- Implement the expandable timeline interaction as planned

PHASE 4 - Dynamic Depth Control:
- Allow users to adjust progression depth (see more/fewer future skills)
- Add "Show Alternative Paths" that explores different top-5 combinations
- Implement real-time recalculation when user adjusts parameters

PHASE 5 - GraphSage-Enhanced LLM Conversations:
- Pass GraphSage relevance scores to LLM for contextualized skill discussions
- Enable LLM to explain why certain skills scored highly for this career path
- Use scoring data to suggest personalized learning priorities

Let Claude-Code determine how to integrate with existing GraphSage implementation and optimize recursive traversal performance.