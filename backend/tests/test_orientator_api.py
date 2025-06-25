"""
Integration tests for Orientator AI API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

from app.main import app
from app.models.user import User
from app.models.conversation import Conversation
from app.models.chat_message import ChatMessage
from app.models.message_component import MessageComponent
from app.schemas.orientator import (
    OrientatorMessageRequest,
    OrientatorMessageResponse,
    SaveComponentRequest,
    MessageComponentType,
    ComponentActionType,
    OrientatorResponse,
    MessageComponent as MessageComponentSchema
)


class TestOrientatorAPI:
    """Test suite for Orientator AI API endpoints"""
    
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
        """Create mock user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        return user
    
    @pytest.fixture
    def mock_conversation(self):
        """Create mock conversation"""
        conv = Mock(spec=Conversation)
        conv.id = 1
        conv.user_id = 1
        conv.title = "Test Conversation"
        conv.message_count = 0
        conv.last_message_at = None
        return conv
    
    @pytest.fixture
    def mock_orientator_response(self):
        """Create mock Orientator response"""
        return OrientatorResponse(
            content="I'll help you explore data science careers.",
            components=[
                MessageComponentSchema(
                    id="comp_1",
                    type=MessageComponentType.SKILL_TREE,
                    data={
                        "skills": [
                            {"name": "Python", "level": "advanced"},
                            {"name": "Machine Learning", "level": "intermediate"}
                        ],
                        "role": "Data Scientist"
                    },
                    actions=[{
                        "type": ComponentActionType.SAVE,
                        "label": "Save Skills"
                    }],
                    metadata={
                        "tool_source": "esco_skills",
                        "generated_at": datetime.utcnow().isoformat()
                    }
                )
            ],
            metadata={
                "tools_invoked": ["esco_skills"],
                "intent": "career_exploration",
                "confidence": 0.95
            }
        )
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_send_message_success(
        self, 
        mock_get_db, 
        mock_get_current_user,
        client,
        auth_headers,
        mock_user,
        mock_conversation,
        mock_orientator_response
    ):
        """Test successful message sending to Orientator"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
        mock_db.add = Mock()
        mock_db.flush = Mock()
        mock_db.commit = Mock()
        
        # Mock Orientator service
        with patch('app.routers.orientator.orientator_service.process_message') as mock_process:
            mock_process.return_value = mock_orientator_response
            
            # Make request
            request_data = {
                "message": "I want to become a data scientist",
                "conversation_id": 1
            }
            
            response = client.post(
                "/api/orientator/message",
                json=request_data,
                headers=auth_headers
            )
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "assistant"
            assert "data science" in data["content"].lower()
            assert len(data["components"]) == 1
            assert data["components"][0]["type"] == "skill_tree"
            assert data["metadata"]["tools_invoked"] == ["esco_skills"]
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_send_message_conversation_not_found(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user
    ):
        """Test message sending with non-existent conversation"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock conversation not found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Make request
        request_data = {
            "message": "Test message",
            "conversation_id": 999
        }
        
        response = client.post(
            "/api/orientator/message",
            json=request_data,
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 404
        assert "Conversation not found" in response.json()["detail"]
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_save_component_success(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user,
        mock_conversation
    ):
        """Test successful component saving"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conversation
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        # Mock saved item
        mock_saved_item = Mock()
        mock_saved_item.id = 123
        mock_db.add.side_effect = lambda x: setattr(x, 'id', 123)
        
        # Make request
        request_data = {
            "component_id": "comp_1",
            "component_type": "skill_tree",
            "component_data": {
                "skills": ["Python", "ML"]
            },
            "source_tool": "esco_skills",
            "conversation_id": 1,
            "note": "Important skills to learn"
        }
        
        response = client.post(
            "/api/orientator/save-component",
            json=request_data,
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["saved_item_id"] == 123
        assert "successfully" in data["message"]
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_get_user_journey_success(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user
    ):
        """Test retrieving user journey"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock saved items
        mock_saved_item = Mock()
        mock_saved_item.component_type = "skill_tree"
        mock_saved_item.component_data = {
            "skills": [{"name": "Python", "level": "advanced"}]
        }
        mock_saved_item.created_at = datetime.utcnow()
        
        # Mock tool invocations
        mock_invocation = Mock()
        mock_invocation.tool_name = "esco_skills"
        
        # Mock journey milestones
        mock_milestone = Mock()
        mock_milestone.milestone_type = "career_exploration"
        mock_milestone.milestone_data = {"career": "Data Scientist"}
        mock_milestone.achieved_at = datetime.utcnow()
        mock_milestone.conversation_id = 1
        
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
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == mock_user.id
        assert data["saved_items_count"] == 1
        assert "esco_skills" in data["tools_used"]
        assert len(data["journey_stages"]) == 1
        assert "Python" in data["skill_progression"]
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_get_user_journey_unauthorized(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user
    ):
        """Test accessing another user's journey"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Make request for different user
        response = client.get(
            "/api/orientator/journey/999",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 403
        assert "Cannot access another user's journey" in response.json()["detail"]
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_get_orientator_conversations(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user
    ):
        """Test retrieving Orientator conversations"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock conversation
        mock_conv = Mock()
        mock_conv.id = 1
        mock_conv.title = "Career Exploration"
        mock_conv.created_at = datetime.utcnow()
        mock_conv.last_message_at = datetime.utcnow()
        mock_conv.message_count = 10
        mock_conv.is_favorite = False
        mock_conv.is_archived = False
        
        # Mock tool invocation
        mock_db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [
            ("esco_skills",), ("career_tree",)
        ]
        
        # Setup query chain
        query_chain = Mock()
        query_chain.filter.return_value = query_chain
        query_chain.join.return_value = query_chain
        query_chain.distinct.return_value = query_chain
        query_chain.order_by.return_value = query_chain
        query_chain.limit.return_value = query_chain
        query_chain.offset.return_value = query_chain
        query_chain.all.return_value = [mock_conv]
        mock_db.query.return_value = query_chain
        
        # Make request
        response = client.get(
            "/api/orientator/conversations?limit=10&offset=0",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["title"] == "Career Exploration"
        assert len(data[0]["tools_used"]) == 2
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_get_tool_analytics(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user
    ):
        """Test retrieving tool analytics"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock tool invocations
        mock_inv1 = Mock()
        mock_inv1.tool_name = "esco_skills"
        mock_inv1.success = "success"
        mock_inv1.execution_time_ms = 250
        
        mock_inv2 = Mock()
        mock_inv2.tool_name = "esco_skills"
        mock_inv2.success = "success"
        mock_inv2.execution_time_ms = 300
        
        mock_inv3 = Mock()
        mock_inv3.tool_name = "career_tree"
        mock_inv3.success = "failed"
        mock_inv3.execution_time_ms = None
        
        mock_db.query.return_value.filter.return_value.all.return_value = [
            mock_inv1, mock_inv2, mock_inv3
        ]
        
        # Make request
        response = client.get(
            "/api/orientator/tool-analytics",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total_invocations"] == 3
        assert data["success_rate"] == 2/3
        assert "esco_skills" in data["tool_usage"]
        assert data["tool_usage"]["esco_skills"]["count"] == 2
        assert data["tool_usage"]["esco_skills"]["success_rate"] == 1.0
        assert data["most_used_tools"][0]["tool"] == "esco_skills"
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_submit_feedback(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers,
        mock_user
    ):
        """Test submitting feedback for AI response"""
        # Setup mocks
        mock_get_current_user.return_value = mock_user
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock message
        mock_message = Mock()
        mock_message.id = 1
        mock_message.role = "assistant"
        mock_message.message_metadata = {}
        
        # Setup query chain
        query_chain = Mock()
        query_chain.join.return_value = query_chain
        query_chain.filter.return_value = query_chain
        query_chain.first.return_value = mock_message
        mock_db.query.return_value = query_chain
        
        # Make request
        response = client.post(
            "/api/orientator/feedback?message_id=1&rating=5",
            json={
                "message_id": 1,
                "feedback": "Very helpful response!",
                "rating": 5
            },
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Thank you" in data["message"]
        
        # Verify feedback was stored
        assert "user_feedback" in mock_message.message_metadata
        assert mock_message.message_metadata["user_feedback"]["rating"] == 5
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/orientator/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "orientator-ai"
        assert "version" in data


# Additional test cases for error scenarios

class TestOrientatorAPIErrors:
    """Test error handling in Orientator API"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Mock authentication headers"""
        return {"Authorization": "Bearer fake-token"}
    
    @patch('app.routers.orientator.get_current_user')
    async def test_unauthorized_request(self, mock_get_current_user, client):
        """Test request without authentication"""
        mock_get_current_user.side_effect = Exception("Unauthorized")
        
        response = client.post(
            "/api/orientator/message",
            json={"message": "Test", "conversation_id": 1}
        )
        
        assert response.status_code == 401
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    async def test_invalid_request_data(
        self,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers
    ):
        """Test request with invalid data"""
        mock_user = Mock()
        mock_user.id = 1
        mock_get_current_user.return_value = mock_user
        
        # Missing required field
        response = client.post(
            "/api/orientator/message",
            json={"message": "Test"},  # Missing conversation_id
            headers=auth_headers
        )
        
        assert response.status_code == 422
        
        # Invalid conversation_id
        response = client.post(
            "/api/orientator/message",
            json={"message": "Test", "conversation_id": -1},
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @patch('app.routers.orientator.get_current_user')
    @patch('app.routers.orientator.get_db')
    @patch('app.routers.orientator.orientator_service.process_message')
    async def test_service_error_handling(
        self,
        mock_process,
        mock_get_db,
        mock_get_current_user,
        client,
        auth_headers
    ):
        """Test handling of service errors"""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_get_current_user.return_value = mock_user
        
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_conv = Mock()
        mock_conv.id = 1
        mock_conv.user_id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_conv
        
        # Mock service error
        mock_process.side_effect = Exception("Service error")
        
        response = client.post(
            "/api/orientator/message",
            json={"message": "Test", "conversation_id": 1},
            headers=auth_headers
        )
        
        assert response.status_code == 500
        assert "Failed to process message" in response.json()["detail"]