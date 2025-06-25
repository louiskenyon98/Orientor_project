import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models import (
    User, Conversation, ChatMessage, SavedRecommendation,
    MessageComponent, ToolInvocation, UserJourneyMilestone
)


class TestMessageComponent:
    """Test MessageComponent model."""
    
    def test_create_message_component(self, db_session, test_user):
        """Test creating a message component."""
        # Create conversation and message
        conversation = Conversation(
            user_id=test_user.id,
            title="Test Conversation"
        )
        db_session.add(conversation)
        db_session.commit()
        
        message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content="Here's a career path for you:"
        )
        db_session.add(message)
        db_session.commit()
        
        # Create message component
        component = MessageComponent(
            message_id=message.id,
            component_type="career_path",
            component_data={
                "title": "Data Scientist Career Path",
                "steps": [
                    {"title": "Learn Python", "duration": "3 months"},
                    {"title": "Study Statistics", "duration": "2 months"}
                ]
            },
            tool_source="career_tree",
            actions=[
                {"type": "save", "label": "Save Path"},
                {"type": "explore", "label": "Explore Skills"}
            ],
            metadata={"generated_at": datetime.utcnow().isoformat()}
        )
        db_session.add(component)
        db_session.commit()
        db_session.refresh(component)
        
        assert component.id is not None
        assert component.component_type == "career_path"
        assert component.tool_source == "career_tree"
        assert len(component.actions) == 2
        assert component.message.content == "Here's a career path for you:"
    
    def test_component_to_dict(self, db_session, test_user):
        """Test converting component to dictionary."""
        # Create required objects
        conversation = Conversation(user_id=test_user.id, title="Test")
        db_session.add(conversation)
        db_session.commit()
        
        message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content="Test content"
        )
        db_session.add(message)
        db_session.commit()
        
        component = MessageComponent(
            message_id=message.id,
            component_type="skill_tree",
            component_data={"skills": ["Python", "SQL"]},
            saved=True
        )
        db_session.add(component)
        db_session.commit()
        
        component_dict = component.to_dict()
        assert component_dict["component_type"] == "skill_tree"
        assert component_dict["saved"] is True
        assert "skills" in component_dict["component_data"]
    
    def test_cascade_delete(self, db_session, test_user):
        """Test that components are deleted when message is deleted."""
        # Create conversation, message, and component
        conversation = Conversation(user_id=test_user.id, title="Test")
        db_session.add(conversation)
        db_session.commit()
        
        message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content="Test"
        )
        db_session.add(message)
        db_session.commit()
        
        component = MessageComponent(
            message_id=message.id,
            component_type="test",
            component_data={}
        )
        db_session.add(component)
        db_session.commit()
        
        # Delete message
        db_session.delete(message)
        db_session.commit()
        
        # Component should be deleted
        assert db_session.query(MessageComponent).filter_by(id=component.id).first() is None


class TestToolInvocation:
    """Test ToolInvocation model."""
    
    def test_create_tool_invocation(self, db_session, test_user):
        """Test creating a tool invocation."""
        conversation = Conversation(
            user_id=test_user.id,
            title="Career Exploration"
        )
        db_session.add(conversation)
        db_session.commit()
        
        invocation = ToolInvocation(
            conversation_id=conversation.id,
            tool_name="esco_skills",
            input_params={"job_title": "data scientist"},
            output_data={
                "skills": ["Python", "Machine Learning", "Statistics"],
                "proficiency_levels": {"Python": "Expert", "Machine Learning": "Advanced"}
            },
            execution_time_ms=1250,
            success="success",
            relevance_score=0.95,
            user_id=test_user.id
        )
        db_session.add(invocation)
        db_session.commit()
        db_session.refresh(invocation)
        
        assert invocation.id is not None
        assert invocation.tool_name == "esco_skills"
        assert invocation.execution_time_ms == 1250
        assert invocation.success == "success"
        assert invocation.relevance_score == 0.95
        assert "skills" in invocation.output_data
    
    def test_failed_invocation(self, db_session, test_user):
        """Test recording a failed tool invocation."""
        conversation = Conversation(user_id=test_user.id, title="Test")
        db_session.add(conversation)
        db_session.commit()
        
        invocation = ToolInvocation(
            conversation_id=conversation.id,
            tool_name="peer_matching",
            input_params={"criteria": "similar_interests"},
            success="failed",
            error_message="Database connection timeout",
            execution_time_ms=30000,
            user_id=test_user.id
        )
        db_session.add(invocation)
        db_session.commit()
        
        assert invocation.success == "failed"
        assert invocation.error_message == "Database connection timeout"
        assert invocation.output_data is None
    
    def test_invocation_to_dict(self, db_session, test_user):
        """Test converting invocation to dictionary."""
        conversation = Conversation(user_id=test_user.id, title="Test")
        db_session.add(conversation)
        db_session.commit()
        
        invocation = ToolInvocation(
            conversation_id=conversation.id,
            tool_name="career_tree",
            input_params={"goal": "software engineer"},
            output_data={"path": ["junior", "mid", "senior"]},
            execution_time_ms=800,
            user_id=test_user.id
        )
        db_session.add(invocation)
        db_session.commit()
        
        invocation_dict = invocation.to_dict()
        assert invocation_dict["tool_name"] == "career_tree"
        assert invocation_dict["execution_time_ms"] == 800
        assert "path" in invocation_dict["output_data"]


