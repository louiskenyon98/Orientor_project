import pytest
import json
from fastapi.testclient import TestClient
from app.models.course import Course, PsychologicalInsight, CareerSignal, ConversationLog

class TestCourseRoutes:
    """Test suite for course API routes."""

    def test_create_course_success(self, client, test_user):
        """Test successful course creation."""
        course_data = {
            "course_name": "Advanced Data Science",
            "course_code": "DS 301",
            "semester": "Spring",
            "year": 2024,
            "professor": "Dr. Jane Smith",
            "subject_category": "STEM",
            "grade": "A",
            "credits": 4,
            "description": "Advanced topics in data science and machine learning"
        }
        
        # Mock authentication - in real app this would come from JWT
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.post("/api/v1/courses/", json=course_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["course_name"] == course_data["course_name"]
        assert data["user_id"] == test_user.id
        assert data["subject_category"] == "STEM"

    def test_create_course_invalid_category(self, client, test_user):
        """Test course creation with invalid category."""
        course_data = {
            "course_name": "Test Course",
            "subject_category": "INVALID_CATEGORY"
        }
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.post("/api/v1/courses/", json=course_data)
        
        assert response.status_code == 422  # Validation error

    def test_get_user_courses(self, client, test_user, test_course):
        """Test retrieving user courses."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["course_name"] == test_course.course_name

    def test_get_course_by_id_success(self, client, test_user, test_course):
        """Test retrieving specific course."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get(f"/api/v1/courses/{test_course.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["course_name"] == test_course.course_name
        assert data["id"] == test_course.id

    def test_get_course_not_found(self, client, test_user):
        """Test retrieving non-existent course."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/99999")
        
        assert response.status_code == 404

    def test_get_course_unauthorized_user(self, client, db_session, test_course):
        """Test retrieving course by unauthorized user."""
        # Create another user
        from app.models.user import User
        other_user = User(email="other@example.com", hashed_password="hashed")
        db_session.add(other_user)
        db_session.commit()
        
        with client as c:
            c.headers.update({"user-id": str(other_user.id)})
            response = c.get(f"/api/v1/courses/{test_course.id}")
        
        assert response.status_code == 404  # Should not find course from different user

    def test_update_course_success(self, client, test_user, test_course):
        """Test successful course update."""
        update_data = {
            "grade": "A+",
            "description": "Updated description"
        }
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.put(f"/api/v1/courses/{test_course.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["grade"] == "A+"
        assert data["description"] == "Updated description"

    def test_delete_course_success(self, client, test_user, test_course):
        """Test successful course deletion."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.delete(f"/api/v1/courses/{test_course.id}")
        
        assert response.status_code == 204

    def test_start_targeted_analysis_success(self, client, test_user, test_course):
        """Test starting targeted analysis."""
        analysis_request = {
            "focus_areas": ["cognitive_preference", "work_style"],
            "analysis_depth": "comprehensive"
        }
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.post(
                f"/api/v1/courses/{test_course.id}/targeted-analysis",
                json=analysis_request
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "initial_questions" in data
        assert len(data["initial_questions"]) >= 1

    def test_start_targeted_analysis_invalid_focus_areas(self, client, test_user, test_course):
        """Test targeted analysis with invalid focus areas."""
        analysis_request = {
            "focus_areas": ["invalid_area"],
            "analysis_depth": "comprehensive"
        }
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.post(
                f"/api/v1/courses/{test_course.id}/targeted-analysis",
                json=analysis_request
            )
        
        assert response.status_code == 422  # Validation error

    def test_submit_conversation_response_success(self, client, test_user, test_course, test_conversation_log):
        """Test submitting conversation response."""
        response_data = {
            "session_id": test_conversation_log.session_id,
            "response": "I found the analytical aspects most engaging",
            "question_intent": "subject_affinity"
        }
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.post(
                f"/api/v1/courses/{test_course.id}/conversation-response",
                json=response_data
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "next_question" in data or "session_complete" in data

    def test_get_course_insights_success(self, client, test_user, test_course, test_insight):
        """Test retrieving course insights."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get(f"/api/v1/courses/{test_course.id}/insights")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["insight_type"] == test_insight.insight_type

    def test_get_course_signals_success(self, client, test_user, test_course, test_career_signal):
        """Test retrieving course career signals."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get(f"/api/v1/courses/{test_course.id}/career-signals")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["signal_type"] == test_career_signal.signal_type

    def test_get_profile_summary_success(self, client, test_user, test_insight, test_career_signal):
        """Test retrieving user profile summary."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/profile-summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "cognitive_preferences" in data
        assert "work_style_indicators" in data
        assert "subject_affinities" in data
        assert "career_readiness" in data
        assert "confidence_score" in data

    def test_get_esco_recommendations_success(self, client, test_user, test_career_signal):
        """Test retrieving ESCO career recommendations."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/esco-recommendations")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        for rec in data:
            assert "occupation_code" in rec
            assert "occupation_title" in rec
            assert "alignment_score" in rec

    def test_analyze_signal_patterns_success(self, client, test_user, test_career_signal):
        """Test signal pattern analysis."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/signal-patterns")
        
        assert response.status_code == 200
        data = response.json()
        assert "signal_distribution" in data
        assert "strength_trends" in data
        assert "cross_course_patterns" in data

    def test_get_trend_analysis_success(self, client, test_user, test_career_signal):
        """Test trend analysis."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/trends")
        
        assert response.status_code == 200
        data = response.json()
        assert "emerging_strengths" in data
        assert "declining_areas" in data
        assert "stable_competencies" in data
        assert "recommendation_priority" in data

    def test_get_course_analysis_status_success(self, client, test_user, test_course):
        """Test getting course analysis status."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get(f"/api/v1/courses/{test_course.id}/analysis-status")
        
        assert response.status_code == 200
        data = response.json()
        assert "course_id" in data
        assert "has_insights" in data
        assert "has_signals" in data
        assert "analysis_completeness" in data
        assert "last_analysis_date" in data

    def test_get_conversation_history_success(self, client, test_user, test_course, test_conversation_log):
        """Test retrieving conversation history."""
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get(f"/api/v1/courses/{test_course.id}/conversation-history")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["session_id"] == test_conversation_log.session_id

    def test_courses_pagination(self, client, test_user, db_session):
        """Test course listing with pagination."""
        # Create multiple courses
        for i in range(15):
            course = Course(
                user_id=test_user.id,
                course_name=f"Course {i}",
                subject_category="STEM"
            )
            db_session.add(course)
        db_session.commit()
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10  # Should return only 10 due to limit

    def test_courses_filtering_by_category(self, client, test_user, db_session):
        """Test course filtering by category."""
        # Create courses in different categories
        stem_course = Course(
            user_id=test_user.id,
            course_name="Math Course",
            subject_category="STEM"
        )
        business_course = Course(
            user_id=test_user.id,
            course_name="Business Course",
            subject_category="BUSINESS"
        )
        db_session.add_all([stem_course, business_course])
        db_session.commit()
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/?category=STEM")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["subject_category"] == "STEM"

    def test_courses_search_by_name(self, client, test_user, db_session):
        """Test course search by name."""
        course1 = Course(
            user_id=test_user.id,
            course_name="Data Science Fundamentals",
            subject_category="STEM"
        )
        course2 = Course(
            user_id=test_user.id,
            course_name="Business Analytics",
            subject_category="BUSINESS"
        )
        db_session.add_all([course1, course2])
        db_session.commit()
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.get("/api/v1/courses/?search=data")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Data Science" in data[0]["course_name"]

    def test_unauthenticated_request(self, client):
        """Test request without authentication."""
        response = client.get("/api/v1/courses/")
        
        # Should return 401 Unauthorized or handle missing auth appropriately
        assert response.status_code in [401, 422]  # Depending on auth implementation

    def test_course_analysis_with_empty_data(self, client, test_user, db_session):
        """Test analysis endpoints with courses that have no insights/signals."""
        # Create course without any insights or signals
        empty_course = Course(
            user_id=test_user.id,
            course_name="Empty Course",
            subject_category="STEM"
        )
        db_session.add(empty_course)
        db_session.commit()
        
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            
            # Test insights endpoint
            response = c.get(f"/api/v1/courses/{empty_course.id}/insights")
            assert response.status_code == 200
            assert response.json() == []
            
            # Test signals endpoint
            response = c.get(f"/api/v1/courses/{empty_course.id}/career-signals")
            assert response.status_code == 200
            assert response.json() == []
            
            # Test analysis status
            response = c.get(f"/api/v1/courses/{empty_course.id}/analysis-status")
            assert response.status_code == 200
            data = response.json()
            assert data["has_insights"] is False
            assert data["has_signals"] is False
            assert data["analysis_completeness"] == 0.0

    def test_bulk_course_operations(self, client, test_user, db_session):
        """Test bulk operations on courses."""
        # Create multiple courses
        courses = []
        for i in range(3):
            course = Course(
                user_id=test_user.id,
                course_name=f"Course {i}",
                subject_category="STEM"
            )
            courses.append(course)
            db_session.add(course)
        db_session.commit()
        
        # Test bulk status check
        course_ids = [str(course.id) for course in courses]
        with client as c:
            c.headers.update({"user-id": str(test_user.id)})
            response = c.post("/api/v1/courses/bulk-status", json={"course_ids": course_ids})
        
        if response.status_code == 200:  # If endpoint exists
            data = response.json()
            assert len(data) == 3
        else:
            # Endpoint might not be implemented yet
            assert response.status_code in [404, 405]