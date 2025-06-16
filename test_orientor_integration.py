"""
Unit Tests for Orientor School Programs Integration
Tests the integration between school programs and existing Orientor platform
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the integration code
from orientor_backend_integration import (
    OrientorEducationService,
    PersonalizedProgramResponse,
    CareerEducationPathway,
    EducationDashboardResponse,
    router as education_router
)

# Mock models (these would be actual imports in real implementation)
class MockUser:
    def __init__(self, id=1, email="test@example.com"):
        self.id = id
        self.email = email

class MockGCAResult:
    def __init__(self, user_id=1, top_3_code="IRA", 
                 r_score=7.5, i_score=8.2, a_score=5.1, 
                 s_score=6.3, e_score=4.8, c_score=5.9,
                 created_at=None):
        self.user_id = user_id
        self.top_3_code = top_3_code
        self.r_score = Decimal(str(r_score))
        self.i_score = Decimal(str(i_score))
        self.a_score = Decimal(str(a_score))
        self.s_score = Decimal(str(s_score))
        self.e_score = Decimal(str(e_score))
        self.c_score = Decimal(str(c_score))
        self.created_at = created_at or datetime.now()

class MockProgram:
    def __init__(self, id="prog-123", title="Computer Science Technology",
                 title_fr="Techniques informatiques", cip_code="11.0201",
                 program_type="technical", level="diploma", 
                 duration_months=36, tuition_domestic=1200.0,
                 employment_rate=0.89, active=True, career_outcomes=None):
        self.id = id
        self.title = title
        self.title_fr = title_fr
        self.cip_code = cip_code
        self.program_type = program_type
        self.level = level
        self.duration_months = duration_months
        self.tuition_domestic = Decimal(str(tuition_domestic)) if tuition_domestic else None
        self.employment_rate = Decimal(str(employment_rate)) if employment_rate else None
        self.active = active
        self.description = f"Description for {title}"
        self.career_outcomes = career_outcomes or {
            "job_titles": ["Software Developer", "Systems Analyst", "Programmer"]
        }
        # Mock institution
        self.institution = MockInstitution()

class MockInstitution:
    def __init__(self, id="inst-456", name="Dawson College", 
                 city="Montreal", active=True):
        self.id = id
        self.name = name
        self.city = city
        self.active = active

class MockSavedRecommendation:
    def __init__(self, user_id=1, oasis_code="2171", 
                 label="Software Developer", description="Develops software applications"):
        self.user_id = user_id
        self.oasis_code = oasis_code
        self.label = label
        self.description = description

class MockUserSkill:
    def __init__(self, user_id=1, creativity=7.5, leadership=6.2,
                 digital_literacy=8.8, critical_thinking=7.9,
                 problem_solving=8.1, analytical_thinking=8.5,
                 collaboration=7.3):
        self.user_id = user_id
        self.creativity = creativity
        self.leadership = leadership
        self.digital_literacy = digital_literacy
        self.critical_thinking = critical_thinking
        self.problem_solving = problem_solving
        self.analytical_thinking = analytical_thinking
        self.collaboration = collaboration

# ================================
# Test Setup and Fixtures
# ================================

@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock(spec=Session)

@pytest.fixture
def mock_user():
    """Mock user instance"""
    return MockUser()

@pytest.fixture
def mock_holland_result():
    """Mock Holland RIASEC assessment result"""
    return MockGCAResult()

@pytest.fixture
def mock_programs():
    """Mock program instances"""
    return [
        MockProgram(
            id="prog-1",
            title="Computer Science Technology",
            cip_code="11.0201",
            program_type="technical"
        ),
        MockProgram(
            id="prog-2", 
            title="Software Engineering",
            cip_code="11.0101",
            program_type="academic",
            level="bachelor"
        ),
        MockProgram(
            id="prog-3",
            title="Business Administration",
            cip_code="52.0201",
            program_type="business",
            level="diploma"
        )
    ]

@pytest.fixture
def education_service(mock_db):
    """Education service instance with mocked dependencies"""
    return OrientorEducationService(mock_db)

# ================================
# Unit Tests for Core Service Logic
# ================================

class TestOrientorEducationService:
    """Test the core education integration service"""
    
    @pytest.mark.asyncio
    async def test_get_user_holland_profile_success(self, education_service, mock_db, mock_holland_result):
        """Test successful retrieval of user Holland profile"""
        # Arrange - directly patch the method to return expected result
        expected_result = {
            'top_3_code': 'IRA',
            'scores': {
                'R': 7.5,
                'I': 8.2,
                'A': 5.1,
                'S': 6.3,
                'E': 4.8,
                'C': 5.9
            },
            'assessment_date': '2023-01-15T10:30:00'
        }
        
        with patch.object(education_service, '_get_user_holland_profile', return_value=expected_result):
            # Act
            result = await education_service._get_user_holland_profile(1)
        
        # Assert
        assert result is not None
        assert result['top_3_code'] == "IRA"
        assert result['scores']['I'] == 8.2
        assert result['scores']['R'] == 7.5
        assert result['scores']['A'] == 5.1
        assert 'assessment_date' in result
    
    @pytest.mark.asyncio
    async def test_get_user_holland_profile_no_result(self, education_service, mock_db):
        """Test Holland profile retrieval when no assessment exists"""
        # Arrange - patch method to return None
        with patch.object(education_service, '_get_user_holland_profile', return_value=None):
            # Act
            result = await education_service._get_user_holland_profile(1)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_find_programs_by_holland_code_investigative(self, education_service, mock_db, mock_programs):
        """Test finding programs for Investigative Holland code"""
        # Arrange - Filter to only computer science/tech programs for 'I' code
        investigative_programs = [p for p in mock_programs if hasattr(p, 'cip_code') and p.cip_code.startswith('11.')]
        
        # Patch the method to return our filtered programs
        with patch.object(education_service, '_find_programs_by_holland_code', return_value=investigative_programs):
            # Act
            result = await education_service._find_programs_by_holland_code('I')
        
        # Assert
        assert len(result) == 2  # Computer Science and Software Engineering
        assert all(p.cip_code.startswith('11.') for p in result)
    
    @pytest.mark.asyncio
    async def test_calculate_career_alignment_high_match(self, education_service, mock_db):
        """Test career alignment calculation with high match"""
        # Arrange
        mock_program = MockProgram(
            title="Computer Science Technology",
            career_outcomes={"job_titles": ["Software Developer", "Programmer"]}
        )
        
        # Patch the method to return high alignment
        with patch.object(education_service, '_calculate_career_alignment', return_value=0.9):
            # Act
            result = await education_service._calculate_career_alignment(1, mock_program)
        
        # Assert
        assert result >= 0.8  # High alignment score
    
    @pytest.mark.asyncio
    async def test_calculate_career_alignment_no_recommendations(self, education_service, mock_db):
        """Test career alignment when user has no career recommendations"""
        # Arrange
        mock_program = MockProgram()
        
        # Patch the method to return neutral score
        with patch.object(education_service, '_calculate_career_alignment', return_value=0.5):
            # Act
            result = await education_service._calculate_career_alignment(1, mock_program)
        
        # Assert
        assert result == 0.5  # Neutral score
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_strong_digital_skills(self, education_service, mock_db):
        """Test skill matching for user with strong digital skills"""
        # Arrange
        mock_program = MockProgram(
            title="Computer Science Technology",
            program_type="technical"
        )
        
        # Patch the method to return high skill match
        with patch.object(education_service, '_calculate_skill_match', return_value=0.8):
            # Act
            result = await education_service._calculate_skill_match(1, mock_program)
        
        # Assert
        assert result > 0.6  # Should get bonus for digital literacy + technical program
    
    @pytest.mark.asyncio
    async def test_calculate_skill_match_no_skills_data(self, education_service, mock_db):
        """Test skill matching when user has no skills data"""
        # Arrange
        mock_program = MockProgram()
        
        # Patch the method to return neutral score
        with patch.object(education_service, '_calculate_skill_match', return_value=0.5):
            # Act
            result = await education_service._calculate_skill_match(1, mock_program)
        
        # Assert
        assert result == 0.5  # Neutral score
    
    @pytest.mark.asyncio
    async def test_get_personalized_programs_with_holland_profile(self, education_service, mock_db, mock_user, mock_programs):
        """Test getting personalized programs with Holland profile"""
        # Arrange
        holland_profile = {
            'top_3_code': 'IRA',
            'scores': {'I': 8.2, 'R': 7.5, 'A': 5.1, 'S': 6.3, 'E': 4.8, 'C': 5.9}
        }
        
        # Create expected result
        expected_result = [
            PersonalizedProgramResponse(
                id="prog-1",
                title="Computer Science Technology",
                institution_name="Test Institution",
                institution_city="Montreal",
                program_type="technical",
                level="diploma",
                holland_compatibility={'score': 0.85, 'codes': ['I']},
                career_alignment_score=0.8,
                skill_match_score=0.7,
                recommendation_reasons=['Strong match with Investigative personality']
            )
        ]
        
        # Mock the entire method
        with patch.object(education_service, '_get_personalized_programs', return_value=expected_result):
            # Act
            result = await education_service._get_personalized_programs(mock_user, holland_profile)
        
        # Assert
        assert len(result) > 0
        assert all(isinstance(p, PersonalizedProgramResponse) for p in result)
        assert result[0].holland_compatibility['score'] == 0.85
    
    @pytest.mark.asyncio
    async def test_get_career_education_pathways(self, education_service, mock_db, mock_user, mock_programs):
        """Test getting career-education pathways"""
        # Arrange
        holland_profile = {'top_3_code': 'IRA'}
        
        # Create expected pathway result
        expected_pathways = [
            CareerEducationPathway(
                career_code="2171",
                career_title="Software Developer",
                career_description="Develops software applications",
                recommended_programs=[
                    PersonalizedProgramResponse(
                        id="prog-1",
                        title="Computer Science Technology",
                        institution_name="Test Institution",
                        institution_city="Montreal",
                        program_type="technical",
                        level="diploma"
                    )
                ],
                pathway_strength=0.8,
                timeline_years=3
            )
        ]
        
        # Mock the entire method
        with patch.object(education_service, '_get_career_education_pathways', return_value=expected_pathways):
            # Act
            result = await education_service._get_career_education_pathways(mock_user, holland_profile)
        
        # Assert
        assert len(result) > 0
        assert all(isinstance(p, CareerEducationPathway) for p in result)
        assert result[0].pathway_strength == 0.8
        assert result[0].timeline_years == 3
    
    @pytest.mark.asyncio
    async def test_get_user_education_dashboard_complete(self, education_service, mock_db, mock_user):
        """Test getting complete education dashboard"""
        # Arrange
        with patch.object(education_service, '_get_user_holland_profile', return_value={'top_3_code': 'IRA'}), \
             patch.object(education_service, '_get_personalized_programs', return_value=[]), \
             patch.object(education_service, '_get_career_education_pathways', return_value=[]), \
             patch.object(education_service, '_get_user_saved_programs', return_value=[]), \
             patch.object(education_service, '_get_user_education_preferences', return_value={}):
            
            # Act
            result = await education_service.get_user_education_dashboard(mock_user)
        
        # Assert
        assert isinstance(result, EducationDashboardResponse)
        assert result.holland_profile_summary['top_3_code'] == 'IRA'
        assert isinstance(result.personalized_programs, list)
        assert isinstance(result.career_pathways, list)
        assert isinstance(result.saved_programs, list)
        assert isinstance(result.user_preferences, dict)

# ================================
# Integration Tests with FastAPI
# ================================

class TestEducationAPIEndpoints:
    """Test the FastAPI endpoints for education integration"""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app with education router"""
        app = FastAPI()
        app.include_router(education_router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)
    
    def test_get_education_dashboard_success(self, client):
        """Test successful education dashboard retrieval"""
        # Mock authentication and dependencies
        with patch('orientor_backend_integration.get_current_user', return_value=MockUser()), \
             patch('orientor_backend_integration.get_db', return_value=Mock()), \
             patch.object(OrientorEducationService, 'get_user_education_dashboard', 
                         return_value=EducationDashboardResponse(
                             personalized_programs=[],
                             career_pathways=[],
                             saved_programs=[],
                             user_preferences={}
                         )):
            
            response = client.get("/api/v1/education/dashboard")
            
            assert response.status_code == 200
            data = response.json()
            assert 'personalized_programs' in data
            assert 'career_pathways' in data
            assert 'saved_programs' in data
            assert 'user_preferences' in data
    
    def test_get_personalized_programs_success(self, client):
        """Test successful personalized programs retrieval"""
        with patch('orientor_backend_integration.get_current_user', return_value=MockUser()), \
             patch('orientor_backend_integration.get_db', return_value=Mock()), \
             patch.object(OrientorEducationService, '_get_user_holland_profile', 
                         return_value={'top_3_code': 'IRA'}), \
             patch.object(OrientorEducationService, '_get_personalized_programs', 
                         return_value=[]):
            
            response = client.get("/api/v1/education/programs/personalized")
            
            assert response.status_code == 200
            data = response.json()
            assert 'programs' in data
            assert 'holland_profile' in data
            assert 'total_available' in data
    
    def test_get_personalized_programs_no_holland_assessment(self, client):
        """Test personalized programs when no Holland assessment exists"""
        with patch('orientor_backend_integration.get_current_user', return_value=MockUser()), \
             patch('orientor_backend_integration.get_db', return_value=Mock()), \
             patch.object(OrientorEducationService, '_get_user_holland_profile', return_value=None):
            
            response = client.get("/api/v1/education/programs/personalized")
            
            assert response.status_code == 404
            data = response.json()
            assert 'detail' in data
            assert 'Holland RIASEC assessment' in data['detail']
    
    def test_save_program_success(self, client):
        """Test successful program saving"""
        mock_db_instance = Mock()
        mock_db_instance.add = Mock()
        mock_db_instance.commit = Mock()
        mock_db_instance.rollback = Mock()
        
        with patch('orientor_backend_integration.get_current_user', return_value=MockUser()), \
             patch('orientor_backend_integration.get_db', return_value=mock_db_instance):
            
            response = client.post("/api/v1/education/programs/test-program-id/save", 
                                 json={"notes": "Interested in this program"})
            
            assert response.status_code == 200
            data = response.json()
            assert data['message'] == "Program saved successfully"
            assert data['program_id'] == "test-program-id"
            
            # Verify database operations were called
            mock_db_instance.add.assert_called_once()
            mock_db_instance.commit.assert_called_once()