class TestUserJourneyMilestone:
    """Test UserJourneyMilestone model."""
    
    def test_create_milestone(self, db_session, test_user):
        """Test creating a user journey milestone."""
        conversation = Conversation(user_id=test_user.id, title="Career Planning")
        db_session.add(conversation)
        db_session.commit()
        
        milestone = UserJourneyMilestone(
            user_id=test_user.id,
            milestone_type="career_goal_set",
            milestone_data={
                "goal": "Become a Data Scientist",
                "target_date": "2025-12-31",
                "required_skills": ["Python", "Statistics", "Machine Learning"]
            },
            title="Set Career Goal: Data Scientist",
            description="User has committed to pursuing a career as a Data Scientist",
            category="career",
            progress_percentage=0.0,
            status="active",
            source_type="conversation",
            source_id=conversation.id,
            conversation_id=conversation.id,
            ai_insights={
                "difficulty": "intermediate",
                "time_estimate": "18-24 months",
                "success_factors": ["Strong math background", "Programming experience"]
            },
            next_steps=["Learn Python basics", "Take statistics course", "Build portfolio"]
        )
        db_session.add(milestone)
        db_session.commit()
        db_session.refresh(milestone)
        
        assert milestone.id is not None
        assert milestone.milestone_type == "career_goal_set"
        assert milestone.category == "career"
        assert milestone.status == "active"
        assert len(milestone.next_steps) == 3
        assert milestone.progress_percentage == 0.0
    
    def test_update_milestone_progress(self, db_session, test_user):
        """Test updating milestone progress."""
        milestone = UserJourneyMilestone(
            user_id=test_user.id,
            milestone_type="skill_acquisition",
            milestone_data={"skill": "Python", "level": "intermediate"},
            title="Learn Python",
            category="skill",
            progress_percentage=25.0,
            status="active"
        )
        db_session.add(milestone)
        db_session.commit()
        
        # Update progress
        milestone.progress_percentage = 75.0
        milestone.milestone_data["completed_modules"] = ["basics", "data structures", "oop"]
        db_session.commit()
        
        # Refresh and verify
        db_session.refresh(milestone)
        assert milestone.progress_percentage == 75.0
        assert "completed_modules" in milestone.milestone_data
    
    def test_complete_milestone(self, db_session, test_user):
        """Test completing a milestone."""
        milestone = UserJourneyMilestone(
            user_id=test_user.id,
            milestone_type="assessment_completed",
            milestone_data={"test": "HEXACO", "score": {"openness": 0.8}},
            title="Complete HEXACO Assessment",
            category="assessment",
            progress_percentage=100.0,
            status="completed",
            achieved_at=datetime.utcnow()
        )
        db_session.add(milestone)
        db_session.commit()
        
        assert milestone.status == "completed"
        assert milestone.achieved_at is not None
        assert milestone.progress_percentage == 100.0
    
    def test_milestone_to_dict(self, db_session, test_user):
        """Test converting milestone to dictionary."""
        milestone = UserJourneyMilestone(
            user_id=test_user.id,
            milestone_type="peer_connection",
            milestone_data={"peer_id": 123, "match_score": 0.85},
            title="Connected with Peer Mentor",
            category="peer",
            status="completed"
        )
        db_session.add(milestone)
        db_session.commit()
        
        milestone_dict = milestone.to_dict()
        assert milestone_dict["milestone_type"] == "peer_connection"
        assert milestone_dict["category"] == "peer"
        assert milestone_dict["status"] == "completed"
        assert "peer_id" in milestone_dict["milestone_data"]


