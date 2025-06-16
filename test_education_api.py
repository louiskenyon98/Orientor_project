#!/usr/bin/env python3
"""
Test script for the Education API
Run this to test the backend search functionality
"""

import asyncio
import json
from backend_education_api import (
    EducationSearchService, 
    ProgramSearchRequest, 
    EducationDataService
)

async def test_education_api():
    """Test the education API functionality"""
    print("🧪 Testing Education API")
    print("=" * 50)
    
    # Test 1: Get all programs
    print("\n1️⃣ Testing: Get All Programs")
    async with EducationDataService() as data_service:
        programs = await data_service.get_all_programs()
        print(f"✅ Found {len(programs)} total programs")
        
        for program in programs[:3]:  # Show first 3
            print(f"   - {program.title} at {program.institution.name}")
    
    # Test 2: Basic search
    print("\n2️⃣ Testing: Basic Text Search")
    search_service = EducationSearchService()
    
    search_request = ProgramSearchRequest(
        query="computer science",
        limit=10
    )
    
    result = await search_service.search_programs(search_request)
    print(f"✅ Search for 'computer science' found {result.total_count} programs")
    
    for program in result.programs:
        print(f"   - {program['title']} at {program['institution']['name']}")
    
    # Test 3: Filtered search
    print("\n3️⃣ Testing: Filtered Search (CEGEPs only)")
    search_request = ProgramSearchRequest(
        institution_types=["cegep"],
        limit=10
    )
    
    result = await search_service.search_programs(search_request)
    print(f"✅ CEGEP-only search found {result.total_count} programs")
    
    for program in result.programs:
        print(f"   - {program['title']} at {program['institution']['name']} ({program['institution']['institution_type']})")
    
    # Test 4: Holland personality matching
    print("\n4️⃣ Testing: Holland Personality Matching")
    mock_holland_scores = {
        "R": 7.5, "I": 8.2, "A": 5.1, 
        "S": 6.3, "E": 4.8, "C": 5.9
    }
    
    search_request = ProgramSearchRequest(
        holland_matching=True,
        user_id=1,
        limit=10
    )
    
    result = await search_service.search_programs(search_request, mock_holland_scores)
    print(f"✅ Personality-matched search found {result.total_count} programs")
    
    for program in result.programs:
        compatibility = program.get('holland_compatibility', {}).get('overall', 0) * 100
        print(f"   - {program['title']} ({compatibility:.0f}% match)")
    
    # Test 5: Combined filters
    print("\n5️⃣ Testing: Combined Filters")
    search_request = ProgramSearchRequest(
        query="science",
        institution_types=["university"],
        max_tuition=10000,
        min_employment_rate=90,
        holland_matching=True,
        user_id=1,
        limit=10
    )
    
    result = await search_service.search_programs(search_request, mock_holland_scores)
    print(f"✅ Advanced filtered search found {result.total_count} programs")
    
    for program in result.programs:
        tuition = program.get('tuition_domestic', 0)
        employment = program.get('employment_rate', 0)
        print(f"   - {program['title']} (${tuition}/year, {employment}% employment)")
    
    # Test 6: Search metadata
    print("\n6️⃣ Testing: Search Metadata")
    print(f"✅ Search metadata:")
    print(f"   - Holland matching enabled: {result.search_metadata['holland_matching_enabled']}")
    print(f"   - Total available programs: {result.search_metadata['total_available_programs']}")
    print(f"   - Filters applied: {json.dumps(result.search_metadata['filters_applied'], indent=2)}")
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)

async def test_data_sources():
    """Test real data source connections"""
    print("\n🌐 Testing Data Source Connections")
    print("=" * 50)
    
    async with EducationDataService() as data_service:
        # Test Données Québec API
        print("\n📊 Testing Données Québec API...")
        datasets = await data_service.fetch_donnees_quebec_datasets()
        print(f"✅ Found {len(datasets)} education datasets from Données Québec")
        
        if datasets:
            for dataset in datasets[:3]:
                print(f"   - {dataset.get('title', 'N/A')}")
        
        # Test CEGEP programs fetching
        print("\n🏫 Testing CEGEP Programs...")
        cegep_programs = await data_service.fetch_cegep_programs()
        print(f"✅ Loaded {len(cegep_programs)} CEGEP programs")
        
        # Test University programs fetching
        print("\n🎓 Testing University Programs...")
        uni_programs = await data_service.fetch_university_programs()
        print(f"✅ Loaded {len(uni_programs)} university programs")
        
        # Test Holland compatibility calculation
        print("\n🧠 Testing Holland Compatibility...")
        if cegep_programs:
            program = cegep_programs[0]
            mock_scores = {"R": 8.0, "I": 7.5, "A": 5.0, "S": 6.0, "E": 4.0, "C": 6.5}
            compatibility = await data_service.calculate_holland_compatibility(program, mock_scores)
            print(f"✅ Calculated compatibility for {program.title}:")
            for code, score in compatibility.items():
                print(f"   - {code}: {score:.2f}")

if __name__ == "__main__":
    print("🚀 Starting Education API Tests")
    print("This will test the real search functionality for Quebec education programs")
    
    # Run main API tests
    asyncio.run(test_education_api())
    
    # Run data source tests
    asyncio.run(test_data_sources())
    
    print("\n✨ Testing complete! The education search API is ready to use.")
    print("\nNext steps:")
    print("1. Start your backend server with the API endpoints")
    print("2. Test the frontend by visiting /education")
    print("3. Try searching for programs by name, institution, or field")
    print("4. Enable Holland personality matching for personalized results")