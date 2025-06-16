import pytest
from unittest.mock import Mock, patch
import json
from app.services.llm_course_service import LLMCourseService

class TestLLMCourseServiceSimple:
    """Simplified test suite for LLMCourseService."""

    @pytest.fixture
    def llm_service(self):
        """Create LLM service instance."""
        return LLMCourseService()

    @pytest.fixture
    def sample_context(self):
        """Sample analysis context."""
        return {
            "course": {
                "name": "Data Science",
                "category": "STEM",
                "grade": "A-",
                "description": "Introduction to data science"
            },
            "user_history": {
                "total_courses": 1,
                "subject_distribution": {"STEM": 1}
            },
            "focus_areas": ["cognitive_preference", "work_style"]
        }

    def test_build_question_prompt(self, llm_service, sample_context):
        """Test question generation prompt building."""
        prompt = llm_service._build_question_prompt(sample_context, ["cognitive_preference"])
        
        assert "cognitive_preference" in prompt
        assert sample_context["course"]["name"] in prompt
        assert sample_context["course"]["category"] in prompt
        assert "JSON format" in prompt

    def test_build_analysis_prompt(self, llm_service):
        """Test analysis prompt building."""
        conversation_context = [
            {
                "question": "What did you enjoy?",
                "response": "I enjoyed the problem-solving",
                "intent": "subject_affinity"
            }
        ]
        
        prompt = llm_service._build_analysis_prompt(conversation_context, ["subject_affinity"])
        
        assert "What did you enjoy?" in prompt
        assert "I enjoyed the problem-solving" in prompt
        assert "subject_affinity" in prompt
        assert "JSON format" in prompt

    def test_parse_llm_response_valid_json(self, llm_service):
        """Test parsing valid JSON response."""
        response_content = json.dumps({
            "insights": [{"type": "test", "value": {}, "confidence": 0.8}],
            "career_signals": []
        })
        
        result = llm_service._parse_llm_response(response_content, "questions")
        
        assert result["insights"][0]["type"] == "test"
        assert result["insights"][0]["confidence"] == 0.8

    def test_parse_llm_response_invalid_json(self, llm_service):
        """Test parsing invalid JSON response."""
        response_content = "Invalid JSON"
        
        result = llm_service._parse_llm_response(response_content, "questions")
        
        # Should return fallback structure
        assert isinstance(result, list)  # For questions
        assert len(result) >= 1

    def test_parse_llm_response_analysis_fallback(self, llm_service):
        """Test parsing with analysis fallback."""
        response_content = "Invalid JSON"
        
        result = llm_service._parse_llm_response(response_content, "analysis")
        
        # Should return fallback analysis structure
        assert "insights" in result
        assert "career_signals" in result
        assert "sentiment" in result
        assert "next_questions" in result

    def test_create_fallback_questions(self, llm_service):
        """Test fallback question creation."""
        questions = llm_service._create_fallback_questions(["cognitive_preference", "work_style"])
        
        assert len(questions) >= 2
        assert any(q["intent"] == "cognitive_preference" for q in questions)
        assert any(q["intent"] == "work_style" for q in questions)
        
        for question in questions:
            assert "id" in question
            assert "question" in question
            assert "intent" in question
            assert "follow_up_triggers" in question

    def test_create_fallback_analysis(self, llm_service):
        """Test fallback analysis creation."""
        conversation_context = [
            {
                "question": "What did you enjoy?",
                "response": "I enjoyed problem-solving",
                "intent": "cognitive_preference"
            }
        ]
        
        analysis = llm_service._create_fallback_analysis(conversation_context)
        
        assert "insights" in analysis
        assert "career_signals" in analysis
        assert "sentiment" in analysis
        assert "next_questions" in analysis
        assert "session_complete" in analysis
        
        # Should extract basic insights from responses
        assert len(analysis["insights"]) >= 1
        assert analysis["insights"][0]["type"] == "cognitive_preference"

    def test_extract_basic_insights(self, llm_service):
        """Test basic insight extraction from responses."""
        conversation_context = [
            {
                "question": "What aspects did you enjoy?",
                "response": "I really enjoyed the analytical thinking and creative problem-solving aspects",
                "intent": "cognitive_preference"
            },
            {
                "question": "How do you prefer to work?",
                "response": "I prefer working independently on complex challenges",
                "intent": "work_style"
            }
        ]
        
        insights = llm_service._extract_basic_insights(conversation_context)
        
        assert len(insights) == 2
        assert insights[0]["type"] == "cognitive_preference"
        assert insights[1]["type"] == "work_style"
        
        # Check that keywords are detected
        cognitive_insight = insights[0]
        assert "analytical" in cognitive_insight["evidence"].lower() or "creative" in cognitive_insight["evidence"].lower()
        
        work_insight = insights[1]
        assert "independent" in work_insight["evidence"].lower()

    def test_detect_sentiment_indicators(self, llm_service):
        """Test sentiment indicator detection."""
        response_positive = "I absolutely loved this course! It was amazing and engaging."
        response_negative = "This was really difficult and frustrating. I didn't enjoy it."
        response_neutral = "The course covered data analysis methods."
        
        sentiment_positive = llm_service._detect_sentiment_indicators(response_positive)
        assert sentiment_positive["engagement_level"] > 0.7
        assert sentiment_positive["authenticity"] > 0.6
        assert any(indicator in ["enthusiasm", "excitement"] for indicator in sentiment_positive["emotional_indicators"])
        
        sentiment_negative = llm_service._detect_sentiment_indicators(response_negative)
        assert sentiment_negative["engagement_level"] < 0.5
        
        sentiment_neutral = llm_service._detect_sentiment_indicators(response_neutral)
        assert 0.4 <= sentiment_neutral["engagement_level"] <= 0.6

    def test_generate_followup_questions(self, llm_service):
        """Test follow-up question generation."""
        conversation_context = [
            {
                "question": "What did you enjoy?",
                "response": "I enjoyed the analytical aspects",
                "intent": "cognitive_preference"
            }
        ]
        
        questions = llm_service._generate_followup_questions(conversation_context, ["cognitive_preference"])
        
        assert len(questions) >= 1
        assert all("question" in q and "intent" in q for q in questions)
        
        # Should generate relevant follow-up based on previous responses
        question_text = questions[0]["question"].lower()
        assert any(keyword in question_text for keyword in ["analytical", "thinking", "approach", "problem"])

    def test_should_end_session(self, llm_service):
        """Test session completion detection."""
        # Short conversation - should not end
        short_context = [
            {"question": "Q1", "response": "R1", "intent": "cognitive_preference"}
        ]
        assert not llm_service._should_end_session(short_context, ["cognitive_preference"])
        
        # Long conversation with covered areas - should end
        long_context = [
            {"question": "Q1", "response": "R1", "intent": "cognitive_preference"},
            {"question": "Q2", "response": "R2", "intent": "work_style"},
            {"question": "Q3", "response": "R3", "intent": "subject_affinity"},
            {"question": "Q4", "response": "R4", "intent": "cognitive_preference"},
            {"question": "Q5", "response": "R5", "intent": "work_style"}
        ]
        assert llm_service._should_end_session(long_context, ["cognitive_preference", "work_style"])
        
        # Medium conversation with uncovered areas - should not end
        medium_context = [
            {"question": "Q1", "response": "R1", "intent": "cognitive_preference"},
            {"question": "Q2", "response": "R2", "intent": "cognitive_preference"}
        ]
        assert not llm_service._should_end_session(medium_context, ["cognitive_preference", "work_style", "subject_affinity"])

    async def test_generate_targeted_questions_with_mock(self, llm_service, sample_context):
        """Test targeted question generation with mocked OpenAI."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "id": "q1",
                "question": "What aspects of data science did you find most engaging?",
                "intent": "subject_affinity",
                "follow_up_triggers": ["engaging", "interesting", "enjoyed"]
            }
        ])
        
        with patch('app.services.llm_course_service.openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            
            questions = await llm_service.generate_targeted_questions(sample_context, ["cognitive_preference"])
            
            assert len(questions) == 1
            assert questions[0]["id"] == "q1"
            assert questions[0]["intent"] == "subject_affinity"

    async def test_analyze_response_with_mock(self, llm_service):
        """Test response analysis with mocked OpenAI."""
        conversation_context = [
            {
                "question": "What aspects did you enjoy?",
                "response": "I loved the analytical problem-solving aspects",
                "intent": "subject_affinity"
            }
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = json.dumps({
            "insights": [
                {
                    "type": "cognitive_preference",
                    "value": {"analytical_thinking": 0.8},
                    "confidence": 0.85,
                    "evidence": "Strong preference for analytical problem-solving"
                }
            ],
            "career_signals": [
                {
                    "type": "analytical_thinking",
                    "strength": 0.8,
                    "evidence": "Demonstrated analytical capabilities"
                }
            ],
            "sentiment": {
                "engagement_level": 0.9,
                "authenticity": 0.8,
                "emotional_indicators": ["enthusiasm", "confidence"]
            },
            "next_questions": [
                {
                    "question": "Can you describe your approach in more detail?",
                    "intent": "cognitive_preference",
                    "priority": "high"
                }
            ],
            "session_complete": False
        })
        
        with patch('app.services.llm_course_service.openai_client') as mock_client:
            mock_client.chat.completions.create.return_value = mock_response
            
            analysis = await llm_service.analyze_response(conversation_context, ["cognitive_preference"])
            
            assert "insights" in analysis
            assert "career_signals" in analysis
            assert "sentiment" in analysis
            assert "next_questions" in analysis
            assert len(analysis["insights"]) == 1
            assert analysis["insights"][0]["type"] == "cognitive_preference"