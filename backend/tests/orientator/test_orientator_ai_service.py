"""
Test suite for OrientatorAIService - TDD implementation
Tests cover message processing, intent analysis, tool invocation, and response generation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import json
from typing import Dict, List, Any

from app.services.orientator_ai_service import OrientatorAIService
from app.services.tool_registry import ToolRegistry, ToolResult
from app.models.user import User
from app.schemas.orientator import (
    OrientatorResponse,
    MessageComponent,
    MessageComponentType,
    ComponentAction,
    ToolInvocationResult
)


class TestOrientatorAIService:
    """Test suite for OrientatorAIService"""
    
    @pytest.fixture
    def orientator_service(self):
        """Create OrientatorAIService instance with mocked dependencies"""
        with patch('app.services.orientator_ai_service.AsyncOpenAI') as mock_openai:
            service = OrientatorAIService()
            service.llm_client = mock_openai.return_value
            return service
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session"""
        session = MagicMock()
        return session
    
    @pytest.fixture
    def test_user(self):
        """Create test user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        
        # Mock profile data
        profile = Mock()
        profile.interests = "data science, AI"
        profile.skills = ["python", "machine learning"]
        profile.education_level = "Bachelor's degree"
        user.profile = profile
        
        return user
    
    @pytest.fixture
    def mock_tool_registry(self):
        """Create mock tool registry"""
        registry = Mock(spec=ToolRegistry)
        return registry

    # Test 1: Message Intent Analysis
    @pytest.mark.asyncio
    async def test_analyze_intent_career_exploration(self, orientator_service):
        """Test intent analysis for career exploration queries"""
        message = "I want to become a data scientist"
        
        # Mock LLM response
        orientator_service.llm_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(
                        content=json.dumps({
                            "intent": "career_exploration",
                            "entities": {
                                "career_goal": "data scientist",
                                "action": "become"
                            },
                            "confidence": 0.95,
                            "suggested_tools": ["career_tree", "esco_skills"]
                        })
                    )
                )]
            )
        )
        
        intent = await orientator_service.analyze_intent(message)
        
        assert intent["intent"] == "career_exploration"
        assert intent["entities"]["career_goal"] == "data scientist"
        assert "career_tree" in intent["suggested_tools"]
        assert intent["confidence"] >= 0.9

    @pytest.mark.asyncio
    async def test_analyze_intent_skill_gap(self, orientator_service):
        """Test intent analysis for skill gap queries"""
        message = "What skills do I need for machine learning engineering?"
        
        orientator_service.llm_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(
                        content=json.dumps({
                            "intent": "skill_gap_analysis",
                            "entities": {
                                "target_role": "machine learning engineering",
                                "query_type": "skills_needed"
                            },
                            "confidence": 0.92,
                            "suggested_tools": ["esco_skills", "xp_challenges"]
                        })
                    )
                )]
            )
        )
        
        intent = await orientator_service.analyze_intent(message)
        
        assert intent["intent"] == "skill_gap_analysis"
        assert intent["entities"]["target_role"] == "machine learning engineering"
        assert "esco_skills" in intent["suggested_tools"]

    @pytest.mark.asyncio
    async def test_analyze_intent_peer_discovery(self, orientator_service):
        """Test intent analysis for peer discovery queries"""
        message = "I want to connect with other aspiring data scientists"
        
        orientator_service.llm_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(
                        content=json.dumps({
                            "intent": "peer_discovery",
                            "entities": {
                                "peer_type": "aspiring data scientists",
                                "action": "connect"
                            },
                            "confidence": 0.88,
                            "suggested_tools": ["peer_matching"]
                        })
                    )
                )]
            )
        )
        
        intent = await orientator_service.analyze_intent(message)
        
        assert intent["intent"] == "peer_discovery"
        assert "peer_matching" in intent["suggested_tools"]

    # Test 2: Tool Determination Logic
    def test_determine_tools_single_tool(self, orientator_service):
        """Test tool determination for single tool scenarios"""
        intent = {
            "intent": "career_exploration",
            "suggested_tools": ["career_tree"],
            "confidence": 0.95
        }
        
        tools = orientator_service.determine_tools(intent)
        
        assert len(tools) == 1
        assert tools[0]["tool_name"] == "career_tree"
        assert tools[0]["priority"] == "high"

    def test_determine_tools_multiple_tools(self, orientator_service):
        """Test tool determination for multiple tool scenarios"""
        intent = {
            "intent": "skill_gap_analysis",
            "suggested_tools": ["esco_skills", "xp_challenges", "career_tree"],
            "confidence": 0.90
        }
        
        tools = orientator_service.determine_tools(intent)
        
        assert len(tools) == 3
        tool_names = [t["tool_name"] for t in tools]
        assert "esco_skills" in tool_names
        assert "xp_challenges" in tool_names
        assert "career_tree" in tool_names

    def test_determine_tools_with_fallback(self, orientator_service):
        """Test tool determination with fallback for unclear intent"""
        intent = {
            "intent": "unclear",
            "suggested_tools": [],
            "confidence": 0.4
        }
        
        tools = orientator_service.determine_tools(intent)
        
        # Should suggest general exploration tools
        assert len(tools) > 0
        assert any(t["tool_name"] == "oasis_explorer" for t in tools)

    # Test 3: Tool Execution
    @pytest.mark.asyncio
    async def test_execute_tools_success(self, orientator_service, mock_tool_registry, test_user, mock_db_session):
        """Test successful tool execution"""
        tools_to_invoke = [
            {"tool_name": "esco_skills", "priority": "high", "params": {"role": "data scientist"}}
        ]
        
        # Mock tool result
        mock_result = ToolResult(
            success=True,
            data={
                "skills": [
                    {"name": "Python Programming", "level": "Advanced", "category": "Technical"},
                    {"name": "Machine Learning", "level": "Advanced", "category": "Technical"},
                    {"name": "Statistics", "level": "Intermediate", "category": "Mathematical"}
                ]
            },
            metadata={"execution_time": 0.5}
        )
        
        orientator_service.tool_registry = mock_tool_registry
        mock_tool_registry.invoke = AsyncMock(return_value=mock_result)
        
        results = await orientator_service.execute_tools(tools_to_invoke, test_user.id, mock_db_session)
        
        assert len(results) == 1
        assert results[0]["tool_name"] == "esco_skills"
        assert results[0]["result"].success
        assert len(results[0]["result"].data["skills"]) == 3

    @pytest.mark.asyncio
    async def test_execute_tools_with_failure(self, orientator_service, mock_tool_registry, test_user, mock_db_session):
        """Test tool execution with failure handling"""
        tools_to_invoke = [
            {"tool_name": "career_tree", "priority": "high", "params": {}},
            {"tool_name": "esco_skills", "priority": "medium", "params": {}}
        ]
        
        # First tool fails, second succeeds
        mock_tool_registry.invoke = AsyncMock(side_effect=[
            ToolResult(success=False, error="Career tree service unavailable"),
            ToolResult(success=True, data={"skills": []})
        ])
        
        orientator_service.tool_registry = mock_tool_registry
        
        results = await orientator_service.execute_tools(tools_to_invoke, test_user.id, mock_db_session)
        
        assert len(results) == 2
        assert not results[0]["result"].success
        assert results[0]["result"].error == "Career tree service unavailable"
        assert results[1]["result"].success

    # Test 4: Response Generation
    @pytest.mark.asyncio
    async def test_generate_response_with_components(self, orientator_service):
        """Test response generation with message components"""
        message = "Show me the path to becoming a data scientist"
        intent = {"intent": "career_exploration", "entities": {"career_goal": "data scientist"}}
        tool_results = [{
            "tool_name": "career_tree",
            "result": ToolResult(
                success=True,
                data={
                    "path": [
                        {"step": 1, "title": "Learn Python", "duration": "3 months"},
                        {"step": 2, "title": "Study Statistics", "duration": "2 months"},
                        {"step": 3, "title": "Machine Learning Basics", "duration": "4 months"}
                    ]
                }
            )
        }]
        
        orientator_service.llm_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(
                        content="I'll help you explore the path to becoming a data scientist. Here's a typical journey with key milestones:"
                    )
                )]
            )
        )
        
        response = await orientator_service.generate_response(message, intent, tool_results)
        
        assert isinstance(response, OrientatorResponse)
        assert response.content.startswith("I'll help you explore")
        assert len(response.components) == 1
        assert response.components[0].type == MessageComponentType.CAREER_PATH
        assert len(response.components[0].data["path"]) == 3
        assert response.metadata["tools_invoked"] == ["career_tree"]

    @pytest.mark.asyncio
    async def test_generate_response_no_tools(self, orientator_service):
        """Test response generation without tool invocation"""
        message = "Hello, can you help me?"
        intent = {"intent": "greeting", "entities": {}}
        tool_results = []
        
        orientator_service.llm_client.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(
                    message=Mock(
                        content="Hello! I'm Orientator, your AI career assistant. I can help you explore career paths, discover required skills, find peers, and much more. What would you like to explore today?"
                    )
                )]
            )
        )
        
        response = await orientator_service.generate_response(message, intent, tool_results)
        
        assert isinstance(response, OrientatorResponse)
        assert "Hello! I'm Orientator" in response.content
        assert len(response.components) == 0
        assert response.metadata["tools_invoked"] == []

    # Test 5: Full Message Processing Flow
    @pytest.mark.asyncio
    async def test_process_message_full_flow(self, orientator_service, test_user, mock_db_session):
        """Test complete message processing flow"""
        message = "What skills do I need to become a machine learning engineer?"
        conversation_id = 1
        
        # Mock intent analysis
        orientator_service.analyze_intent = AsyncMock(return_value={
            "intent": "skill_gap_analysis",
            "entities": {"target_role": "machine learning engineer"},
            "confidence": 0.95,
            "suggested_tools": ["esco_skills"]
        })
        
        # Mock tool determination
        orientator_service.determine_tools = Mock(return_value=[
            {"tool_name": "esco_skills", "priority": "high", "params": {"role": "machine learning engineer"}}
        ])
        
        # Mock tool execution
        orientator_service.execute_tools = AsyncMock(return_value=[{
            "tool_name": "esco_skills",
            "result": ToolResult(
                success=True,
                data={
                    "skills": [
                        {"name": "Python", "level": "Expert"},
                        {"name": "TensorFlow", "level": "Advanced"}
                    ]
                }
            )
        }])
        
        # Mock response generation
        orientator_service.generate_response = AsyncMock(return_value=OrientatorResponse(
            content="To become a machine learning engineer, you'll need these key skills:",
            components=[
                MessageComponent(
                    id="comp_1",
                    type=MessageComponentType.SKILL_TREE,
                    data={"skills": [{"name": "Python", "level": "Expert"}]},
                    actions=[
                        ComponentAction(
                            type="save",
                            label="Save to My Space",
                            endpoint="/api/orientator/save-component"
                        )
                    ],
                    metadata={"tool_source": "esco_skills"}
                )
            ],
            metadata={"tools_invoked": ["esco_skills"]}
        ))
        
        # Mock database storage
        orientator_service.store_message_with_components = AsyncMock()
        
        response = await orientator_service.process_message(
            test_user.id, message, conversation_id, mock_db_session
        )
        
        assert isinstance(response, OrientatorResponse)
        assert "machine learning engineer" in response.content
        assert len(response.components) == 1
        assert response.components[0].type == MessageComponentType.SKILL_TREE
        
        # Verify all methods were called
        orientator_service.analyze_intent.assert_called_once_with(message)
        orientator_service.determine_tools.assert_called_once()
        orientator_service.execute_tools.assert_called_once()
        orientator_service.generate_response.assert_called_once()
        orientator_service.store_message_with_components.assert_called_once()

    # Test 6: Error Handling
    @pytest.mark.asyncio
    async def test_process_message_llm_error(self, orientator_service, test_user, mock_db_session):
        """Test error handling when LLM fails"""
        message = "Help me with my career"
        conversation_id = 1
        
        # Mock LLM failure
        orientator_service.analyze_intent = AsyncMock(
            side_effect=Exception("OpenAI API error")
        )
        
        with pytest.raises(Exception) as exc_info:
            await orientator_service.process_message(
                test_user.id, message, conversation_id, mock_db_session
            )
        
        assert "OpenAI API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_message_tool_registry_error(self, orientator_service, test_user, mock_db_session):
        """Test error handling when tool registry fails"""
        message = "Show me career paths"
        conversation_id = 1
        
        orientator_service.analyze_intent = AsyncMock(return_value={
            "intent": "career_exploration",
            "suggested_tools": ["career_tree"]
        })
        
        orientator_service.determine_tools = Mock(return_value=[
            {"tool_name": "career_tree", "priority": "high"}
        ])
        
        # Mock tool execution failure
        orientator_service.execute_tools = AsyncMock(
            side_effect=ValueError("Unknown tool: career_tree")
        )
        
        with pytest.raises(ValueError) as exc_info:
            await orientator_service.process_message(
                test_user.id, message, conversation_id, mock_db_session
            )
        
        assert "Unknown tool" in str(exc_info.value)

    # Test 7: Database Storage
    @pytest.mark.asyncio
    async def test_store_message_with_components(self, orientator_service, mock_db_session):
        """Test storing message and components in database"""
        conversation_id = 1
        response = OrientatorResponse(
            content="Here are the skills you need:",
            components=[
                MessageComponent(
                    id="comp_1",
                    type=MessageComponentType.SKILL_TREE,
                    data={"skills": [{"name": "Python"}]},
                    actions=[],
                    metadata={"tool_source": "esco_skills"}
                )
            ],
            metadata={"tools_invoked": ["esco_skills"]}
        )
        
        # Mock database operations
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        await orientator_service.store_message_with_components(
            conversation_id, response, mock_db_session
        )
        
        # Verify database operations
        assert mock_db_session.add.call_count >= 1  # At least the message was added
        mock_db_session.commit.assert_called()