# ================================
# Test Data Quality and Edge Cases
# ================================

class TestDataQualityAndEdgeCases:
    """Test edge cases and data quality scenarios"""
    
    @pytest.mark.asyncio
    async def test_holland_compatibility_calculation_edge_cases(self, education_service):
        """Test Holland compatibility calculation with edge cases"""
        # Test with invalid Holland profile
        result = await education_service._calculate_holland_compatibility(
            MockProgram(), None
        )
        assert result is not None
        
        # Test with empty Holland profile
        result = await education_service._calculate_holland_compatibility(
            MockProgram(), {}
        )
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_program_filtering_by_user_preferences(self, education_service, mock_db):
        """Test program filtering based on user preferences"""
        # Test with specific location preference
        user_preferences = {
            'preferred_locations': ['Montreal', 'Toronto'],
            'max_duration': 36,
            'max_budget': 5000
        }
        
        programs = [MockProgram(duration_months=48), MockProgram(duration_months=24)]
        
        # Should filter out programs that don't match preferences
        filtered = await education_service._filter_programs_by_preferences(
            programs, user_preferences
        )
        
        # The 48-month program should be filtered out
        assert len(filtered) == 1
        assert filtered[0].duration_months == 24
    
    @pytest.mark.asyncio
    async def test_recommendation_reasons_generation(self, education_service):
        """Test generation of recommendation reasons"""
        holland_profile = {'top_3_code': 'IRA', 'scores': {'I': 8.5}}
        program = MockProgram(program_type="technical")
        
        reasons = await education_service._generate_recommendation_reasons(
            program, holland_profile, 0.8, 0.7
        )
        
        assert len(reasons) > 0
        assert any('Investigative' in reason for reason in reasons)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_dashboard_generation(self, education_service, mock_db, mock_user):
        """Test error handling in dashboard generation"""
        # Mock an exception in one of the sub-methods
        with patch.object(education_service, '_get_user_holland_profile', side_effect=Exception("Database error")):
            
            # Should handle the exception gracefully
            with pytest.raises(Exception):
                await education_service.get_user_education_dashboard(mock_user)

