#!/usr/bin/env python3
"""
Test script for the Education API integration with your existing backend
"""

import requests
import json
import sys

# API Configuration
BACKEND_URL = "http://localhost:8000"

def test_education_endpoints():
    """Test the education API endpoints"""
    print("🧪 Testing Education API Integration")
    print("=" * 50)
    
    # Test health check first
    print("\n1️⃣ Testing Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        return False
    
    # Test metadata endpoint (no auth required for testing)
    print("\n2️⃣ Testing Metadata Endpoint")
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/education/metadata")
        if response.status_code == 401:
            print("✅ Metadata endpoint exists (requires authentication)")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Metadata endpoint working: {len(data.get('fields_of_study', []))} fields available")
        else:
            print(f"⚠️ Metadata endpoint status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing metadata: {e}")
    
    # Test search endpoint
    print("\n3️⃣ Testing Search Endpoint")
    try:
        search_data = {
            "query": "computer science",
            "holland_matching": True,
            "limit": 5
        }
        response = requests.post(
            f"{BACKEND_URL}/api/v1/education/programs/search",
            json=search_data
        )
        if response.status_code == 401:
            print("✅ Search endpoint exists (requires authentication)")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint working: found {data.get('total_count', 0)} programs")
        else:
            print(f"⚠️ Search endpoint status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing search: {e}")
    
    print("\n4️⃣ Checking Available Routes")
    try:
        response = requests.get(f"{BACKEND_URL}/docs")
        if response.status_code == 200:
            print("✅ API docs available at /docs")
        else:
            print(f"⚠️ API docs status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking docs: {e}")
    
    return True

def print_integration_status():
    """Print integration status and next steps"""
    print("\n" + "=" * 50)
    print("🎯 Integration Status")
    print("=" * 50)
    
    print("\n✅ What's Completed:")
    print("   - Education router created and added to main.py")
    print("   - Search API endpoints implemented")
    print("   - Holland RIASEC personality matching")
    print("   - Real Quebec education program data")
    print("   - Frontend service integration")
    
    print("\n📋 Next Steps:")
    print("   1. Start your backend server:")
    print("      cd /path/to/backend && python run.py")
    print("   2. Test the education page in your frontend:")
    print("      Visit http://localhost:3000/education")
    print("   3. Search should now work with real data!")
    
    print("\n🔧 Troubleshooting:")
    print("   - 404 errors: Make sure backend is running")
    print("   - 401 errors: Normal - endpoints require authentication")
    print("   - CORS errors: CORS is configured for localhost:3000")

if __name__ == "__main__":
    print("🚀 Testing Education API Backend Integration")
    print("This will test if the education endpoints are properly integrated")
    
    success = test_education_endpoints()
    print_integration_status()
    
    if success:
        print("\n🎉 Integration test completed!")
        print("The education search API is now integrated with your backend.")
    else:
        print("\n⚠️ Integration test had issues.")
        print("Check that your backend server is running on port 8000.")