class TestSavedRecommendationUpdates:
    """Test updates to SavedRecommendation model."""
    
    def test_create_recommendation_with_orientator_fields(self, db_session, test_user):
        """Test creating a recommendation with new Orientator AI fields."""
        conversation = Conversation(user_id=test_user.id, title="Career Exploration")
        db_session.add(conversation)
        db_session.commit()
        
        recommendation = SavedRecommendation(
            user_id=test_user.id,
            oasis_code="DS001",
            label="Data Scientist",
            description="Analyze complex data to help organizations make decisions",
            # New Orientator AI fields
            source_tool="oasis_explorer",
            conversation_id=conversation.id,
            component_type="job_card",
            component_data={
                "match_score": 0.92,
                "skills_matched": ["Python", "Statistics", "Machine Learning"],
                "skills_gap": ["Deep Learning", "Big Data"]
            },
            interaction_metadata={
                "saved_from": "chat_component",
                "user_action": "explicit_save",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        db_session.add(recommendation)
        db_session.commit()
        db_session.refresh(recommendation)
        
        assert recommendation.source_tool == "oasis_explorer"
        assert recommendation.conversation_id == conversation.id
        assert recommendation.component_type == "job_card"
        assert "match_score" in recommendation.component_data
        assert recommendation.interaction_metadata["user_action"] == "explicit_save"
    
    def test_query_recommendations_by_tool(self, db_session, test_user):
        """Test querying recommendations by source tool."""
        conversation = Conversation(user_id=test_user.id, title="Test")
        db_session.add(conversation)
        db_session.commit()
        
        # Create recommendations from different tools
        rec1 = SavedRecommendation(
            user_id=test_user.id,
            oasis_code="JOB001",
            label="Job 1",
            source_tool="oasis_explorer"
        )
        rec2 = SavedRecommendation(
            user_id=test_user.id,
            oasis_code="JOB002",
            label="Job 2",
            source_tool="career_tree"
        )
        rec3 = SavedRecommendation(
            user_id=test_user.id,
            oasis_code="JOB003",
            label="Job 3",
            source_tool="oasis_explorer"
        )
        
        db_session.add_all([rec1, rec2, rec3])
        db_session.commit()
        
        # Query by tool
        oasis_recs = db_session.query(SavedRecommendation).filter_by(
            user_id=test_user.id,
            source_tool="oasis_explorer"
        ).all()
        
        assert len(oasis_recs) == 2
        assert all(rec.source_tool == "oasis_explorer" for rec in oasis_recs)


class TestModelRelationships:
    """Test relationships between models."""
    
    def test_conversation_relationships(self, db_session, test_user):
        """Test relationships between conversation and new models."""
        conversation = Conversation(user_id=test_user.id, title="AI Chat")
        db_session.add(conversation)
        db_session.commit()
        
        # Add message with component
        message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content="Here's what I found:"
        )
        db_session.add(message)
        db_session.commit()
        
        component = MessageComponent(
            message_id=message.id,
            component_type="skills",
            component_data={"skills": ["Python"]}
        )
        db_session.add(component)
        
        # Add tool invocation
        invocation = ToolInvocation(
            conversation_id=conversation.id,
            tool_name="esco_skills",
            user_id=test_user.id
        )
        db_session.add(invocation)
        
        # Add journey milestone
        milestone = UserJourneyMilestone(
            user_id=test_user.id,
            conversation_id=conversation.id,
            milestone_type="goal_set",
            milestone_data={},
            title="Career Goal Set"
        )
        db_session.add(milestone)
        
        db_session.commit()
        
        # Test relationships
        assert len(conversation.messages) == 1
        assert len(conversation.messages[0].components) == 1
        assert len(conversation.tool_invocations) == 1
        assert len(conversation.journey_milestones) == 1
        assert conversation.tool_invocations[0].tool_name == "esco_skills"
    
    def test_user_relationships(self, db_session, test_user):
        """Test relationships between user and new models."""
        # Create test data
        conversation = Conversation(user_id=test_user.id, title="Test")
        db_session.add(conversation)
        db_session.commit()
        
        invocation = ToolInvocation(
            conversation_id=conversation.id,
            tool_name="test_tool",
            user_id=test_user.id
        )
        milestone = UserJourneyMilestone(
            user_id=test_user.id,
            milestone_type="test",
            milestone_data={},
            title="Test Milestone"
        )
        
        db_session.add_all([invocation, milestone])
        db_session.commit()
        
        # Test relationships
        assert len(test_user.tool_invocations) == 1
        assert len(test_user.journey_milestones) == 1
        assert test_user.tool_invocations[0].tool_name == "test_tool"
        assert test_user.journey_milestones[0].title == "Test Milestone"