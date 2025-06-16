import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.esco_integration_service import ESCOIntegrationService
from app.models.course import CareerSignal, PsychologicalInsight

class TestESCOIntegrationService:
    """Test suite for ESCOIntegrationService."""

    @pytest.fixture
    def esco_service(self):
        """Create ESCO integration service instance."""
        return ESCOIntegrationService()

    @pytest.mark.asyncio
    async def test_map_signals_to_esco_categories(self, esco_service, test_career_signal):
        """Test mapping career signals to ESCO categories."""
        signals = [test_career_signal]
        
        result = await esco_service.map_signals_to_esco_categories(signals)
        
        assert "signal_mappings" in result
        assert "top_skill_groups" in result
        assert "recommended_occupations" in result
        assert "confidence_score" in result
        
        # Check signal mapping structure
        signal_mapping = result["signal_mappings"][0]
        assert signal_mapping["signal_type"] == test_career_signal.signal_type
        assert "esco_categories" in signal_mapping
        assert "skill_groups" in signal_mapping
        assert "related_occupations" in signal_mapping

    @pytest.mark.asyncio
    async def test_map_signals_empty_list(self, esco_service):
        """Test mapping with empty signals list."""
        result = await esco_service.map_signals_to_esco_categories([])
        
        assert result["signal_mappings"] == []
        assert result["top_skill_groups"] == []
        assert result["recommended_occupations"] == []
        assert result["confidence_score"] == 0.0

    @pytest.mark.asyncio
    async def test_generate_career_recommendations(self, esco_service, test_career_signal):
        """Test career recommendation generation."""
        signals = [test_career_signal]
        profile_summary = {
            "cognitive_preferences": {"analytical_thinking": 0.8},
            "work_style_indicators": {"collaboration_preference": 0.6},
            "subject_affinities": [{"subject": "data science", "strength": 0.9}]
        }
        
        recommendations = await esco_service.generate_career_recommendations(signals, profile_summary)
        
        assert len(recommendations) >= 1
        
        for rec in recommendations:
            assert "occupation_code" in rec
            assert "occupation_title" in rec
            assert "alignment_score" in rec
            assert "skill_match_details" in rec
            assert "development_path" in rec
            assert 0 <= rec["alignment_score"] <= 1

    @pytest.mark.asyncio
    async def test_generate_career_recommendations_empty_signals(self, esco_service):
        """Test career recommendations with empty signals."""
        profile_summary = {
            "cognitive_preferences": {},
            "work_style_indicators": {},
            "subject_affinities": []
        }
        
        recommendations = await esco_service.generate_career_recommendations([], profile_summary)
        
        # Should return some general recommendations
        assert len(recommendations) >= 1
        assert all(rec["alignment_score"] >= 0 for rec in recommendations)

    def test_map_signal_to_esco_analytical_thinking(self, esco_service):
        """Test mapping analytical thinking signal to ESCO."""
        mapping = esco_service._map_signal_to_esco("analytical_thinking", 0.8)
        
        assert "esco_categories" in mapping
        assert "skill_groups" in mapping
        assert "related_occupations" in mapping
        assert "confidence" in mapping
        
        # Should include relevant ESCO categories for analytical thinking
        assert any("analytical" in cat.lower() for cat in mapping["skill_groups"])
        assert any("analyst" in occ.lower() for occ in mapping["related_occupations"])

    def test_map_signal_to_esco_creative_thinking(self, esco_service):
        """Test mapping creative thinking signal to ESCO."""
        mapping = esco_service._map_signal_to_esco("creative_problem_solving", 0.7)
        
        assert "creative" in str(mapping["skill_groups"]).lower() or "innovation" in str(mapping["skill_groups"]).lower()
        assert any("design" in occ.lower() or "creative" in occ.lower() for occ in mapping["related_occupations"])

    def test_map_signal_to_esco_unknown_signal(self, esco_service):
        """Test mapping unknown signal type to ESCO."""
        mapping = esco_service._map_signal_to_esco("unknown_signal_type", 0.5)
        
        # Should return generic mapping
        assert len(mapping["esco_categories"]) >= 1
        assert len(mapping["skill_groups"]) >= 1
        assert len(mapping["related_occupations"]) >= 1
        assert mapping["confidence"] <= 0.5

    def test_calculate_alignment_score_high_match(self, esco_service):
        """Test alignment score calculation with high signal match."""
        signal_data = {
            "type": "analytical_thinking",
            "strength": 0.9,
            "esco_mapping": {
                "skill_groups": ["analytical skills", "data analysis"],
                "esco_categories": ["S1.1.1", "S1.2.1"]
            }
        }
        
        occupation_data = {
            "required_skills": ["analytical skills", "data analysis", "problem solving"],
            "skill_categories": ["S1.1.1", "S1.2.1", "S1.3.1"],
            "occupation_type": "analytical"
        }
        
        score = esco_service._calculate_alignment_score(signal_data, occupation_data)
        
        assert 0.7 <= score <= 1.0  # High match expected

    def test_calculate_alignment_score_low_match(self, esco_service):
        """Test alignment score calculation with low signal match."""
        signal_data = {
            "type": "creative_problem_solving",
            "strength": 0.6,
            "esco_mapping": {
                "skill_groups": ["creativity", "innovation"],
                "esco_categories": ["S3.1.1", "S3.2.1"]
            }
        }
        
        occupation_data = {
            "required_skills": ["analytical skills", "data analysis"],
            "skill_categories": ["S1.1.1", "S1.2.1"],
            "occupation_type": "analytical"
        }
        
        score = esco_service._calculate_alignment_score(signal_data, occupation_data)
        
        assert 0.0 <= score <= 0.5  # Low match expected

    def test_generate_development_path_entry_level(self, esco_service):
        """Test development path generation for entry-level occupation."""
        occupation_data = {
            "occupation_title": "Junior Data Analyst",
            "required_skills": ["data analysis", "statistics", "SQL"],
            "experience_level": "entry"
        }
        
        signal_strengths = {"analytical_thinking": 0.7, "technical_skills": 0.5}
        
        path = esco_service._generate_development_path(occupation_data, signal_strengths)
        
        assert "immediate_steps" in path
        assert "medium_term_goals" in path
        assert "skill_gaps" in path
        assert "estimated_timeline" in path
        
        # Entry level should have shorter timeline
        assert "6 months" in path["estimated_timeline"] or "1 year" in path["estimated_timeline"]

    def test_generate_development_path_senior_level(self, esco_service):
        """Test development path generation for senior-level occupation."""
        occupation_data = {
            "occupation_title": "Senior Data Scientist",
            "required_skills": ["machine learning", "advanced statistics", "leadership"],
            "experience_level": "senior"
        }
        
        signal_strengths = {"analytical_thinking": 0.8, "leadership": 0.4}
        
        path = esco_service._generate_development_path(occupation_data, signal_strengths)
        
        # Senior level should have longer timeline and more complex steps
        assert "2-3 years" in path["estimated_timeline"] or "3-5 years" in path["estimated_timeline"]
        assert len(path["skill_gaps"]) >= 1  # Should identify leadership gap

    def test_identify_skill_gaps(self, esco_service):
        """Test skill gap identification."""
        required_skills = ["data analysis", "machine learning", "leadership", "communication"]
        signal_strengths = {
            "analytical_thinking": 0.8,  # Maps to data analysis
            "technical_skills": 0.6,     # Maps to machine learning
            "leadership": 0.3,           # Gap here
            "communication": 0.2         # Gap here
        }
        
        gaps = esco_service._identify_skill_gaps(required_skills, signal_strengths)
        
        assert len(gaps) >= 2
        assert any(gap["skill"] == "leadership" for gap in gaps)
        assert any(gap["skill"] == "communication" for gap in gaps)
        
        # Check gap severity
        leadership_gap = next(gap for gap in gaps if gap["skill"] == "leadership")
        assert leadership_gap["severity"] == "high"  # 0.3 is low strength

    def test_get_occupation_database_known_occupation(self, esco_service):
        """Test occupation database retrieval for known occupation."""
        occupation = esco_service._get_occupation_database("data analyst")
        
        assert "required_skills" in occupation
        assert "skill_categories" in occupation
        assert "experience_level" in occupation
        assert "growth_outlook" in occupation
        
        # Should contain relevant skills for data analyst
        skills_str = str(occupation["required_skills"]).lower()
        assert any(skill in skills_str for skill in ["data", "analysis", "analytical"])

    def test_get_occupation_database_unknown_occupation(self, esco_service):
        """Test occupation database retrieval for unknown occupation."""
        occupation = esco_service._get_occupation_database("unknown job title")
        
        # Should return generic occupation data
        assert "required_skills" in occupation
        assert occupation["experience_level"] == "entry"
        assert len(occupation["required_skills"]) >= 1

    def test_aggregate_skill_recommendations(self, esco_service):
        """Test skill recommendation aggregation."""
        signal_mappings = [
            {
                "signal_type": "analytical_thinking",
                "strength": 0.8,
                "skill_groups": ["analytical skills", "data analysis"],
                "esco_categories": ["S1.1.1", "S1.2.1"]
            },
            {
                "signal_type": "creative_problem_solving",
                "strength": 0.7,
                "skill_groups": ["creativity", "innovation"],
                "esco_categories": ["S3.1.1", "S3.2.1"]
            }
        ]
        
        aggregated = esco_service._aggregate_skill_recommendations(signal_mappings)
        
        assert "top_skill_groups" in aggregated
        assert "skill_category_distribution" in aggregated
        assert "interdisciplinary_opportunities" in aggregated
        
        # Should include skills from both signals
        all_skills = [skill["name"] for skill in aggregated["top_skill_groups"]]
        assert any("analytical" in skill.lower() for skill in all_skills)
        assert any("creative" in skill.lower() or "innovation" in skill.lower() for skill in all_skills)

    def test_calculate_category_confidence(self, esco_service):
        """Test ESCO category confidence calculation."""
        signal_mappings = [
            {
                "signal_type": "analytical_thinking",
                "strength": 0.8,
                "esco_categories": ["S1.1.1", "S1.2.1"],
                "confidence": 0.9
            },
            {
                "signal_type": "technical_skills",
                "strength": 0.7,
                "esco_categories": ["S1.1.1", "S2.1.1"],
                "confidence": 0.8
            }
        ]
        
        confidence = esco_service._calculate_category_confidence(signal_mappings)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence >= 0.7  # Should be high given strong signals

    def test_calculate_category_confidence_weak_signals(self, esco_service):
        """Test confidence calculation with weak signals."""
        signal_mappings = [
            {
                "signal_type": "analytical_thinking",
                "strength": 0.3,
                "esco_categories": ["S1.1.1"],
                "confidence": 0.4
            }
        ]
        
        confidence = esco_service._calculate_category_confidence(signal_mappings)
        
        assert confidence <= 0.5  # Should be low given weak signals

    def test_find_interdisciplinary_paths(self, esco_service):
        """Test interdisciplinary career path finding."""
        skill_groups = [
            {"name": "analytical skills", "strength": 0.8, "category": "S1.1.1"},
            {"name": "creativity", "strength": 0.7, "category": "S3.1.1"},
            {"name": "communication", "strength": 0.6, "category": "S2.1.1"}
        ]
        
        paths = esco_service._find_interdisciplinary_paths(skill_groups)
        
        assert len(paths) >= 1
        
        for path in paths:
            assert "path_name" in path
            assert "combining_skills" in path
            assert "example_occupations" in path
            assert "alignment_strength" in path
            assert len(path["combining_skills"]) >= 2  # Should combine multiple skills

    def test_map_profile_to_occupations(self, esco_service):
        """Test profile mapping to occupations."""
        profile_summary = {
            "cognitive_preferences": {"analytical_thinking": 0.8, "creative_thinking": 0.6},
            "work_style_indicators": {"collaboration_preference": 0.7, "autonomy_preference": 0.5},
            "subject_affinities": [
                {"subject": "data science", "strength": 0.9},
                {"subject": "design", "strength": 0.6}
            ]
        }
        
        occupations = esco_service._map_profile_to_occupations(profile_summary)
        
        assert len(occupations) >= 1
        
        for occ in occupations:
            assert "occupation_code" in occ
            assert "occupation_title" in occ
            assert "match_score" in occ
            assert "matching_attributes" in occ
            assert 0 <= occ["match_score"] <= 1

    def test_enhance_with_esco_metadata(self, esco_service):
        """Test enhancement with ESCO metadata."""
        base_recommendation = {
            "occupation_code": "2512.1",
            "occupation_title": "Data Analyst",
            "alignment_score": 0.8
        }
        
        enhanced = esco_service._enhance_with_esco_metadata(base_recommendation)
        
        assert "esco_uri" in enhanced
        assert "related_skills" in enhanced
        assert "alternative_titles" in enhanced
        assert "salary_range" in enhanced
        assert "growth_outlook" in enhanced
        
        # Should contain ESCO-compliant URI
        assert enhanced["esco_uri"].startswith("http")

    @pytest.mark.asyncio
    async def test_get_skill_development_suggestions(self, esco_service):
        """Test skill development suggestions."""
        skill_gaps = [
            {"skill": "machine learning", "severity": "high", "current_level": 0.2},
            {"skill": "leadership", "severity": "medium", "current_level": 0.4}
        ]
        
        suggestions = await esco_service.get_skill_development_suggestions(skill_gaps)
        
        assert len(suggestions) == 2
        
        for suggestion in suggestions:
            assert "skill" in suggestion
            assert "priority" in suggestion
            assert "resources" in suggestion
            assert "timeline" in suggestion
            assert "milestones" in suggestion
            
            # High severity gaps should have high priority
            if suggestion["skill"] == "machine learning":
                assert suggestion["priority"] == "high"

    def test_calculate_career_readiness_score(self, esco_service):
        """Test career readiness score calculation."""
        signal_mappings = [
            {
                "signal_type": "analytical_thinking",
                "strength": 0.8,
                "esco_categories": ["S1.1.1"],
                "confidence": 0.9
            },
            {
                "signal_type": "technical_skills",
                "strength": 0.6,
                "esco_categories": ["S1.2.1"],
                "confidence": 0.7
            }
        ]
        
        occupation_requirements = {
            "required_skills": ["analytical skills", "technical skills", "communication"],
            "experience_level": "entry"
        }
        
        readiness = esco_service._calculate_career_readiness_score(signal_mappings, occupation_requirements)
        
        assert 0.0 <= readiness <= 1.0
        assert readiness >= 0.5  # Should be moderately ready given skills match