import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.utils.database import Base, get_db
from app.models.user import User
from app.models.course import Course, PsychologicalInsight, CareerSignal, ConversationLog

# Test database URL - use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_course(db_session, test_user):
    """Create test course."""
    course = Course(
        user_id=test_user.id,
        course_name="Introduction to Data Science",
        course_code="CS 101",
        semester="Fall",
        year=2024,
        professor="Dr. Sarah Chen",
        subject_category="STEM",
        grade="A-",
        credits=3,
        description="An introductory course covering fundamental concepts in data science."
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course

@pytest.fixture
def test_insight(db_session, test_user, test_course):
    """Create test psychological insight."""
    insight = PsychologicalInsight(
        user_id=test_user.id,
        course_id=test_course.id,
        insight_type="cognitive_preference",
        insight_value={"preference": "analytical_thinking", "strength": 0.8},
        confidence_score=0.85,
        evidence_source="Strong performance in quantitative analysis assignments"
    )
    db_session.add(insight)
    db_session.commit()
    db_session.refresh(insight)
    return insight

@pytest.fixture
def test_career_signal(db_session, test_user, test_course):
    """Create test career signal."""
    signal = CareerSignal(
        user_id=test_user.id,
        course_id=test_course.id,
        signal_type="analytical_thinking",
        strength_score=0.8,
        evidence_source="Excellent performance in data analysis projects"
    )
    db_session.add(signal)
    db_session.commit()
    db_session.refresh(signal)
    return signal

@pytest.fixture
def test_conversation_log(db_session, test_user, test_course):
    """Create test conversation log."""
    log = ConversationLog(
        user_id=test_user.id,
        course_id=test_course.id,
        session_id="test_session_123",
        question_intent="cognitive_preference",
        question_text="What aspects of data analysis did you find most engaging?",
        response="I really enjoyed the logical problem-solving approach and seeing patterns in data.",
        extracted_insights=[
            {
                "type": "cognitive_preference",
                "value": {"analytical_thinking": 0.8},
                "confidence": 0.85
            }
        ]
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log

# Mock data for testing
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": """
                    [
                        {
                            "id": "q1",
                            "question": "What aspects of this course did you find most engaging?",
                            "intent": "subject_affinity",
                            "follow_up_triggers": ["engaging", "interesting", "enjoyed"]
                        }
                    ]
                    """
                }
            }
        ]
    }

@pytest.fixture
def mock_analysis_response():
    """Mock analysis response."""
    return {
        "insights": [
            {
                "type": "cognitive_preference",
                "value": {"analytical_thinking": 0.8},
                "confidence": 0.85,
                "evidence": "Strong preference for logical problem-solving"
            }
        ],
        "career_signals": [
            {
                "type": "analytical_thinking",
                "strength": 0.8,
                "evidence": "Demonstrated analytical capabilities",
                "metadata": {"source": "course_analysis"}
            }
        ],
        "sentiment": {
            "engagement_level": 0.9,
            "authenticity": 0.8,
            "emotional_indicators": ["enthusiasm", "confidence"]
        },
        "next_questions": [
            {
                "question": "Can you describe your problem-solving approach in more detail?",
                "intent": "cognitive_preference",
                "priority": "high"
            }
        ],
        "session_complete": False,
        "career_implications": {
            "immediate_insights": ["Strong analytical thinking preference"],
            "esco_connections": ["analytical skills", "data analysis"],
            "recommended_exploration": ["data science", "business analysis"]
        }
    }