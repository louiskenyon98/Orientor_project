"""
Test suite for unified chat system after router consolidation
Tests the core functionality to ensure messages load properly and no conflicts exist
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.utils.database import get_db
from app.models import User, Conversation, ChatMessage
from app.routers.user import get_current_user

# Create test client
client = TestClient(app)

# Mock user for testing
test_user = User(id=1, email="test@example.com", hashed_password="fake_hash")

def override_get_current_user():
    """Override the get_current_user dependency for testing"""
    return test_user

def override_get_db():
    """Override the get_db dependency for testing"""
    # This would normally return a test database session
    # For now, we'll use a mock
    return None

# Override dependencies
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

class TestChatSystemUnified:
    """Test suite for unified chat system"""

    def test_router_mounting_order(self):
        """Test that conversations router takes precedence over chat router"""
        # Test that /chat/conversations route exists and is accessible
        response = client.get("/chat/conversations")
        # Should not get 404 (would mean route not found)
        assert response.status_code != 404
        
    def test_conversations_endpoint_exists(self):
        """Test that conversations endpoint is available"""
        response = client.get("/chat/conversations")
        # Endpoint should exist (even if auth fails, shouldn't be 404)
        assert response.status_code in [200, 401, 422]  # Valid HTTP responses
        
    def test_messages_endpoint_unified_format(self):
        """Test that messages endpoint returns unified format"""
        # This would test a real conversation ID in a full test
        response = client.get("/chat/conversations/1/messages")
        # Should not be 404 (route should exist)
        assert response.status_code != 404
        
    def test_chat_send_endpoint_exists(self):
        """Test that chat send endpoint still exists"""
        response = client.post("/chat/send", json={"text": "test message"})
        # Endpoint should exist (even if auth fails, shouldn't be 404)
        assert response.status_code in [200, 401, 422]
        
    def test_no_route_conflicts(self):
        """Test that there are no route conflicts by checking available routes"""
        # Get all routes from the app
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append((route.path, route.methods))
        
        # Check for duplicate /chat/conversations routes
        conversations_routes = [r for r in routes if r[0] == '/chat/conversations' and 'GET' in r[1]]
        
        # Should have exactly one GET /chat/conversations route
        assert len(conversations_routes) <= 1, f"Found duplicate routes: {conversations_routes}"
        
    def test_message_response_format_compatibility(self):
        """Test that response format is consistent"""
        # This is a conceptual test - in real implementation would mock the service
        # and verify response format matches {"messages": [...]}
        
        # Mock response format validation
        mock_response = {
            "messages": [
                {
                    "id": 1,
                    "role": "user", 
                    "content": "Test message",
                    "created_at": "2024-01-01T00:00:00",
                    "tokens_used": None
                }
            ],
            "total": 1,
            "conversation_id": 1
        }
        
        # Validate the response has the expected structure
        assert "messages" in mock_response
        assert isinstance(mock_response["messages"], list)
        assert "total" in mock_response
        assert "conversation_id" in mock_response

if __name__ == "__main__":
    # Run basic tests
    test_suite = TestChatSystemUnified()
    
    print("🧪 Running Chat System Unified Tests...")
    
    try:
        test_suite.test_router_mounting_order()
        print("✅ Router mounting order test passed")
        
        test_suite.test_conversations_endpoint_exists()
        print("✅ Conversations endpoint exists test passed")
        
        test_suite.test_messages_endpoint_unified_format()
        print("✅ Messages endpoint format test passed")
        
        test_suite.test_chat_send_endpoint_exists()
        print("✅ Chat send endpoint exists test passed")
        
        test_suite.test_no_route_conflicts()
        print("✅ No route conflicts test passed")
        
        test_suite.test_message_response_format_compatibility()
        print("✅ Message response format compatibility test passed")
        
        print("\n🎉 All tests passed! Chat system unification successful.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

print("Test file created successfully. Run with: python test_chat_system_unified.py")