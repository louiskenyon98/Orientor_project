"""
Test suite for Tool Registry - TDD implementation
Tests cover tool registration, invocation, and all integrated tools
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from app.services.tool_registry import (
    ToolRegistry, 
    ToolResult, 
    BaseTool,
    ESCOSkillsTool,
    CareerTreeTool,
    OASISExplorerTool,
    PeerMatchingTool,
    HEXACOTestTool,
    HollandTestTool,
    XPChallengesTool
)
from app.models.user import User


class TestToolRegistry:
    """Test suite for Tool Registry"""
    
    @pytest.fixture
    def tool_registry(self):
        """Create Tool Registry instance"""
        return ToolRegistry()
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session"""
        session = Mock()
        return session
    
    @pytest.fixture
    def test_user(self):
        """Create test user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        
        # Mock profile data
        profile = Mock()
        profile.skills = ["python"]
        profile.interests = "AI"
        user.profile = profile
        
        return user

    # Test 1: Tool Registration
    def test_tool_registration_default_tools(self, tool_registry):
        """Test that all default tools are registered"""
        expected_tools = [
            "esco_skills",
            "career_tree",
            "oasis_explorer",
            "peer_matching",
            "hexaco_test",
            "holland_test",
            "xp_challenges"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_registry.tools
            assert isinstance(tool_registry.tools[tool_name], BaseTool)

    def test_register_custom_tool(self, tool_registry):
        """Test registering a custom tool"""
        class CustomTool(BaseTool):
            async def execute(self, params: Dict[str, Any], user_id: int, db) -> ToolResult:
                return ToolResult(success=True, data={"custom": "result"})
        
        custom_tool = CustomTool()
        tool_registry.register("custom_tool", custom_tool)
        
        assert "custom_tool" in tool_registry.tools
        assert tool_registry.tools["custom_tool"] == custom_tool

    def test_register_duplicate_tool_raises_error(self, tool_registry):
        """Test that registering duplicate tool raises error"""
        with pytest.raises(ValueError) as exc_info:
            tool_registry.register("esco_skills", Mock())
        
        assert "already registered" in str(exc_info.value)

    # Test 2: Tool Invocation
    @pytest.mark.asyncio
    async def test_invoke_existing_tool(self, tool_registry, test_user, mock_db_session):
        """Test invoking an existing tool"""
        # Mock the ESCO skills tool
        mock_tool = AsyncMock()
        mock_tool.execute.return_value = ToolResult(
            success=True,
            data={"skills": ["Python", "Machine Learning"]}
        )
        tool_registry.tools["esco_skills"] = mock_tool
        
        result = await tool_registry.invoke(
            "esco_skills",
            {"role": "data scientist"},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert "skills" in result.data
        mock_tool.execute.assert_called_once_with(
            {"role": "data scientist"},
            test_user.id,
            mock_db_session
        )

    @pytest.mark.asyncio
    async def test_invoke_unknown_tool_raises_error(self, tool_registry, test_user, mock_db_session):
        """Test invoking unknown tool raises error"""
        with pytest.raises(ValueError) as exc_info:
            await tool_registry.invoke(
                "unknown_tool",
                {},
                test_user.id,
                mock_db_session
            )
        
        assert "Unknown tool: unknown_tool" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invoke_with_error_handling(self, tool_registry, test_user, mock_db_session):
        """Test tool invocation with error handling"""
        # Mock tool that raises exception
        mock_tool = AsyncMock()
        mock_tool.execute.side_effect = Exception("Tool execution failed")
        tool_registry.tools["career_tree"] = mock_tool
        
        result = await tool_registry.invoke(
            "career_tree",
            {},
            test_user.id,
            mock_db_session
        )
        
        assert not result.success
        assert "Tool execution failed" in result.error

    # Test 3: Tool Discovery
    def test_get_available_tools(self, tool_registry):
        """Test getting list of available tools"""
        tools = tool_registry.get_available_tools()
        
        assert isinstance(tools, list)
        assert len(tools) >= 7  # At least 7 default tools
        
        # Check tool info structure
        for tool_info in tools:
            assert "name" in tool_info
            assert "description" in tool_info
            assert "category" in tool_info

    def test_get_tool_info(self, tool_registry):
        """Test getting information about specific tool"""
        info = tool_registry.get_tool_info("esco_skills")
        
        assert info["name"] == "esco_skills"
        assert "description" in info
        assert info["category"] == "skills"
        assert "required_params" in info
        assert "optional_params" in info


class TestESCOSkillsTool:
    """Test suite for ESCO Skills Tool"""
    
    @pytest.fixture
    def esco_tool(self):
        """Create ESCO Skills tool instance"""
        with patch('app.services.tools.esco_skills.ESCOIntegrationService') as mock_service:
            tool = ESCOSkillsTool()
            tool.esco_service = mock_service.return_value
            return tool
    
    @pytest.mark.asyncio
    async def test_execute_with_role(self, esco_tool, test_user, mock_db_session):
        """Test ESCO skills tool execution with role parameter"""
        # Mock ESCO service response
        esco_tool.esco_service.get_skills_for_role = AsyncMock(return_value={
            "role": "Data Scientist",
            "skills": [
                {
                    "uri": "http://data.europa.eu/esco/skill/1",
                    "name": "Python programming",
                    "skill_type": "skill/competence",
                    "reuse_level": "cross-sectoral",
                    "proficiency_level": "advanced"
                },
                {
                    "uri": "http://data.europa.eu/esco/skill/2", 
                    "name": "Machine learning",
                    "skill_type": "skill/competence",
                    "reuse_level": "occupation-specific",
                    "proficiency_level": "advanced"
                }
            ],
            "skill_hierarchy": {
                "technical": ["Python programming", "Machine learning"],
                "analytical": [],
                "soft": []
            }
        })
        
        result = await esco_tool.execute(
            {"role": "Data Scientist"},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert len(result.data["skills"]) == 2
        assert result.data["skills"][0]["name"] == "Python programming"
        assert "skill_hierarchy" in result.data
        assert result.metadata["source"] == "esco"

    @pytest.mark.asyncio
    async def test_execute_with_skills_list(self, esco_tool, test_user, mock_db_session):
        """Test ESCO skills tool with skills list parameter"""
        esco_tool.esco_service.analyze_skills = AsyncMock(return_value={
            "analyzed_skills": [
                {
                    "input_skill": "python",
                    "matched_skill": {
                        "name": "Python programming",
                        "uri": "http://data.europa.eu/esco/skill/1",
                        "broader_skills": ["Programming languages"],
                        "narrower_skills": ["Django", "Flask"]
                    }
                }
            ]
        })
        
        result = await esco_tool.execute(
            {"skills": ["python", "data analysis"]},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert "analyzed_skills" in result.data

    @pytest.mark.asyncio
    async def test_execute_missing_params(self, esco_tool, test_user, mock_db_session):
        """Test ESCO tool with missing parameters"""
        result = await esco_tool.execute(
            {},  # No parameters
            test_user.id,
            mock_db_session
        )
        
        assert not result.success
        assert "Missing required parameter" in result.error


class TestCareerTreeTool:
    """Test suite for Career Tree Tool"""
    
    @pytest.fixture
    def career_tree_tool(self):
        """Create Career Tree tool instance"""
        with patch('app.services.tools.career_tree.CareerProgressionService') as mock_service:
            tool = CareerTreeTool()
            tool.career_service = mock_service.return_value
            return tool
    
    @pytest.mark.asyncio
    async def test_execute_career_path(self, career_tree_tool, test_user, mock_db_session):
        """Test Career Tree tool execution"""
        # Mock career service response
        career_tree_tool.career_service.generate_career_path = AsyncMock(return_value={
            "career_goal": "Senior Data Scientist",
            "current_position": "Junior Developer",
            "path": [
                {
                    "step": 1,
                    "position": "Junior Developer",
                    "duration": "Current",
                    "skills_needed": ["Python", "SQL"],
                    "description": "Build foundation in programming"
                },
                {
                    "step": 2,
                    "position": "Data Analyst",
                    "duration": "1-2 years",
                    "skills_needed": ["Statistics", "Data Visualization"],
                    "description": "Transition to data-focused role"
                },
                {
                    "step": 3,
                    "position": "Data Scientist",
                    "duration": "2-3 years",
                    "skills_needed": ["Machine Learning", "Deep Learning"],
                    "description": "Develop ML expertise"
                }
            ],
            "total_duration": "3-5 years",
            "key_transitions": [
                "Developer to Analyst: Focus on data skills",
                "Analyst to Scientist: Add ML/AI capabilities"
            ]
        })
        
        result = await career_tree_tool.execute(
            {"career_goal": "Senior Data Scientist"},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert len(result.data["path"]) == 3
        assert result.data["career_goal"] == "Senior Data Scientist"
        assert "total_duration" in result.data
        assert result.metadata["tool"] == "career_tree"


class TestOASISExplorerTool:
    """Test suite for OASIS Explorer Tool"""
    
    @pytest.fixture
    def oasis_tool(self):
        """Create OASIS Explorer tool instance"""
        with patch('app.services.tools.oasis_explorer.OasisEmbeddingService') as mock_service:
            tool = OASISExplorerTool()
            tool.oasis_service = mock_service.return_value
            return tool
    
    @pytest.mark.asyncio
    async def test_execute_job_search(self, oasis_tool, test_user, mock_db_session):
        """Test OASIS tool job search"""
        # Mock OASIS service response
        oasis_tool.oasis_service.search_similar_jobs = AsyncMock(return_value={
            "query": "data scientist",
            "results": [
                {
                    "occupation_code": "2152",
                    "occupation_title": "Data Scientists",
                    "description": "Analyze complex data to help companies make decisions",
                    "match_score": 0.95,
                    "required_skills": ["Statistics", "Machine Learning", "Python"],
                    "education_level": "Bachelor's degree",
                    "experience_years": "2-4"
                },
                {
                    "occupation_code": "2120",
                    "occupation_title": "Machine Learning Engineer",
                    "description": "Build and deploy ML models",
                    "match_score": 0.87,
                    "required_skills": ["Machine Learning", "Software Engineering"],
                    "education_level": "Bachelor's degree",
                    "experience_years": "3-5"
                }
            ],
            "filters_applied": {
                "min_match_score": 0.7,
                "limit": 10
            }
        })
        
        result = await oasis_tool.execute(
            {"query": "data scientist", "limit": 10},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert len(result.data["results"]) == 2
        assert result.data["results"][0]["occupation_title"] == "Data Scientists"
        assert result.data["results"][0]["match_score"] > 0.9


class TestPeerMatchingTool:
    """Test suite for Peer Matching Tool"""
    
    @pytest.fixture
    def peer_tool(self):
        """Create Peer Matching tool instance"""
        with patch('app.services.tools.peer_matching.PeerMatchingService') as mock_service:
            tool = PeerMatchingTool()
            tool.peer_service = mock_service.return_value
            return tool
    
    @pytest.mark.asyncio
    async def test_execute_peer_search(self, peer_tool, test_user, mock_db_session):
        """Test Peer Matching tool execution"""
        # Mock peer service response
        peer_tool.peer_service.find_compatible_peers = AsyncMock(return_value={
            "user_profile": {
                "interests": ["data science", "AI"],
                "skills": ["python"],
                "goals": ["become data scientist"]
            },
            "matched_peers": [
                {
                    "user_id": 2,
                    "name": "Jane Doe",
                    "match_score": 0.85,
                    "common_interests": ["data science", "AI"],
                    "complementary_skills": ["statistics", "R"],
                    "similar_goals": ["data science career"],
                    "interaction_potential": "high"
                },
                {
                    "user_id": 3,
                    "name": "John Smith",
                    "match_score": 0.78,
                    "common_interests": ["AI"],
                    "complementary_skills": ["cloud computing"],
                    "similar_goals": ["tech career"],
                    "interaction_potential": "medium"
                }
            ],
            "matching_criteria": {
                "interests_weight": 0.3,
                "skills_weight": 0.3,
                "goals_weight": 0.4
            }
        })
        
        result = await peer_tool.execute(
            {"limit": 5, "min_match_score": 0.7},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert len(result.data["matched_peers"]) == 2
        assert result.data["matched_peers"][0]["match_score"] > 0.8
        assert "common_interests" in result.data["matched_peers"][0]


class TestPersonalityTestTools:
    """Test suite for HEXACO and Holland test tools"""
    
    @pytest.fixture
    def hexaco_tool(self):
        """Create HEXACO test tool instance"""
        with patch('app.services.tools.hexaco_test.HexacoService') as mock_service:
            tool = HEXACOTestTool()
            tool.hexaco_service = mock_service.return_value
            return tool
    
    @pytest.fixture
    def holland_tool(self):
        """Create Holland test tool instance"""
        with patch('app.services.tools.holland_test.HollandTestService') as mock_service:
            tool = HollandTestTool()
            tool.holland_service = mock_service.return_value
            return tool
    
    @pytest.mark.asyncio
    async def test_hexaco_test_initiation(self, hexaco_tool, test_user, mock_db_session):
        """Test HEXACO test initiation"""
        hexaco_tool.hexaco_service.initiate_test = AsyncMock(return_value={
            "test_id": "hexaco_123",
            "test_type": "HEXACO-60",
            "questions": [
                {
                    "id": 1,
                    "text": "I would be quite bored by a visit to an art gallery",
                    "dimension": "Openness",
                    "reversed": True
                }
            ],
            "total_questions": 60,
            "estimated_time": "10-15 minutes"
        })
        
        result = await hexaco_tool.execute(
            {"action": "start"},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert result.data["test_type"] == "HEXACO-60"
        assert "questions" in result.data
        assert result.data["total_questions"] == 60

    @pytest.mark.asyncio
    async def test_hexaco_test_completion(self, hexaco_tool, test_user, mock_db_session):
        """Test HEXACO test result processing"""
        hexaco_tool.hexaco_service.process_results = AsyncMock(return_value={
            "test_id": "hexaco_123",
            "scores": {
                "Honesty-Humility": 3.8,
                "Emotionality": 3.2,
                "Extraversion": 4.1,
                "Agreeableness": 3.5,
                "Conscientiousness": 4.3,
                "Openness": 4.5
            },
            "career_implications": {
                "strengths": ["analytical thinking", "innovation", "leadership"],
                "suitable_environments": ["research", "startups", "tech companies"],
                "recommended_roles": ["Data Scientist", "Product Manager", "Research Analyst"]
            },
            "detailed_analysis": "High openness and conscientiousness suggest..."
        })
        
        result = await hexaco_tool.execute(
            {"action": "submit", "test_id": "hexaco_123", "answers": {}},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert "scores" in result.data
        assert result.data["scores"]["Openness"] == 4.5
        assert "career_implications" in result.data

    @pytest.mark.asyncio
    async def test_holland_test_execution(self, holland_tool, test_user, mock_db_session):
        """Test Holland test execution"""
        holland_tool.holland_service.process_interests = AsyncMock(return_value={
            "holland_code": "IAS",
            "scores": {
                "Realistic": 2.1,
                "Investigative": 4.5,
                "Artistic": 3.8,
                "Social": 3.2,
                "Enterprising": 2.8,
                "Conventional": 2.3
            },
            "primary_type": "Investigative",
            "secondary_type": "Artistic",
            "tertiary_type": "Social",
            "career_matches": [
                {
                    "occupation": "Data Scientist",
                    "match_score": 0.92,
                    "description": "Perfect blend of investigation and creativity"
                },
                {
                    "occupation": "UX Researcher",
                    "match_score": 0.85,
                    "description": "Combines research with design thinking"
                }
            ]
        })
        
        result = await holland_tool.execute(
            {"interests": ["solving complex problems", "creating visualizations"]},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert result.data["holland_code"] == "IAS"
        assert result.data["primary_type"] == "Investigative"
        assert len(result.data["career_matches"]) >= 2


class TestXPChallengesTool:
    """Test suite for XP Challenges Tool"""
    
    @pytest.fixture
    def challenges_tool(self):
        """Create XP Challenges tool instance"""
        with patch('app.services.tools.xp_challenges.ChallengesService') as mock_service:
            tool = XPChallengesTool()
            tool.challenges_service = mock_service.return_value
            return tool
    
    @pytest.mark.asyncio
    async def test_get_challenges_for_skill(self, challenges_tool, test_user, mock_db_session):
        """Test getting challenges for specific skill"""
        challenges_tool.challenges_service.get_challenges = AsyncMock(return_value={
            "skill": "Python Programming",
            "user_level": "intermediate",
            "challenges": [
                {
                    "id": "ch_001",
                    "title": "Build a Web Scraper",
                    "description": "Create a Python web scraper using BeautifulSoup",
                    "difficulty": "intermediate",
                    "xp_reward": 150,
                    "estimated_time": "2-3 hours",
                    "skills_practiced": ["Python", "Web Scraping", "Data Processing"],
                    "resources": ["BeautifulSoup docs", "Tutorial link"]
                },
                {
                    "id": "ch_002",
                    "title": "Implement a REST API",
                    "description": "Build a RESTful API using FastAPI",
                    "difficulty": "intermediate",
                    "xp_reward": 200,
                    "estimated_time": "3-4 hours",
                    "skills_practiced": ["Python", "API Development", "FastAPI"],
                    "resources": ["FastAPI documentation"]
                }
            ],
            "progression_path": {
                "current_level": "intermediate",
                "next_level": "advanced",
                "xp_to_next_level": 500,
                "current_xp": 1200
            }
        })
        
        result = await challenges_tool.execute(
            {"skill": "Python Programming"},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert len(result.data["challenges"]) == 2
        assert result.data["challenges"][0]["xp_reward"] == 150
        assert "progression_path" in result.data

    @pytest.mark.asyncio
    async def test_get_challenges_for_career_goal(self, challenges_tool, test_user, mock_db_session):
        """Test getting challenges for career goal"""
        challenges_tool.challenges_service.get_career_challenges = AsyncMock(return_value={
            "career_goal": "Data Scientist",
            "challenge_tracks": [
                {
                    "track_name": "Foundation Track",
                    "description": "Build core data science skills",
                    "challenges": [
                        {
                            "id": "ds_001",
                            "title": "Exploratory Data Analysis Project",
                            "xp_reward": 300,
                            "skills": ["Pandas", "Matplotlib", "Statistics"]
                        }
                    ]
                },
                {
                    "track_name": "Machine Learning Track",
                    "description": "Master ML algorithms",
                    "challenges": [
                        {
                            "id": "ml_001",
                            "title": "Build Your First Classifier",
                            "xp_reward": 400,
                            "skills": ["Scikit-learn", "ML Basics"]
                        }
                    ]
                }
            ],
            "total_xp_available": 2500,
            "estimated_completion_time": "3-6 months"
        })
        
        result = await challenges_tool.execute(
            {"career_goal": "Data Scientist"},
            test_user.id,
            mock_db_session
        )
        
        assert result.success
        assert len(result.data["challenge_tracks"]) == 2
        assert result.data["total_xp_available"] == 2500