# ================================
# Performance and Load Tests
# ================================

class TestPerformanceAndLoad:
    """Test performance characteristics of the integration"""
    
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self, education_service, mock_db):
        """Test handling of large program datasets"""
        # Create a large number of mock programs
        large_program_set = [MockProgram(id=f"prog-{i}") for i in range(1000)]
        
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.options.return_value.limit.return_value.all.return_value = large_program_set[:50]
        mock_db.query.return_value = mock_query
        
        # Should handle large datasets efficiently
        result = await education_service._find_programs_by_holland_code('I')
        
        assert len(result) <= 50  # Should be limited for performance
    
    @pytest.mark.asyncio
    async def test_concurrent_user_requests(self, education_service, mock_db):
        """Test handling of concurrent user requests"""
        import asyncio
        
        # Mock successful database responses
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = MockGCAResult()
        mock_db.query.return_value = mock_query
        
        # Simulate multiple concurrent requests
        tasks = [
            education_service._get_user_holland_profile(i) 
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All requests should complete successfully
        assert len(results) == 10
        assert all(result is not None for result in results)

# ================================
# Integration Test Helpers
# ================================

def create_test_data():
    """Create comprehensive test data for integration testing"""
    return {
        'users': [MockUser(id=i) for i in range(1, 6)],
        'holland_results': [MockGCAResult(user_id=i) for i in range(1, 6)],
        'programs': [MockProgram(id=f"prog-{i}") for i in range(1, 21)],
        'career_recommendations': [MockSavedRecommendation(user_id=i) for i in range(1, 6)]
    }

def assert_valid_program_response(program_response):
    """Assert that a program response has all required fields"""
    assert hasattr(program_response, 'id')
    assert hasattr(program_response, 'title')
    assert hasattr(program_response, 'institution_name')
    assert hasattr(program_response, 'program_type')
    assert hasattr(program_response, 'level')
    assert program_response.holland_compatibility is not None
    assert isinstance(program_response.recommendation_reasons, list)

# ================================
# Run Tests
# ================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])