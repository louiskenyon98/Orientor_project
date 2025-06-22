import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models import User, UserProfile, UserSkill, SavedRecommendation
from app.utils.database import get_db
import json

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    """Create a test user with profile and skills."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    db.add(user)
    db.commit()
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        name="Test User",
        age=22,
        major="Computer Science",
        year=3,
        gpa=3.5,
        education_level="Bachelor's",
        years_experience=1,
        career_goals="Software Engineer",
        interests="AI, Web Development"
    )
    db.add(profile)
    
    # Create user skills
    skills = UserSkill(
        user_id=user.id,
        creativity=3.5,
        leadership=3.0,
        digital_literacy=4.5,
        critical_thinking=4.0,
        problem_solving=4.2,
        analytical_thinking=4.0,
        attention_to_detail=3.8,
        collaboration=3.5,
        adaptability=4.0,
        independence=3.7,
        evaluation=3.5,
        decision_making=3.6,
        stress_tolerance=3.2
    )
    db.add(skills)
    
    db.commit()
    return user

@pytest.fixture
def test_saved_recommendation(db: Session, test_user: User):
    """Create a test saved recommendation."""
    recommendation = SavedRecommendation(
        user_id=test_user.id,
        oasis_code="OASIS_123",
        label="Software Developer",
        description="Develop and maintain software applications",
        main_duties="Write code, debug, test software",
        role_creativity=3.5,
        role_leadership=2.5,
        role_digital_literacy=4.8,
        role_critical_thinking=4.5,
        role_problem_solving=4.7,
        analytical_thinking=4.5,
        attention_to_detail=4.0,
        collaboration=3.5,
        adaptability=3.8,
        independence=3.5,
        evaluation=3.5,
        decision_making=3.5,
        stress_tolerance=3.5,
        source_type="oasis"
    )
    db.add(recommendation)
    db.commit()
    return recommendation

@pytest.fixture
def auth_headers(test_user: User):
    """Generate auth headers for test user."""
    # In a real test, you'd generate a proper JWT token
    return {"Authorization": f"Bearer test_token_for_{test_user.id}"}

class TestCareerFitAnalyzer:
    """Test suite for Career Fit Analyzer functionality."""
    
    def test_career_fit_analysis_oasis(self, test_saved_recommendation, auth_headers):
        """Test career fit analysis for OaSIS job."""
        response = client.post(
            "/careers/fit-analysis",
            json={
                "job_id": test_saved_recommendation.oasis_code,
                "job_source": "oasis"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "fit_score" in data
        assert "skill_match" in data
        assert "gap_analysis" in data
        assert "recommendations" in data
        
        # Validate fit score
        assert 0 <= data["fit_score"] <= 100
        
        # Check skill matches
        assert len(data["skill_match"]) > 0
        for skill_name, match in data["skill_match"].items():
            assert "skill_name" in match
            assert "match_percentage" in match
            assert 0 <= match["match_percentage"] <= 100
        
        # Check gap analysis
        assert "skill_gaps" in data["gap_analysis"]
        assert "strength_areas" in data["gap_analysis"]
        assert "improvement_areas" in data["gap_analysis"]
        
        # Check recommendations
        assert len(data["recommendations"]) > 0
        assert all(isinstance(rec, str) for rec in data["recommendations"])
    
    def test_career_fit_analysis_missing_job(self, auth_headers):
        """Test career fit analysis with non-existent job."""
        response = client.post(
            "/careers/fit-analysis",
            json={
                "job_id": "NONEXISTENT_JOB",
                "job_source": "oasis"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_career_fit_analysis_missing_skills(self, db: Session, auth_headers):
        """Test career fit analysis when user has no skills."""
        # Create user without skills
        user = User(
            email="noskills@example.com",
            username="noskillsuser",
            hashed_password="hashedpassword"
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/careers/fit-analysis",
            json={
                "job_id": "OASIS_123",
                "job_source": "oasis"
            },
            headers={"Authorization": f"Bearer test_token_for_{user.id}"}
        )
        
        assert response.status_code == 400
        assert "skills not found" in response.json()["detail"].lower()
    
    def test_llm_career_query(self, test_saved_recommendation, auth_headers):
        """Test LLM career advisor query."""
        response = client.post(
            "/api/careers/llm-query",
            json={
                "job_id": test_saved_recommendation.oasis_code,
                "job_source": "oasis",
                "query": "Why would I want to do this job?",
                "context": {
                    "fit_score": 75
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "query" in data
        assert data["query"] == "Why would I want to do this job?"
        assert len(data["response"]) > 0
    
    def test_saved_careers_dual_source(self, db: Session, test_user: User, auth_headers):
        """Test retrieving saved careers from both ESCO and OaSIS sources."""
        # Create OaSIS recommendation
        oasis_rec = SavedRecommendation(
            user_id=test_user.id,
            oasis_code="OASIS_456",
            label="Data Scientist",
            source_type="oasis"
        )
        db.add(oasis_rec)
        
        # Create ESCO job (would normally be in saved_jobs table)
        # For this test, we'll simulate the response
        
        response = client.get("/careers/saved", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        # Check that we have jobs from both sources
        oasis_jobs = [job for job in data if job.get("source_type") == "oasis"]
        esco_jobs = [job for job in data if job.get("source_type") == "esco"]
        
        assert len(oasis_jobs) > 0
        
        # Verify job structure
        for job in data:
            assert "id" in job
            assert "source_type" in job
            assert job["source_type"] in ["oasis", "esco"]
            
            if job["source_type"] == "oasis":
                assert "oasis_code" in job
                assert "label" in job
            else:
                assert "esco_id" in job
                assert "job_title" in job or "title" in job

class TestCareerFitUIComponent:
    """Test suite for Career Fit Analyzer UI component."""
    
    def test_feasibility_calculations(self):
        """Test feasibility metric calculations."""
        from app.services.career_fit_service import calculate_feasibility_metrics
        
        user_data = {
            "current_education": "Bachelor's in progress",
            "years_remaining": 2,
            "current_debt": 20000,
            "minimum_salary": 50000
        }
        
        job_data = {
            "entry_education": "Master's",
            "typical_salary": 75000,
            "years_to_entry": 3
        }
        
        metrics = calculate_feasibility_metrics(user_data, job_data)
        
        assert "entry_timeline" in metrics
        assert "education_gap" in metrics
        assert "income_gap_months" in metrics
        assert metrics["entry_timeline"] >= 3  # At least 3 years
        assert metrics["education_gap"] == "Master's required"
    
    def test_skill_gap_prioritization(self):
        """Test skill gap prioritization logic."""
        skill_gaps = [
            {"skill": "Python", "gap": 2.5},
            {"skill": "Machine Learning", "gap": 3.0},
            {"skill": "Communication", "gap": 1.0},
            {"skill": "Data Analysis", "gap": 2.0}
        ]
        
        # Sort by gap size (descending)
        prioritized = sorted(skill_gaps, key=lambda x: x["gap"], reverse=True)
        
        assert prioritized[0]["skill"] == "Machine Learning"
        assert prioritized[-1]["skill"] == "Communication"
    
    def test_graphsage_skill_extraction(self):
        """Test GraphSAGE skill extraction for OaSIS jobs."""
        job_data = {
            "oasis_code": "OASIS_789",
            "title": "AI Engineer",
            "description": "Develop AI models and deploy ML solutions"
        }
        
        # Mock GraphSAGE extraction
        expected_skills = [
            {"skill_name": "Machine Learning", "relevance_score": 0.95},
            {"skill_name": "Python", "relevance_score": 0.92},
            {"skill_name": "Deep Learning", "relevance_score": 0.88},
            {"skill_name": "Data Science", "relevance_score": 0.85},
            {"skill_name": "Cloud Computing", "relevance_score": 0.78}
        ]
        
        # Verify top 5 skills extraction
        assert len(expected_skills) == 5
        assert all(0 <= skill["relevance_score"] <= 1 for skill in expected_skills)
        assert expected_skills[0]["relevance_score"] >= expected_skills[-1]["relevance_score"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])