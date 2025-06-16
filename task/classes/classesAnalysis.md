Implement a psychologically-targeted course sentiment analysis system for career profiling with the following components:

The user should access and interact with the: My Classes card in the Home page.  

BACKEND REQUIREMENTS:
1. Database schema with career profiling focus:
   - courses table: user_id, course_name, course_code, semester, year, professor, subject_category (STEM/humanities/business/arts)
   - psychological_insights table: user_id, course_id, insight_type (cognitive_preference/work_style/subject_affinity), insight_value, confidence_score, extracted_at
   - career_signals table: user_id, signal_type (analytical_thinking/creative_problem_solving/interpersonal_skills), strength_score, evidence_source (course_id + specific_interaction)
   - conversation_logs table: user_id, course_id, question_intent (explore_frustration/identify_strengths/clarify_preferences), response, extracted_insights

2. Career mapping integration:
   - Link insights to ESCO skill categories
   - Track patterns across multiple courses/semesters
   - Flag contradictions in student self-perception vs. performance

3. API endpoints:
   - POST /courses (add course with automatic subject categorization)
   - GET /psychological-profile/{user_id} (aggregated insights for career mapping)
   - POST /courses/{id}/targeted-analysis (trigger career-focused LLM conversation)
   - GET /career-signals/{user_id} (extract patterns for ESCO tree traversal)

FRONTEND REQUIREMENTS:
1. Career-focused conversation interface:
   - "Discover Your Career Preferences" button (not generic course feedback)
   - Targeted questioning based on course performance and previous responses
   - Real-time insight extraction displayed to user ("This suggests you prefer concrete over abstract thinking")

2. Insight dashboard:
   - Visual representation of discovered preferences/strengths
   - Connection to potential career paths from ESCO data
   - Timeline showing how insights evolve across semesters

LLM INTEGRATION - CAREER PROFILING SPECIFIC:
1. Question frameworks tied to psychological constructs:
   - Cognitive style: "You struggled with calculus but excelled in statistics - what felt different about solving those problems?"
   - Work environment preferences: "Your group project grade was lower than individual work - do you prefer independent or collaborative tasks?"
   - Interest authenticity: "Your marketing grade is high but you say you find it boring - what specifically disengages you?"

2. Response analysis for career insights:
   - Extract indicators of analytical vs. creative thinking preferences
   - Identify patterns suggesting introversion/extraversion work styles
   - Flag authentic interests vs. forced academic choices
   - Connect emotional reactions to specific ESCO skill categories

3. Career guidance integration:
   - Generate personalized ESCO tree starting points based on extracted insights
   - Flag career paths that contradict discovered preferences
   - Suggest skills to explore based on authentic interests revealed through course reactions

OUTPUT: Each conversation should produce specific, actionable insights that directly inform career tree traversal and job recommendations, not just course sentiment tracking.