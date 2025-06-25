"""
Integration tests for Orientator AI feature
Tests the complete flow from API request to response
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

from app.main import app
from app.schemas.orientator import (
    OrientatorResponse,
    MessageComponent,
    MessageComponentType,
    ComponentAction,
    ComponentActionType
)


class TestOrientatorIntegration:
    """Integration tests for complete Orientator AI flow"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer fake-token"}
    
    @pytest.fixture
    def mock_user(self):
        """Create mock authenticated user"""
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        
        # Mock profile
        profile = Mock()
        profile.interests = "data science, AI"
        profile.skills = ["python", "machine learning"]
        profile.education_level = "Bachelor's degree"
        profile.career_goals = "Become a data scientist"
        user.profile = profile
        
        return user
    
    @pytest.fixture
    def mock_conversation(self):
        """Create mock conversation"""
        conv = Mock()
        conv.id = 1
        conv.user_id = 1
        conv.title = "Career Exploration"
        conv.message_count = 0
        conv.last_message_at = None
        conv.created_at = datetime.utcnow()
        return conv
    
    @pytest.mark.asyncio
    async def test_career_exploration_flow(self, client, auth_headers, mock_user, mock_conversation):
        """Test complete career exploration conversation flow"""
        with patch('app.routers.orientator.get_current_user') as mock_get_user:
            with patch('app.routers.orientator.get_db') as mock_get_db:
                # Setup mocks
                mock_get_user.return_value = mock_user
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                # Mock conversation lookup
                mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
                
                # Mock Orientator service
                with patch('app.routers.orientator.orientator_service') as mock_service:
                    # Create mock response
                    mock_response = OrientatorResponse(
                        content="I'll help you explore the path to becoming a data scientist. Let me show you the typical career progression and required skills.",
                        components=[
                            MessageComponent(
                                id="comp_1",
                                type=MessageComponentType.CAREER_PATH,
                                data={
                                    "career_goal": "Data Scientist",
                                    "current_position": "Student",
                                    "path": [
                                        {
                                            "step": 1,
                                            "position": "Data Analyst Intern",
                                            "duration": "6-12 months",
                                            "skills_needed": ["Python basics", "SQL", "Excel"],
                                            "description": "Start with internships to gain practical experience"
                                        },
                                        {
                                            "step": 2,
                                            "position": "Junior Data Analyst",
                                            "duration": "1-2 years",
                                            "skills_needed": ["Statistics", "Data Visualization", "Pandas"],
                                            "description": "Build analytical skills and domain knowledge"
                                        },
                                        {
                                            "step": 3,
                                            "position": "Data Scientist",
                                            "duration": "2-3 years",
                                            "skills_needed": ["Machine Learning", "Deep Learning", "Cloud Platforms"],
                                            "description": "Transition to ML/AI focused role"
                                        }
                                    ],
                                    "total_duration": "3-5 years",
                                    "key_transitions": [
                                        "Analyst to Scientist: Focus on ML skills",
                                        "Build portfolio of projects"
                                    ]
                                },
                                actions=[
                                    ComponentAction(
                                        type=ComponentActionType.SAVE,
                                        label="Save Career Path",
                                        endpoint="/api/orientator/save-component"
                                    ),
                                    ComponentAction(
                                        type=ComponentActionType.EXPLORE,
                                        label="Explore Required Skills",
                                        endpoint="/api/skills/explore"
                                    )
                                ],
                                metadata={
                                    "tool_source": "career_tree",
                                    "generated_at": datetime.utcnow().isoformat()
                                }
                            )
                        ],
                        metadata={
                            "tools_invoked": ["career_tree"],
                            "intent": "career_exploration",
                            "confidence": 0.95,
                            "processing_time_ms": 1250
                        }
                    )
                    
                    mock_service.process_message = AsyncMock(return_value=mock_response)
                    
                    # Make API request
                    response = client.post(
                        "/api/orientator/message",
                        json={
                            "message": "I want to become a data scientist",
                            "conversation_id": 1
                        },
                        headers=auth_headers
                    )
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Check message content
                    assert "data scientist" in data["content"].lower()
                    assert data["role"] == "assistant"
                    
                    # Check components
                    assert len(data["components"]) == 1
                    component = data["components"][0]
                    assert component["type"] == "career_path"
                    assert component["data"]["career_goal"] == "Data Scientist"
                    assert len(component["data"]["path"]) == 3
                    
                    # Check metadata
                    assert data["metadata"]["tools_invoked"] == ["career_tree"]
                    assert data["metadata"]["intent"] == "career_exploration"
                    assert data["metadata"]["confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_skill_gap_analysis_flow(self, client, auth_headers, mock_user, mock_conversation):
        """Test skill gap analysis conversation flow"""
        with patch('app.routers.orientator.get_current_user') as mock_get_user:
            with patch('app.routers.orientator.get_db') as mock_get_db:
                # Setup mocks
                mock_get_user.return_value = mock_user
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                # Mock conversation lookup
                mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
                
                # Mock Orientator service
                with patch('app.routers.orientator.orientator_service') as mock_service:
                    # Create mock response
                    mock_response = OrientatorResponse(
                        content="Based on your current skills and the requirements for a Machine Learning Engineer role, here's a detailed skill analysis:",
                        components=[
                            MessageComponent(
                                id="comp_1",
                                type=MessageComponentType.SKILL_TREE,
                                data={
                                    "role": "Machine Learning Engineer",
                                    "skills": [
                                        {
                                            "name": "Python Programming",
                                            "level": "Expert",
                                            "category": "Technical",
                                            "current_level": "Intermediate",
                                            "gap": "Advanced",
                                            "priority": "High"
                                        },
                                        {
                                            "name": "TensorFlow/PyTorch",
                                            "level": "Advanced",
                                            "category": "Technical",
                                            "current_level": "None",
                                            "gap": "Advanced",
                                            "priority": "High"
                                        },
                                        {
                                            "name": "MLOps",
                                            "level": "Intermediate",
                                            "category": "Technical",
                                            "current_level": "None",
                                            "gap": "Intermediate",
                                            "priority": "Medium"
                                        }
                                    ],
                                    "skill_hierarchy": {
                                        "technical": ["Python Programming", "TensorFlow/PyTorch", "MLOps"],
                                        "mathematical": ["Linear Algebra", "Statistics"],
                                        "soft": ["Communication", "Problem Solving"]
                                    },
                                    "recommendations": [
                                        "Focus on deep learning frameworks",
                                        "Build ML projects for portfolio",
                                        "Learn deployment and MLOps"
                                    ]
                                },
                                actions=[
                                    ComponentAction(
                                        type=ComponentActionType.SAVE,
                                        label="Save Skill Analysis",
                                        endpoint="/api/orientator/save-component"
                                    )
                                ],
                                metadata={
                                    "tool_source": "esco_skills",
                                    "generated_at": datetime.utcnow().isoformat()
                                }
                            )
                        ],
                        metadata={
                            "tools_invoked": ["esco_skills"],
                            "intent": "skill_gap_analysis",
                            "confidence": 0.92
                        }
                    )
                    
                    mock_service.process_message = AsyncMock(return_value=mock_response)
                    
                    # Make API request
                    response = client.post(
                        "/api/orientator/message",
                        json={
                            "message": "What skills do I need to become a machine learning engineer?",
                            "conversation_id": 1
                        },
                        headers=auth_headers
                    )
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Check content
                    assert "skill" in data["content"].lower()
                    assert "machine learning engineer" in data["content"].lower()
                    
                    # Check skill component
                    assert len(data["components"]) == 1
                    component = data["components"][0]
                    assert component["type"] == "skill_tree"
                    assert len(component["data"]["skills"]) >= 3
                    assert "skill_hierarchy" in component["data"]
    
    @pytest.mark.asyncio
    async def test_save_component_flow(self, client, auth_headers, mock_user, mock_conversation):
        """Test saving a component from chat"""
        with patch('app.routers.orientator.get_current_user') as mock_get_user:
            with patch('app.routers.orientator.get_db') as mock_get_db:
                # Setup mocks
                mock_get_user.return_value = mock_user
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                # Mock conversation lookup
                mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
                
                # Mock database operations
                mock_db.add = Mock()
                mock_db.commit = Mock()
                mock_db.refresh = Mock()
                
                # Make save request
                response = client.post(
                    "/api/orientator/save-component",
                    json={
                        "component_id": "comp_1",
                        "component_type": "skill_tree",
                        "component_data": {
                            "skills": ["Python", "Machine Learning", "Statistics"],
                            "role": "Data Scientist"
                        },
                        "source_tool": "esco_skills",
                        "conversation_id": 1,
                        "note": "Key skills to focus on"
                    },
                    headers=auth_headers
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.json()
                assert data["success"] == True
                assert "saved_item_id" in data
                assert "successfully" in data["message"]
                
                # Verify database operations were called
                assert mock_db.add.called
                assert mock_db.commit.called
    
    @pytest.mark.asyncio
    async def test_user_journey_aggregation(self, client, auth_headers, mock_user):
        """Test retrieving aggregated user journey"""
        with patch('app.routers.orientator.get_current_user') as mock_get_user:
            with patch('app.routers.orientator.get_db') as mock_get_db:
                # Setup mocks
                mock_get_user.return_value = mock_user
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                # Mock saved items
                mock_saved_item = Mock()
                mock_saved_item.component_type = "skill_tree"
                mock_saved_item.component_data = {
                    "skills": [{"name": "Python", "level": "advanced"}],
                    "role": "Data Scientist"
                }
                mock_saved_item.created_at = datetime.utcnow()
                mock_saved_item.source_tool = "esco_skills"
                
                # Mock tool invocations
                mock_invocation = Mock()
                mock_invocation.tool_name = "esco_skills"
                mock_invocation.success = "success"
                mock_invocation.created_at = datetime.utcnow()
                
                # Mock milestones
                mock_milestone = Mock()
                mock_milestone.milestone_type = "career_goal_set"
                mock_milestone.milestone_data = {"goal": "Data Scientist"}
                mock_milestone.achieved_at = datetime.utcnow()
                mock_milestone.title = "Set Career Goal"
                mock_milestone.category = "career"
                
                # Setup query returns
                mock_db.query.return_value.filter.return_value.all.side_effect = [
                    [mock_saved_item],  # saved items
                    [mock_invocation],  # tool invocations
                    [mock_milestone]    # milestones
                ]
                
                # Make request
                response = client.get(
                    f"/api/orientator/journey/{mock_user.id}",
                    headers=auth_headers
                )
                
                # Verify response
                assert response.status_code == 200
                data = response.json()
                
                assert data["user_id"] == mock_user.id
                assert data["saved_items_count"] == 1
                assert "esco_skills" in data["tools_used"]
                assert len(data["journey_stages"]) == 1
                assert "Data Scientist" in str(data["career_goals"])
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_conversation(self, client, auth_headers, mock_user):
        """Test error handling for invalid conversation"""
        with patch('app.routers.orientator.get_current_user') as mock_get_user:
            with patch('app.routers.orientator.get_db') as mock_get_db:
                # Setup mocks
                mock_get_user.return_value = mock_user
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                # Mock conversation not found
                mock_db.query.return_value.filter.return_value.first.return_value = None
                
                # Make request
                response = client.post(
                    "/api/orientator/message",
                    json={
                        "message": "Test message",
                        "conversation_id": 999
                    },
                    headers=auth_headers
                )
                
                # Verify error response
                assert response.status_code == 404
                assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_multi_tool_invocation_flow(self, client, auth_headers, mock_user, mock_conversation):
        """Test conversation with multiple tool invocations"""
        with patch('app.routers.orientator.get_current_user') as mock_get_user:
            with patch('app.routers.orientator.get_db') as mock_get_db:
                # Setup mocks
                mock_get_user.return_value = mock_user
                mock_db = Mock()
                mock_get_db.return_value = mock_db
                
                # Mock conversation lookup
                mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
                
                # Mock Orientator service with multiple components
                with patch('app.routers.orientator.orientator_service') as mock_service:
                    # Create mock response with multiple components
                    mock_response = OrientatorResponse(
                        content="I've analyzed your career goals and found relevant information. Here's a comprehensive overview including career paths, required skills, and similar job opportunities:",
                        components=[
                            MessageComponent(
                                id="comp_1",
                                type=MessageComponentType.CAREER_PATH,
                                data={
                                    "career_goal": "Data Scientist",
                                    "path": [
                                        {"step": 1, "position": "Data Analyst", "duration": "1-2 years"}
                                    ]
                                },
                                actions=[],
                                metadata={"tool_source": "career_tree"}
                            ),
                            MessageComponent(
                                id="comp_2",
                                type=MessageComponentType.SKILL_TREE,
                                data={
                                    "skills": [
                                        {"name": "Python", "level": "Advanced"}
                                    ]
                                },
                                actions=[],
                                metadata={"tool_source": "esco_skills"}
                            ),
                            MessageComponent(
                                id="comp_3",
                                type=MessageComponentType.JOB_CARD,
                                data={
                                    "job_title": "Data Scientist",
                                    "match_score": 0.92,
                                    "description": "Analyze complex data to help companies make decisions"
                                },
                                actions=[],
                                metadata={"tool_source": "oasis_explorer"}
                            )
                        ],
                        metadata={
                            "tools_invoked": ["career_tree", "esco_skills", "oasis_explorer"],
                            "intent": "comprehensive_career_exploration",
                            "confidence": 0.88
                        }
                    )
                    
                    mock_service.process_message = AsyncMock(return_value=mock_response)
                    
                    # Make API request
                    response = client.post(
                        "/api/orientator/message",
                        json={
                            "message": "Tell me everything about becoming a data scientist - career path, skills, and job opportunities",
                            "conversation_id": 1
                        },
                        headers=auth_headers
                    )
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Check multiple components
                    assert len(data["components"]) == 3
                    
                    # Verify component types
                    component_types = [c["type"] for c in data["components"]]
                    assert "career_path" in component_types
                    assert "skill_tree" in component_types
                    assert "job_card" in component_types
                    
                    # Check metadata
                    assert len(data["metadata"]["tools_invoked"]) == 3
                    assert "career_tree" in data["metadata"]["tools_invoked"]
                    assert "esco_skills" in data["metadata"]["tools_invoked"]
                    assert "oasis_explorer" in data["metadata"]["tools_invoked"]