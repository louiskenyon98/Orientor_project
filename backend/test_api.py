#!/usr/bin/env python3
import requests
import json

def test_course_creation():
    """Test course creation API endpoint"""
    url = "http://localhost:8000/api/v1/courses"
    
    course_data = {
        "course_name": "Introduction to Python Programming",
        "course_code": "CS 101",
        "semester": "Fall",
        "year": 2024,
        "professor": "Dr. Smith",
        "subject_category": "STEM",
        "grade": "A",
        "credits": 3,
        "description": "An introductory course on Python programming"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print("Testing course creation...")
        response = requests.post(url, json=course_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ Course created successfully!")
            return response.json()
        else:
            print(f"❌ Failed to create course: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting to API: {str(e)}")
        return None

def test_get_courses():
    """Test getting courses"""
    url = "http://localhost:8000/api/v1/courses"
    
    try:
        print("\nTesting get courses...")
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Get courses successful!")
            return response.json()
        else:
            print(f"❌ Failed to get courses: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error connecting to API: {str(e)}")
        return None

if __name__ == "__main__":
    # Test course creation
    created_course = test_course_creation()
    
    # Test getting courses
    courses = test_get_courses()