import pytest
from unittest.mock import Mock, patch
from app.services.course_analysis_service import CourseAnalysisService
from app.schemas.course import SubjectCategory

class TestCourseAnalysisServiceSimple:
    """Simplified test suite for CourseAnalysisService that works without full database setup."""

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

    def test_assess_grade_quality(self):
        """Test grade quality assessment."""
        assert CourseAnalysisService._assess_grade_quality("A+") == "excellent"
        assert CourseAnalysisService._assess_grade_quality("A") == "excellent"
        assert CourseAnalysisService._assess_grade_quality("B") == "good"
        assert CourseAnalysisService._assess_grade_quality("C") == "satisfactory"
        assert CourseAnalysisService._assess_grade_quality("D") == "challenging"
        assert CourseAnalysisService._assess_grade_quality("F") == "challenging"
        assert CourseAnalysisService._assess_grade_quality("XYZ") is None

    async def test_generate_initial_insights(self):
        """Test generation of initial insights."""
        # Create mock course
        mock_course = Mock()
        mock_course.course_name = "Data Science"
        mock_course.subject_category = "STEM"
        mock_course.grade = "A"
        mock_course.description = "Introduction to data science"
        
        context = {
            "user_history": {
                "subject_distribution": {"STEM": 2}
            }
        }
        
        insights = await CourseAnalysisService._generate_initial_insights(mock_course, context)
        
        assert len(insights) >= 1
        assert any("performance" in insight["type"] for insight in insights)

    async def test_generate_profile_summary(self):
        """Test profile summary generation."""
        # Create mock insights and signals
        insights = [
            {
                "insight_type": "cognitive_preference",
                "insight_value": {"analytical_thinking": 0.8},
                "confidence_score": 0.85
            }
        ]
        
        signals = [
            {
                "signal_type": "analytical_thinking",
                "strength_score": 0.8
            }
        ]
        
        summary = await CourseAnalysisService.generate_profile_summary(insights, signals)
        
        assert "cognitive_preferences" in summary
        assert "work_style_indicators" in summary
        assert "subject_affinities" in summary
        assert "career_readiness" in summary
        assert "confidence_score" in summary
        assert 0 <= summary["confidence_score"] <= 1

    def test_analyze_cognitive_patterns(self):
        """Test cognitive pattern analysis."""
        # Create mock insight objects with attributes
        mock_insight = Mock()
        mock_insight.insight_type = "cognitive_preference"
        mock_insight.insight_value = {"analytical_thinking": 0.8}
        mock_insight.confidence_score = 0.85
        
        insights = [mock_insight]
        
        patterns = CourseAnalysisService._analyze_cognitive_patterns(insights)
        
        assert "analytical_thinking" in patterns
        assert "creative_thinking" in patterns
        assert "concrete_vs_abstract" in patterns
        assert "detail_vs_big_picture" in patterns
        
        # All scores should be between -1 and 1 or 0 and 1
        for score in patterns.values():
            assert -1 <= score <= 1

    def test_analyze_work_style_patterns(self):
        """Test work style pattern analysis."""
        # Create mock insight objects with attributes
        mock_insight = Mock()
        mock_insight.insight_type = "work_style"
        mock_insight.insight_value = {"collaboration": "preferred", "structure": "flexible"}
        mock_insight.confidence_score = 0.8
        
        insights = [mock_insight]
        
        patterns = CourseAnalysisService._analyze_work_style_patterns(insights)
        
        assert "collaboration_preference" in patterns
        assert "structure_preference" in patterns
        assert "autonomy_preference" in patterns
        assert "pace_preference" in patterns
        
        # All scores should be between 0 and 1
        for score in patterns.values():
            assert 0 <= score <= 1

    def test_analyze_subject_patterns(self):
        """Test subject affinity pattern analysis."""
        # Create mock insight objects with attributes
        mock_insight = Mock()
        mock_insight.insight_type = "subject_affinity"
        mock_insight.insight_value = {
            "authentic": True,
            "subject": "data science",
            "reason": "enjoys problem-solving"
        }
        mock_insight.confidence_score = 0.8
        
        insights = [mock_insight]
        
        patterns = CourseAnalysisService._analyze_subject_patterns(insights)
        
        assert "authentic_interests" in patterns
        assert "forced_choices" in patterns
        assert "engagement_patterns" in patterns
        assert "difficulty_tolerance" in patterns
        
        assert len(patterns["authentic_interests"]) == 1
        assert patterns["authentic_interests"][0]["subject"] == "data science"

    def test_analyze_career_signals(self):
        """Test career signal analysis."""
        # Create mock signal objects with attributes
        mock_signal = Mock()
        mock_signal.signal_type = "analytical_thinking"
        mock_signal.strength_score = 0.8
        
        signals = [mock_signal]
        
        readiness = CourseAnalysisService._analyze_career_signals(signals)
        
        assert "strongest_signals" in readiness
        assert "developing_areas" in readiness
        assert "overall_readiness" in readiness
        assert "esco_alignment" in readiness
        
        assert 0 <= readiness["overall_readiness"] <= 1

    async def test_analyze_signal_patterns(self):
        """Test signal pattern analysis."""
        signals = [
            {
                "signal_type": "analytical_thinking",
                "strength_score": 0.8,
                "extracted_at": "2024-01-01T00:00:00"
            }
        ]
        
        patterns = await CourseAnalysisService.analyze_signal_patterns(signals)
        
        assert "signal_distribution" in patterns
        assert "strength_trends" in patterns
        assert "cross_course_patterns" in patterns
        assert "consistency_score" in patterns

    async def test_identify_trends_empty_signals(self):
        """Test trend identification with empty signals."""
        trends = await CourseAnalysisService.identify_trends([])
        
        assert "emerging_strengths" in trends
        assert "declining_areas" in trends
        assert "stable_competencies" in trends
        assert "recommendation_priority" in trends
        
        assert len(trends["emerging_strengths"]) == 0

    async def test_generate_recommendations(self):
        """Test recommendation generation."""
        signals = [
            {
                "signal_type": "analytical_thinking",
                "strength_score": 0.8
            }
        ]
        
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
        
        # Check recommendation structure
        for rec in recommendations:
            assert "type" in rec
            assert "priority" in rec
            assert "title" in rec
            assert "description" in rec
            assert "action_items" in rec

    def test_basic_functionality(self):
        """Test basic service functionality."""
        # Test that the service can be imported and basic methods exist
        assert hasattr(CourseAnalysisService, 'categorize_course')
        assert hasattr(CourseAnalysisService, 'generate_profile_summary')
        assert hasattr(CourseAnalysisService, '_analyze_cognitive_patterns')
        assert hasattr(CourseAnalysisService, '_analyze_work_style_patterns')
        assert hasattr(CourseAnalysisService, '_analyze_subject_patterns')