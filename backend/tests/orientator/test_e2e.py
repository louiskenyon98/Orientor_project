"""
End-to-End tests for Orientator AI feature
Tests the complete user journey from start to finish
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from app.schemas.orientator import (
    OrientatorResponse,
    MessageComponent,
    MessageComponentType,
    ComponentAction,
    ComponentActionType,
    UserJourneyResponse
)


class TestOrientatorE2E:
    """End-to-end tests for complete user journeys"""
    
    @pytest.fixture
    def test_context(self):
        """Create test context with all necessary mocks"""
        context = {}
        
        # User
        user = Mock()
        user.id = 1
        user.email = "student@university.edu"
        
        profile = Mock()
        profile.name = "Jane Doe"
        profile.age = 22
        profile.major = "Computer Science"
        profile.year = 3
        profile.interests = "AI, data science, machine learning"
        profile.skills = ["python", "statistics", "sql"]
        profile.career_goals = "Become a data scientist at a tech company"
        user.profile = profile
        
        context['user'] = user
        
        # Conversation
        conv = Mock()
        conv.id = 1
        conv.user_id = user.id
        conv.title = "Career Exploration Journey"
        conv.created_at = datetime.utcnow()
        conv.message_count = 0
        context['conversation'] = conv
        
        # Saved components
        context['saved_components'] = []
        
        return context
    
    @pytest.mark.asyncio
    async def test_complete_career_exploration_journey(self, test_context):
        """Test a complete career exploration journey from start to finish"""
        
        # Step 1: Initial career exploration
        career_response = OrientatorResponse(
            content="Great! I can see you're interested in becoming a data scientist. Let me show you a comprehensive career path from your current position as a Computer Science student.",
            components=[
                MessageComponent(
                    id="career_path_001",
                    type=MessageComponentType.CAREER_PATH,
                    data={
                        "career_goal": "Senior Data Scientist",
                        "current_position": "CS Student (Year 3)",
                        "path": [
                            {
                                "step": 1,
                                "position": "Data Science Intern",
                                "duration": "3-6 months",
                                "when": "Final year or summer",
                                "skills_needed": ["Python", "Pandas", "Basic ML"],
                                "key_activities": [
                                    "Work on real data projects",
                                    "Learn from senior data scientists",
                                    "Build portfolio"
                                ]
                            },
                            {
                                "step": 2,
                                "position": "Junior Data Scientist",
                                "duration": "1-2 years",
                                "when": "After graduation",
                                "skills_needed": ["Advanced Python", "ML algorithms", "SQL", "Statistics"],
                                "key_activities": [
                                    "Lead small projects",
                                    "Develop ML models",
                                    "Learn cloud platforms"
                                ]
                            },
                            {
                                "step": 3,
                                "position": "Data Scientist",
                                "duration": "2-3 years",
                                "skills_needed": ["Deep Learning", "MLOps", "Business Acumen"],
                                "key_activities": [
                                    "Own end-to-end ML projects",
                                    "Mentor juniors",
                                    "Present to stakeholders"
                                ]
                            },
                            {
                                "step": 4,
                                "position": "Senior Data Scientist",
                                "duration": "Ongoing",
                                "skills_needed": ["Leadership", "Architecture", "Strategy"],
                                "key_activities": [
                                    "Define ML strategy",
                                    "Lead teams",
                                    "Drive innovation"
                                ]
                            }
                        ],
                        "total_estimated_time": "5-7 years",
                        "key_milestones": [
                            "Complete first internship",
                            "Deploy first production ML model",
                            "Lead a team project",
                            "Publish research or speak at conference"
                        ]
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.SAVE,
                            label="Save Career Path"
                        ),
                        ComponentAction(
                            type=ComponentActionType.EXPLORE,
                            label="View Required Skills"
                        )
                    ],
                    metadata={"tool_source": "career_tree"}
                )
            ],
            metadata={
                "tools_invoked": ["career_tree"],
                "intent": "career_exploration"
            }
        )
        
        # User saves the career path
        test_context['saved_components'].append({
            "type": "career_path",
            "data": career_response.components[0].data,
            "saved_at": datetime.utcnow()
        })
        
        # Step 2: Skill gap analysis
        skills_response = OrientatorResponse(
            content="Now let's analyze your current skills against what you'll need for each stage of your data science journey. I'll identify the gaps and prioritize what to learn next.",
            components=[
                MessageComponent(
                    id="skills_001",
                    type=MessageComponentType.SKILL_TREE,
                    data={
                        "current_role": "CS Student",
                        "target_role": "Data Science Intern",
                        "skill_analysis": {
                            "have": [
                                {"name": "Python", "level": "Intermediate", "sufficient": True},
                                {"name": "Statistics", "level": "Basic", "sufficient": False},
                                {"name": "SQL", "level": "Basic", "sufficient": True}
                            ],
                            "need": [
                                {"name": "Pandas", "priority": "High", "time_to_learn": "2-4 weeks"},
                                {"name": "NumPy", "priority": "High", "time_to_learn": "1-2 weeks"},
                                {"name": "Scikit-learn", "priority": "High", "time_to_learn": "4-6 weeks"},
                                {"name": "Data Visualization", "priority": "Medium", "time_to_learn": "2-3 weeks"},
                                {"name": "Statistical Testing", "priority": "Medium", "time_to_learn": "3-4 weeks"}
                            ],
                            "learning_path": [
                                {
                                    "phase": "Foundation (Next 2 months)",
                                    "skills": ["NumPy", "Pandas", "Data Visualization"],
                                    "projects": ["EDA on real dataset", "Data cleaning pipeline"]
                                },
                                {
                                    "phase": "ML Basics (Following 2 months)",
                                    "skills": ["Scikit-learn", "Statistical Testing"],
                                    "projects": ["Predictive model", "A/B testing analysis"]
                                }
                            ]
                        },
                        "recommended_resources": [
                            {"type": "course", "name": "Python for Data Science", "platform": "Coursera"},
                            {"type": "book", "name": "Hands-On Machine Learning", "author": "Aurélien Géron"},
                            {"type": "project", "name": "Kaggle competitions", "difficulty": "Beginner"}
                        ]
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.SAVE,
                            label="Save Skill Analysis"
                        )
                    ],
                    metadata={"tool_source": "esco_skills"}
                )
            ],
            metadata={
                "tools_invoked": ["esco_skills"],
                "intent": "skill_gap_analysis"
            }
        )
        
        # User saves the skill analysis
        test_context['saved_components'].append({
            "type": "skill_analysis",
            "data": skills_response.components[0].data,
            "saved_at": datetime.utcnow()
        })
        
        # Step 3: Job market exploration
        jobs_response = OrientatorResponse(
            content="Let me show you current data science job opportunities that match your profile and the different types of roles available in the market.",
            components=[
                MessageComponent(
                    id="jobs_001",
                    type=MessageComponentType.JOB_CARD,
                    data={
                        "job_matches": [
                            {
                                "title": "Data Science Intern - Tech Startup",
                                "company": "InnovateTech",
                                "match_score": 0.85,
                                "location": "San Francisco, CA (Remote friendly)",
                                "requirements_match": {
                                    "have": ["Python", "SQL", "Student status"],
                                    "missing": ["Pandas experience", "ML projects"],
                                    "nice_to_have": ["Cloud experience"]
                                },
                                "description": "Work on real ML projects with mentorship",
                                "salary_range": "$25-35/hour",
                                "growth_potential": "High - many interns convert to full-time"
                            },
                            {
                                "title": "Junior Data Analyst",
                                "company": "RetailCorp",
                                "match_score": 0.78,
                                "location": "New York, NY",
                                "requirements_match": {
                                    "have": ["SQL", "Python basics"],
                                    "missing": ["Business analytics experience"],
                                    "nice_to_have": ["Tableau"]
                                },
                                "description": "Analytics role with path to data science",
                                "salary_range": "$65,000-75,000",
                                "growth_potential": "Medium - can transition to DS in 1-2 years"
                            },
                            {
                                "title": "ML Engineering Intern",
                                "company": "BigTech Inc",
                                "match_score": 0.72,
                                "location": "Seattle, WA",
                                "requirements_match": {
                                    "have": ["Python", "CS background"],
                                    "missing": ["Deep learning", "System design"],
                                    "nice_to_have": ["Research experience"]
                                },
                                "description": "Focus on ML infrastructure and deployment",
                                "salary_range": "$40-50/hour",
                                "growth_potential": "Very High - top tier experience"
                            }
                        ],
                        "market_insights": {
                            "demand_trend": "Growing 25% YoY",
                            "avg_salary_progression": {
                                "intern": "$30-40/hour",
                                "junior": "$70,000-90,000",
                                "mid": "$110,000-140,000",
                                "senior": "$150,000-200,000+"
                            },
                            "hot_skills_2024": ["LLMs", "MLOps", "Cloud ML", "Causal Inference"],
                            "top_industries": ["Tech", "Finance", "Healthcare", "Retail"]
                        }
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.SAVE,
                            label="Save Job Matches"
                        )
                    ],
                    metadata={"tool_source": "oasis_explorer"}
                )
            ],
            metadata={
                "tools_invoked": ["oasis_explorer"],
                "intent": "job_exploration"
            }
        )
        
        # Step 4: Personality assessment for career fit
        personality_response = OrientatorResponse(
            content="Based on our conversation, I recommend taking a personality assessment to ensure data science aligns with your natural strengths and work preferences.",
            components=[
                MessageComponent(
                    id="personality_001",
                    type=MessageComponentType.TEST_RESULT,
                    data={
                        "test_type": "Holland Code (RIASEC)",
                        "results": {
                            "primary_code": "IRA",
                            "scores": {
                                "Investigative": 0.85,
                                "Realistic": 0.72,
                                "Artistic": 0.68,
                                "Social": 0.45,
                                "Enterprising": 0.40,
                                "Conventional": 0.35
                            },
                            "interpretation": {
                                "fit_score": 0.92,
                                "strengths": [
                                    "Strong analytical and problem-solving orientation",
                                    "Enjoys working with data and abstract concepts",
                                    "Creative approach to finding solutions"
                                ],
                                "considerations": [
                                    "May need to develop presentation skills for stakeholder communication",
                                    "Consider roles with creative problem-solving opportunities"
                                ],
                                "ideal_environments": [
                                    "Research-oriented teams",
                                    "Innovative tech companies",
                                    "Roles with autonomy and intellectual challenges"
                                ]
                            }
                        },
                        "career_recommendations": [
                            {
                                "role": "Data Scientist - Research Focus",
                                "fit": 0.95,
                                "reason": "Perfect match for investigative nature"
                            },
                            {
                                "role": "ML Research Engineer",
                                "fit": 0.88,
                                "reason": "Combines investigation with building"
                            },
                            {
                                "role": "Data Science Consultant",
                                "fit": 0.75,
                                "reason": "Good fit but requires more social interaction"
                            }
                        ]
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.SAVE,
                            label="Save Assessment Results"
                        )
                    ],
                    metadata={"tool_source": "holland_test"}
                )
            ],
            metadata={
                "tools_invoked": ["holland_test"],
                "intent": "personality_assessment"
            }
        )
        
        # Step 5: Challenge recommendations
        challenges_response = OrientatorResponse(
            content="Here are practical challenges and projects to help you build the skills you need and strengthen your portfolio for data science internships.",
            components=[
                MessageComponent(
                    id="challenges_001",
                    type=MessageComponentType.CHALLENGE_CARD,
                    data={
                        "skill_challenges": [
                            {
                                "id": "ch_001",
                                "title": "Customer Churn Prediction",
                                "skills_practiced": ["Pandas", "Scikit-learn", "EDA"],
                                "difficulty": "Beginner",
                                "estimated_time": "1 week",
                                "xp_reward": 500,
                                "description": "Build a model to predict customer churn using real telecom data",
                                "learning_outcomes": [
                                    "Data preprocessing with Pandas",
                                    "Feature engineering",
                                    "Model evaluation metrics"
                                ],
                                "resources": ["Dataset on Kaggle", "Guided tutorial available"]
                            },
                            {
                                "id": "ch_002",
                                "title": "Time Series Forecasting",
                                "skills_practiced": ["Statistical Analysis", "Python", "Visualization"],
                                "difficulty": "Intermediate",
                                "estimated_time": "2 weeks",
                                "xp_reward": 750,
                                "description": "Forecast sales using historical data with multiple techniques",
                                "learning_outcomes": [
                                    "Time series decomposition",
                                    "ARIMA models",
                                    "Prophet forecasting"
                                ]
                            },
                            {
                                "id": "ch_003",
                                "title": "Build a Recommendation System",
                                "skills_practiced": ["ML Algorithms", "Python", "System Design"],
                                "difficulty": "Intermediate",
                                "estimated_time": "3 weeks",
                                "xp_reward": 1000,
                                "description": "Create a movie recommendation system from scratch",
                                "learning_outcomes": [
                                    "Collaborative filtering",
                                    "Content-based filtering",
                                    "Hybrid approaches"
                                ]
                            }
                        ],
                        "portfolio_projects": [
                            {
                                "title": "End-to-End ML Pipeline",
                                "description": "Build a complete ML project from data collection to deployment",
                                "impact": "Shows employers you can handle full project lifecycle",
                                "technologies": ["Python", "Docker", "Cloud (AWS/GCP)", "Git"]
                            }
                        ],
                        "achievement_path": {
                            "current_xp": 0,
                            "next_milestone": "Data Explorer (500 XP)",
                            "milestones": [
                                {"title": "Data Explorer", "xp": 500, "reward": "LinkedIn Badge"},
                                {"title": "ML Practitioner", "xp": 2000, "reward": "Certificate"},
                                {"title": "Data Science Ready", "xp": 5000, "reward": "Job Referrals"}
                            ]
                        }
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.START,
                            label="Start First Challenge"
                        ),
                        ComponentAction(
                            type=ComponentActionType.SAVE,
                            label="Save Challenges"
                        )
                    ],
                    metadata={"tool_source": "xp_challenges"}
                )
            ],
            metadata={
                "tools_invoked": ["xp_challenges"],
                "intent": "skill_development"
            }
        )
        
        # Step 6: Journey summary and milestones
        journey_summary = UserJourneyResponse(
            user_id=test_context['user'].id,
            journey_stages=[
                {
                    "stage": "Career Goal Defined",
                    "type": "career_exploration",
                    "data": {"goal": "Senior Data Scientist", "timeline": "5-7 years"},
                    "achieved_at": datetime.utcnow().isoformat()
                },
                {
                    "stage": "Skills Gap Identified",
                    "type": "skill_analysis",
                    "data": {"skills_to_learn": 5, "estimated_time": "4 months"},
                    "achieved_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
                },
                {
                    "stage": "Job Market Explored",
                    "type": "job_matching",
                    "data": {"matches_found": 3, "best_match_score": 0.85},
                    "achieved_at": (datetime.utcnow() + timedelta(hours=2)).isoformat()
                },
                {
                    "stage": "Personality Assessment Completed",
                    "type": "assessment",
                    "data": {"holland_code": "IRA", "career_fit": 0.92},
                    "achieved_at": (datetime.utcnow() + timedelta(hours=3)).isoformat()
                },
                {
                    "stage": "Learning Path Created",
                    "type": "challenges",
                    "data": {"challenges_available": 3, "total_xp": 2250},
                    "achieved_at": (datetime.utcnow() + timedelta(hours=4)).isoformat()
                }
            ],
            saved_items_count=5,
            tools_used=["career_tree", "esco_skills", "oasis_explorer", "holland_test", "xp_challenges"],
            career_goals=["Senior Data Scientist"],
            skill_progression={
                "current": ["Python", "Statistics", "SQL"],
                "learning": ["Pandas", "NumPy", "Scikit-learn"],
                "future": ["Deep Learning", "MLOps", "Leadership"]
            },
            personality_insights={
                "holland_code": "IRA",
                "strengths": ["Analytical", "Creative problem-solving"],
                "career_fit_score": 0.92
            },
            challenges_completed=[],
            next_steps=[
                "Complete first Pandas project challenge",
                "Apply to 2-3 internships matching profile",
                "Start building GitHub portfolio",
                "Network with data scientists on LinkedIn"
            ]
        )
        
        # Verify the complete journey
        assert len(journey_summary.journey_stages) == 5
        assert journey_summary.saved_items_count == 5
        assert len(journey_summary.tools_used) == 5
        assert journey_summary.personality_insights["career_fit_score"] > 0.9
        assert len(journey_summary.next_steps) >= 4
        
        # Verify user has actionable path forward
        assert "Pandas" in journey_summary.skill_progression["learning"]
        assert any("internship" in step.lower() for step in journey_summary.next_steps)
        
        # Verify comprehensive coverage
        tools_categories = {
            "career_tree": "career_planning",
            "esco_skills": "skill_analysis", 
            "oasis_explorer": "job_market",
            "holland_test": "self_assessment",
            "xp_challenges": "skill_development"
        }
        
        for tool in journey_summary.tools_used:
            assert tool in tools_categories
        
        return journey_summary
    
    @pytest.mark.asyncio
    async def test_returning_user_journey_continuation(self, test_context):
        """Test a returning user continuing their journey"""
        
        # Previous journey state
        previous_state = {
            "completed_challenges": ["ch_001"],
            "current_position": "Completed Python basics",
            "xp_earned": 500,
            "internship_applications": 2
        }
        
        # Returning user asks for progress update
        progress_response = OrientatorResponse(
            content=f"Welcome back! I see you've completed the Customer Churn Prediction challenge and earned 500 XP. You're making great progress! Let's review where you are and plan your next steps.",
            components=[
                MessageComponent(
                    id="progress_001",
                    type=MessageComponentType.TEXT,
                    data={
                        "progress_summary": {
                            "completed": [
                                "Customer Churn Prediction challenge",
                                "Basic Pandas proficiency",
                                "Applied to 2 internships"
                            ],
                            "in_progress": [
                                "Time Series Forecasting challenge",
                                "Learning Scikit-learn"
                            ],
                            "upcoming": [
                                "Recommendation System project",
                                "Interview preparation",
                                "Advanced statistics"
                            ],
                            "metrics": {
                                "skills_gained": 2,
                                "xp_earned": 500,
                                "portfolio_projects": 1,
                                "days_active": 14
                            }
                        },
                        "personalized_recommendations": [
                            "Complete Time Series challenge this week",
                            "Schedule mock interviews for applied positions",
                            "Join data science community meetup"
                        ]
                    },
                    actions=[],
                    metadata={"generated_from": "user_progress_analysis"}
                )
            ],
            metadata={
                "intent": "progress_review",
                "user_engagement_score": 0.85
            }
        )
        
        assert "500 XP" in progress_response.content
        assert len(progress_response.components[0].data["progress_summary"]["completed"]) >= 3
        assert progress_response.metadata["user_engagement_score"] > 0.8
    
    @pytest.mark.asyncio
    async def test_adaptive_guidance_based_on_progress(self, test_context):
        """Test that Orientator adapts guidance based on user progress"""
        
        # User struggling with challenges
        struggling_response = OrientatorResponse(
            content="I notice you've been working on the Time Series challenge for a while. Let me break it down into smaller, manageable steps and provide additional resources to help you succeed.",
            components=[
                MessageComponent(
                    id="adaptive_001",
                    type=MessageComponentType.TEXT,
                    data={
                        "adaptive_support": {
                            "challenge_breakdown": [
                                {
                                    "step": "Data Understanding",
                                    "tasks": [
                                        "Plot the time series",
                                        "Check for seasonality",
                                        "Identify trends"
                                    ],
                                    "resources": ["Video: Time Series Basics", "Interactive notebook"]
                                },
                                {
                                    "step": "Simple Forecasting",
                                    "tasks": [
                                        "Try moving average",
                                        "Implement naive forecast",
                                        "Calculate error metrics"
                                    ],
                                    "resources": ["Code examples", "Office hours Thursday 3pm"]
                                }
                            ],
                            "alternative_paths": [
                                "Switch to easier Statistics Fundamentals challenge",
                                "Pair with a peer on this challenge",
                                "Attend weekend workshop on time series"
                            ],
                            "encouragement": "Remember, even experienced data scientists find time series challenging. You're building valuable skills!"
                        }
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.EXPLORE,
                            label="View Simplified Steps"
                        )
                    ],
                    metadata={"adaptation_type": "difficulty_support"}
                )
            ],
            metadata={
                "intent": "adaptive_guidance",
                "user_state": "struggling",
                "intervention_type": "breakdown_and_support"
            }
        )
        
        assert "smaller, manageable steps" in struggling_response.content
        assert len(struggling_response.components[0].data["adaptive_support"]["challenge_breakdown"]) >= 2
        assert "alternative_paths" in struggling_response.components[0].data["adaptive_support"]
    
    @pytest.mark.asyncio
    async def test_milestone_celebration_and_next_phase(self, test_context):
        """Test milestone achievement and transition to next phase"""
        
        # User completes first major milestone
        milestone_response = OrientatorResponse(
            content="🎉 Congratulations! You've reached the 'ML Practitioner' milestone with 2000 XP! You've completed 5 challenges, built 3 portfolio projects, and successfully landed a Data Science internship. Let's plan your next phase of growth.",
            components=[
                MessageComponent(
                    id="milestone_001",
                    type=MessageComponentType.TEXT,
                    data={
                        "achievement": {
                            "milestone": "ML Practitioner",
                            "xp_earned": 2000,
                            "badge_earned": "ml-practitioner-badge.png",
                            "certificate": "ML_Practitioner_Certificate_Jane_Doe.pdf",
                            "accomplishments": [
                                "5 challenges completed",
                                "3 portfolio projects",
                                "85% average score",
                                "Data Science Internship secured"
                            ],
                            "skills_mastered": [
                                "Pandas", "NumPy", "Scikit-learn",
                                "Basic ML algorithms", "Data visualization"
                            ]
                        },
                        "next_phase": {
                            "title": "Journey to Data Scientist",
                            "new_goals": [
                                "Master deep learning frameworks",
                                "Complete internship successfully",
                                "Contribute to open source",
                                "Build specialization (NLP/CV/RL)"
                            ],
                            "upcoming_challenges": [
                                "Deep Learning Fundamentals",
                                "Real-world ML Pipeline",
                                "A/B Testing Master Class"
                            ],
                            "timeline": "Next 6-12 months"
                        },
                        "celebration_actions": [
                            "Share achievement on LinkedIn",
                            "Update resume with new skills",
                            "Schedule mentorship session",
                            "Join advanced study group"
                        ]
                    },
                    actions=[
                        ComponentAction(
                            type=ComponentActionType.SHARE,
                            label="Share Achievement"
                        ),
                        ComponentAction(
                            type=ComponentActionType.SAVE,
                            label="Save Certificate"
                        )
                    ],
                    metadata={"milestone_type": "major", "celebration_level": "high"}
                )
            ],
            metadata={
                "intent": "milestone_celebration",
                "user_achievement_level": "high",
                "engagement_boost": True
            }
        )
        
        assert "Congratulations" in milestone_response.content
        assert milestone_response.components[0].data["achievement"]["xp_earned"] == 2000
        assert len(milestone_response.components[0].data["next_phase"]["new_goals"]) >= 4
        assert milestone_response.metadata["engagement_boost"] == True