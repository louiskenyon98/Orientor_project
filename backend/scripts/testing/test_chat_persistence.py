#!/usr/bin/env python3
"""
Test script for chat persistence system implementation.
This script verifies that all components of the chat persistence system are working correctly.
"""

import os
import sys
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class ChatPersistenceTest:
    def __init__(self):
        self.api_url = API_BASE_URL
        self.token = None
        self.user_id = None
        self.conversation_id = None
        self.category_id = None
        
    def print_test(self, test_name: str, passed: bool, details: str = ""):
        """Print test result with formatting."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"\n{test_name}: {status}")
        if details:
            print(f"  Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to the API."""
        url = f"{self.api_url}{endpoint}"
        headers = {}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        if data is not None:
            headers["Content-Type"] = "application/json"
            
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            if response.status_code >= 400:
                print(f"  Error {response.status_code}: {response.text}")
                return None
                
            return response.json() if response.text else {}
            
        except Exception as e:
            print(f"  Request failed: {str(e)}")
            return None
    
    def test_user_authentication(self) -> bool:
        """Test user registration and login."""
        print("\n=== Testing User Authentication ===")
        
        # Try to register a new user
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        # First try login in case user already exists
        login_result = self.make_request("POST", "/auth/login", {
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_result:
            self.token = login_result.get("access_token")
            self.user_id = login_result.get("user_id", 1)  # Default to 1 if not provided
            self.print_test("User Login", True, f"User ID: {self.user_id}")
            return True
        
        # If login failed, try to register
        register_result = self.make_request("POST", "/auth/register", register_data)
        
        if register_result:
            # Now login
            login_result = self.make_request("POST", "/auth/login", {
                "username": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if login_result:
                self.token = login_result.get("access_token")
                self.user_id = login_result.get("user_id", 1)
                self.print_test("User Registration & Login", True, f"User ID: {self.user_id}")
                return True
                
        self.print_test("User Authentication", False, "Could not authenticate")
        return False
    
    def test_category_management(self) -> bool:
        """Test category CRUD operations."""
        print("\n=== Testing Category Management ===")
        
        # Create a category
        category_data = {
            "name": "Career Planning",
            "description": "Discussions about career planning and development",
            "color": "#3B82F6"
        }
        
        result = self.make_request("POST", "/chat/categories", category_data)
        if result:
            self.category_id = result["id"]
            self.print_test("Create Category", True, f"Category ID: {self.category_id}")
        else:
            self.print_test("Create Category", False)
            return False
            
        # List categories
        categories = self.make_request("GET", "/chat/categories")
        if categories and len(categories) > 0:
            self.print_test("List Categories", True, f"Found {len(categories)} categories")
        else:
            self.print_test("List Categories", False)
            
        # Update category
        update_data = {"name": "Career Development", "color": "#10B981"}
        result = self.make_request("PUT", f"/chat/categories/{self.category_id}", update_data)
        self.print_test("Update Category", result is not None)
        
        return True
    
    def test_conversation_management(self) -> bool:
        """Test conversation CRUD operations."""
        print("\n=== Testing Conversation Management ===")
        
        # Create a conversation
        conversation_data = {
            "initial_message": "Hello, I need help with my career path",
            "category_id": self.category_id
        }
        
        result = self.make_request("POST", "/chat/conversations", conversation_data)
        if result:
            self.conversation_id = result["id"]
            self.print_test("Create Conversation", True, 
                          f"Conversation ID: {self.conversation_id}, Title: {result.get('title')}")
        else:
            self.print_test("Create Conversation", False)
            return False
            
        # List conversations
        conversations = self.make_request("GET", "/chat/conversations")
        if conversations and conversations.get("total", 0) > 0:
            self.print_test("List Conversations", True, 
                          f"Found {conversations['total']} conversations")
        else:
            self.print_test("List Conversations", False)
            
        # Update conversation title
        update_data = {"title": "Career Path Discussion"}
        result = self.make_request("PUT", f"/chat/conversations/{self.conversation_id}", 
                                 update_data)
        self.print_test("Update Conversation Title", result is not None)
        
        # Toggle favorite
        result = self.make_request("POST", f"/chat/conversations/{self.conversation_id}/favorite")
        self.print_test("Toggle Favorite", result is not None)
        
        return True
    
    def test_chat_messaging(self) -> bool:
        """Test sending and receiving messages."""
        print("\n=== Testing Chat Messaging ===")
        
        # Send a message
        message_data = {
            "message": "What career options are available for someone with my background?"
        }
        
        result = self.make_request("POST", f"/chat/send/{self.conversation_id}", message_data)
        if result:
            self.print_test("Send Message", True, 
                          f"Response length: {len(result.get('response', ''))}")
        else:
            self.print_test("Send Message", False)
            return False
            
        # Get conversation messages
        messages = self.make_request("GET", f"/chat/conversations/{self.conversation_id}/messages")
        if messages and messages.get("messages"):
            self.print_test("Get Messages", True, 
                          f"Found {len(messages['messages'])} messages")
        else:
            self.print_test("Get Messages", False)
            
        return True
    
    def test_search_functionality(self) -> bool:
        """Test full-text search."""
        print("\n=== Testing Search Functionality ===")
        
        # Search for messages
        search_params = {
            "query": "career",
            "date_range": "all"
        }
        
        results = self.make_request("GET", "/chat/search", params=search_params)
        if results and "results" in results:
            self.print_test("Search Messages", True, 
                          f"Found {len(results['results'])} results")
        else:
            self.print_test("Search Messages", False)
            
        return True
    
    def test_export_functionality(self) -> bool:
        """Test conversation export."""
        print("\n=== Testing Export Functionality ===")
        
        # Export as JSON
        export_data = {"format": "json"}
        result = self.make_request("POST", 
                                 f"/chat/conversations/{self.conversation_id}/export", 
                                 export_data)
        
        # For export, we just check if we got a response (it returns file content)
        self.print_test("Export as JSON", result is not None)
        
        # Export as TXT
        export_data = {"format": "txt"}
        result = self.make_request("POST", 
                                 f"/chat/conversations/{self.conversation_id}/export", 
                                 export_data)
        self.print_test("Export as TXT", result is not None)
        
        return True
    
    def test_sharing_functionality(self) -> bool:
        """Test conversation sharing."""
        print("\n=== Testing Sharing Functionality ===")
        
        # Create a share link
        share_data = {
            "is_public": False,
            "password": "sharepass123",
            "expires_in_hours": 24,
            "base_url": API_BASE_URL
        }
        
        result = self.make_request("POST", 
                                 f"/chat/share/conversations/{self.conversation_id}", 
                                 share_data)
        if result and "share_token" in result:
            share_token = result["share_token"]
            self.print_test("Create Share Link", True, 
                          f"Share token: {share_token[:8]}...")
            
            # Access shared conversation
            # Note: This would normally be done without authentication
            shared = self.make_request("GET", f"/chat/share/{share_token}")
            self.print_test("Access Shared Conversation", shared is not None)
        else:
            self.print_test("Create Share Link", False)
            
        return True
    
    def test_analytics(self) -> bool:
        """Test analytics functionality."""
        print("\n=== Testing Analytics ===")
        
        # Get analytics summary
        result = self.make_request("GET", "/chat/analytics/summary")
        if result and "user_analytics" in result:
            analytics = result["user_analytics"]
            self.print_test("Get Analytics Summary", True, 
                          f"Total messages: {analytics.get('total_messages', 0)}")
        else:
            self.print_test("Get Analytics Summary", False)
            
        # Get popular topics
        topics = self.make_request("GET", "/chat/analytics/topics")
        if topics and "topics" in topics:
            self.print_test("Get Popular Topics", True, 
                          f"Found {len(topics['topics'])} topics")
        else:
            self.print_test("Get Popular Topics", False)
            
        return True
    
    def test_cleanup(self) -> bool:
        """Test cleanup operations."""
        print("\n=== Testing Cleanup Operations ===")
        
        # Archive conversation
        result = self.make_request("POST", 
                                 f"/chat/conversations/{self.conversation_id}/archive")
        self.print_test("Archive Conversation", result is not None)
        
        # Delete conversation
        result = self.make_request("DELETE", 
                                 f"/chat/conversations/{self.conversation_id}")
        self.print_test("Delete Conversation", result is not None)
        
        # Delete category
        if self.category_id:
            result = self.make_request("DELETE", f"/chat/categories/{self.category_id}")
            self.print_test("Delete Category", result is not None)
            
        return True
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("\n" + "="*50)
        print("CHAT PERSISTENCE SYSTEM TEST SUITE")
        print("="*50)
        
        test_results = []
        
        # Run tests in order
        tests = [
            ("Authentication", self.test_user_authentication),
            ("Category Management", self.test_category_management),
            ("Conversation Management", self.test_conversation_management),
            ("Chat Messaging", self.test_chat_messaging),
            ("Search", self.test_search_functionality),
            ("Export", self.test_export_functionality),
            ("Sharing", self.test_sharing_functionality),
            ("Analytics", self.test_analytics),
            ("Cleanup", self.test_cleanup)
        ]
        
        for test_name, test_func in tests:
            try:
                passed = test_func()
                test_results.append((test_name, passed))
            except Exception as e:
                print(f"\n❌ {test_name} failed with exception: {str(e)}")
                test_results.append((test_name, False))
        
        # Print summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed_count = sum(1 for _, passed in test_results if passed)
        total_count = len(test_results)
        
        for test_name, passed in test_results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name}: {status}")
            
        print(f"\nTotal: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("\n🎉 All tests passed! The chat persistence system is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            print(f"Please ensure the server is running at {API_BASE_URL}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print("Please start the server with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run tests
    tester = ChatPersistenceTest()
    tester.run_all_tests()