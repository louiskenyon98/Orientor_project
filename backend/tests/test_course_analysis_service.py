import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.course_analysis_service import CourseAnalysisService
from app.models.course import Course, PsychologicalInsight, CareerSignal
from app.schemas.course import SubjectCategory

class TestCourseAnalysisService:
    """Test suite for CourseAnalysisService."""

    @pytest.mark.asyncio
    async def test_categorize_course_stem(self):
        """Test course categorization for STEM subjects."""
        # Test STEM keywords
        result = await CourseAnalysisService.categorize_course(
            "Introduction to Data Science",
            "This course covers mathematical foundations and programming concepts"
        )
        assert result == SubjectCategory.STEM

        result = await CourseAnalysisService.categorize_course(
            "Calculus and Linear Algebra"
        )
        assert result == SubjectCategory.STEM

    @pytest.mark.asyncio
    async def test_categorize_course_business(self):
        """Test course categorization for business subjects."""
        result = await CourseAnalysisService.categorize_course(
            "Strategic Management",
            "Business strategy and leadership principles"
        )
        assert result == SubjectCategory.BUSINESS

        result = await CourseAnalysisService.categorize_course(
            "Marketing Fundamentals"
        )
        assert result == SubjectCategory.BUSINESS

    @pytest.mark.asyncio
    async def test_categorize_course_humanities(self):
        """Test course categorization for humanities subjects."""
        result = await CourseAnalysisService.categorize_course(
            "Introduction to Philosophy",
            "Exploring philosophical thought and literature"
        )
        assert result == SubjectCategory.HUMANITIES

        result = await CourseAnalysisService.categorize_course(
            "World History"
        )
        assert result == SubjectCategory.HUMANITIES

    @pytest.mark.asyncio
    async def test_categorize_course_arts(self):
        """Test course categorization for arts subjects."""
        result = await CourseAnalysisService.categorize_course(
            "Digital Art and Design",
            "Creative visual arts and multimedia design"
        )
        assert result == SubjectCategory.ARTS

        result = await CourseAnalysisService.categorize_course(
            "Music Theory"
        )
        assert result == SubjectCategory.ARTS

    @pytest.mark.asyncio
    async def test_categorize_course_other(self):
        """Test course categorization for uncategorized subjects."""
        result = await CourseAnalysisService.categorize_course(
            "Physical Education"
        )
        assert result == SubjectCategory.OTHER

        result = await CourseAnalysisService.categorize_course(
            "Random Course Name"
        )
        assert result == SubjectCategory.OTHER

    @pytest.mark.asyncio
    async def test_build_analysis_context(self, db_session, test_user, test_course):
        """Test building analysis context."""
        # Create additional course for context
        other_course = Course(
            user_id=test_user.id,
            course_name="Statistics",
            subject_category="STEM",
            grade="B+",
            semester="Spring",
            year=2024
        )
        db_session.add(other_course)
        db_session.commit()

        context = await CourseAnalysisService.build_analysis_context(
            test_course, test_user, db_session, ["cognitive_preference"]
        )

        assert context["course"]["name"] == test_course.course_name
        assert context["course"]["category"] == test_course.subject_category
        assert context["user_history"]["total_courses"] == 1
        assert context["focus_areas"] == ["cognitive_preference"]
        assert "subject_distribution" in context["user_history"]

    def test_assess_grade_quality(self):
        """Test grade quality assessment."""
        assert CourseAnalysisService._assess_grade_quality("A+") == "excellent"
        assert CourseAnalysisService._assess_grade_quality("A") == "excellent"
        assert CourseAnalysisService._assess_grade_quality("B") == "good"
        assert CourseAnalysisService._assess_grade_quality("C") == "satisfactory"
        assert CourseAnalysisService._assess_grade_quality("D") == "challenging"
        assert CourseAnalysisService._assess_grade_quality("F") == "challenging"
        assert CourseAnalysisService._assess_grade_quality("XYZ") is None

    @pytest.mark.asyncio
    async def test_generate_initial_insights(self, test_course):
        """Test generation of initial insights."""
        context = {
            "user_history": {
                "subject_distribution": {"STEM": 2}
            }
        }
        
        insights = await CourseAnalysisService._generate_initial_insights(test_course, context)
        
        assert len(insights) >= 1
        assert any("performance" in insight["type"] for insight in insights)
        assert any("pattern" in insight["type"] for insight in insights)

    @pytest.mark.asyncio
    async def test_generate_profile_summary(self, test_insight, test_career_signal):
        """Test profile summary generation."""
        insights = [test_insight]
        signals = [test_career_signal]
        
        summary = await CourseAnalysisService.generate_profile_summary(insights, signals)
        
        assert "cognitive_preferences" in summary
        assert "work_style_indicators" in summary
        assert "subject_affinities" in summary
        assert "career_readiness" in summary
        assert "confidence_score" in summary
        assert 0 <= summary["confidence_score"] <= 1

    def test_analyze_cognitive_patterns(self, test_insight):
        """Test cognitive pattern analysis."""
        insights = [test_insight]
        patterns = CourseAnalysisService._analyze_cognitive_patterns(insights)
        
        assert "analytical_thinking" in patterns
        assert "creative_thinking" in patterns
        assert "concrete_vs_abstract" in patterns
        assert "detail_vs_big_picture" in patterns
        
        # All scores should be between -1 and 1 or 0 and 1
        for score in patterns.values():
            assert -1 <= score <= 1

    def test_analyze_work_style_patterns(self, test_insight):
        """Test work style pattern analysis."""
        # Create work style insight
        test_insight.insight_type = "work_style"
        test_insight.insight_value = {"collaboration": "preferred", "structure": "flexible"}
        
        insights = [test_insight]
        patterns = CourseAnalysisService._analyze_work_style_patterns(insights)
        
        assert "collaboration_preference" in patterns
        assert "structure_preference" in patterns
        assert "autonomy_preference" in patterns
        assert "pace_preference" in patterns
        
        # All scores should be between 0 and 1
        for score in patterns.values():
            assert 0 <= score <= 1

    def test_analyze_subject_patterns(self, test_insight):
        """Test subject affinity pattern analysis."""
        # Create subject affinity insight
        test_insight.insight_type = "subject_affinity"
        test_insight.insight_value = {
            "authentic": True,
            "subject": "data science",
            "reason": "enjoys problem-solving"
        }
        
        insights = [test_insight]
        patterns = CourseAnalysisService._analyze_subject_patterns(insights)
        
        assert "authentic_interests" in patterns
        assert "forced_choices" in patterns
        assert "engagement_patterns" in patterns
        assert "difficulty_tolerance" in patterns
        
        assert len(patterns["authentic_interests"]) == 1
        assert patterns["authentic_interests"][0]["subject"] == "data science"

    def test_analyze_career_signals(self, test_career_signal):
        """Test career signal analysis."""
        signals = [test_career_signal]
        readiness = CourseAnalysisService._analyze_career_signals(signals)
        
        assert "strongest_signals" in readiness
        assert "developing_areas" in readiness
        assert "overall_readiness" in readiness
        assert "esco_alignment" in readiness
        
        assert 0 <= readiness["overall_readiness"] <= 1

    @pytest.mark.asyncio
    async def test_analyze_signal_patterns(self, test_career_signal):
        """Test signal pattern analysis."""
        signals = [test_career_signal]
        patterns = await CourseAnalysisService.analyze_signal_patterns(signals)
        
        assert "signal_distribution" in patterns
        assert "strength_trends" in patterns
        assert "cross_course_patterns" in patterns
        assert "consistency_score" in patterns
        
        assert test_career_signal.signal_type in patterns["signal_distribution"]

    @pytest.mark.asyncio
    async def test_identify_trends_empty_signals(self):
        """Test trend identification with empty signals."""
        trends = await CourseAnalysisService.identify_trends([])
        
        assert "emerging_strengths" in trends
        assert "declining_areas" in trends
        assert "stable_competencies" in trends
        assert "recommendation_priority" in trends
        
        assert len(trends["emerging_strengths"]) == 0

    @pytest.mark.asyncio
    async def test_identify_trends_with_signals(self, db_session, test_user, test_course):
        """Test trend identification with actual signals."""
        # Create signals with different strengths
        signal1 = CareerSignal(
            user_id=test_user.id,
            course_id=test_course.id,
            signal_type="analytical_thinking",
            strength_score=0.6,
            evidence_source="Earlier assessment"
        )
        
        signal2 = CareerSignal(
            user_id=test_user.id,
            course_id=test_course.id,
            signal_type="analytical_thinking",
            strength_score=0.8,
            evidence_source="Recent assessment"
        )
        
        db_session.add_all([signal1, signal2])
        db_session.commit()
        
        trends = await CourseAnalysisService.identify_trends([signal1, signal2])
        
        assert len(trends["emerging_strengths"]) == 1
        assert trends["emerging_strengths"][0]["signal_type"] == "analytical_thinking"
        assert trends["emerging_strengths"][0]["improvement"] == 0.2

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, test_career_signal):
        """Test recommendation generation."""
        signals = [test_career_signal]
        pattern_analysis = {
            "strength_trends": {
                "analytical_thinking": {
                    "trend": "increasing",
                    "slope": 0.1
                }
            }
        }
        esco_paths = [
            {
                "occupation_title": "Data Analyst",
                "alignment_score": 0.8
            }
        ]
        
        recommendations = await CourseAnalysisService.generate_recommendations(
            signals, pattern_analysis, esco_paths
        )
        
        assert len(recommendations) >= 1
        assert any(rec["type"] == "leverage_strength" for rec in recommendations)
        assert any(rec["type"] == "career_exploration" for rec in recommendations)
        
        # Check recommendation structure
        for rec in recommendations:
            assert "type" in rec
            assert "priority" in rec
            assert "title" in rec
            assert "description" in rec
            assert "action_items" in rec

    @pytest.mark.asyncio
    async def test_calculate_development_priority(self):
        """Test development priority calculation."""
        signal_high = {"strength": 0.7, "type": "analytical_thinking"}
        signal_medium = {"strength": 0.5, "type": "creative_thinking"}
        signal_low = {"strength": 0.3, "type": "leadership"}
        
        profile_summary = {}
        
        assert CourseAnalysisService._calculate_development_priority(signal_high, profile_summary) == "high"
        assert CourseAnalysisService._calculate_development_priority(signal_medium, profile_summary) == "medium"
        assert CourseAnalysisService._calculate_development_priority(signal_low, profile_summary) == "low"

    def test_determine_career_cluster(self):
        """Test career cluster determination."""
        assert CourseAnalysisService._determine_career_cluster("analytical_thinking") == "Data & Analysis"
        assert CourseAnalysisService._determine_career_cluster("creative_problem_solving") == "Innovation & Design"
        assert CourseAnalysisService._determine_career_cluster("interpersonal_skills") == "Communication & Relations"
        assert CourseAnalysisService._determine_career_cluster("unknown_signal") == "General"

    def test_generate_next_steps(self):
        """Test next steps generation."""
        steps = CourseAnalysisService._generate_next_steps("analytical_thinking", 0.5)
        assert len(steps) == 3
        assert all(isinstance(step, str) for step in steps)
        assert any("data analysis" in step.lower() for step in steps)

        # Test with high strength
        steps_high = CourseAnalysisService._generate_next_steps("analytical_thinking", 0.8)
        assert any("advanced" in step.lower() for step in steps_high)

        # Test with low strength
        steps_low = CourseAnalysisService._generate_next_steps("analytical_thinking", 0.3)
        assert any("start with basics" in step.lower() for step in steps_low)

    def test_create_interdisciplinary_path(self):
        """Test interdisciplinary path creation."""
        signal1 = {
            "type": "analytical_thinking",
            "strength": 0.8,
            "esco_mapping": {
                "skill_groups": ["analytical skills", "data analysis"],
                "esco_categories": ["S1.1.1", "S1.2.1"],
                "related_occupations": ["data analyst", "researcher"]
            }
        }
        
        signal2 = {
            "type": "creative_problem_solving",
            "strength": 0.7,
            "esco_mapping": {
                "skill_groups": ["creativity", "innovation"],
                "esco_categories": ["S1.4.1", "S3.1.1"],
                "related_occupations": ["designer", "consultant"]
            }
        }
        
        path = CourseAnalysisService._create_interdisciplinary_path([signal1, signal2])
        
        assert path["path_id"] == "interdisciplinary"
        assert len(path["primary_signals"]) == 2
        assert "analytical_thinking" in path["primary_signals"]
        assert "creative_problem_solving" in path["primary_signals"]
        assert 0.7 <= path["alignment_score"] <= 0.8  # Average of the two strengths
        assert len(path["skill_requirements"]) <= 5  # Should be limited to top 5

    def test_find_interdisciplinary_occupations(self):
        """Test finding interdisciplinary occupations."""
        # Test known combinations
        occupations = CourseAnalysisService._find_interdisciplinary_occupations(
            "analytical_thinking", "creative_problem_solving"
        )
        assert "UX researcher" in occupations or "product manager" in occupations
        
        # Test reverse order
        occupations_reverse = CourseAnalysisService._find_interdisciplinary_occupations(
            "creative_problem_solving", "analytical_thinking"
        )
        assert occupations == occupations_reverse
        
        # Test unknown combination
        unknown_occupations = CourseAnalysisService._find_interdisciplinary_occupations(
            "unknown_signal1", "unknown_signal2"
        )
        assert "interdisciplinary specialist" in unknown_occupations

    def test_calculate_impact_potential(self):
        """Test impact potential calculation."""
        profile_summary = {}
        
        # Test known signal types
        impact = CourseAnalysisService._calculate_impact_potential("analytical_thinking", profile_summary)
        assert 0.0 <= impact <= 1.0
        assert impact == 0.9  # High demand skill
        
        impact = CourseAnalysisService._calculate_impact_potential("unknown_signal", profile_summary)
        assert impact == 0.6  # Default value

    def test_suggest_development_methods(self):
        """Test development method suggestions."""
        methods = CourseAnalysisService._suggest_development_methods("analytical_thinking")
        assert len(methods) >= 1
        assert any("data analysis" in method.lower() for method in methods)
        
        methods = CourseAnalysisService._suggest_development_methods("creative_problem_solving")
        assert any("design thinking" in method.lower() for method in methods)
        
        methods = CourseAnalysisService._suggest_development_methods("unknown_signal")
        assert "Seek relevant training opportunities" in methods