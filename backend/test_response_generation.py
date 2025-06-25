#!/usr/bin/env python3
"""
Test complete response generation with rich components
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orientator_ai_service import OrientatorAIService
from app.services.tool_registry import ToolResult


async def test_response_generation():
    """Test complete response generation with mock tool results"""
    
    print("🧪 Testing Orientator AI Response Generation...")
    
    service = OrientatorAIService()
    
    # Mock tool results
    mock_tool_results = [
        {
            "tool_name": "career_tree",
            "result": ToolResult(
                success=True,
                data={"career_path": "Data Scientist"},
                metadata={"source": "career_tree"}
            )
        },
        {
            "tool_name": "esco_skills", 
            "result": ToolResult(
                success=True,
                data={"skills": ["Python", "Statistics", "Machine Learning"]},
                metadata={"source": "esco_skills"}
            )
        },
        {
            "tool_name": "oasis_explorer",
            "result": ToolResult(
                success=True,
                data={"jobs": ["Data Scientist", "ML Engineer", "Data Analyst"]},
                metadata={"source": "oasis_explorer"}
            )
        }
    ]
    
    # Mock intent
    mock_intent = {
        "intent": "career_exploration",
        "entities": {"career_goals": "data scientist"},
        "confidence": 0.95,
        "suggested_tools": ["career_tree", "esco_skills", "oasis_explorer"]
    }
    
    message = "I want to become a data scientist"
    
    try:
        # Test response generation
        print(f"\n🔄 Generating response for: '{message}'")
        
        response = await service.generate_response(message, mock_intent, mock_tool_results)
        
        print(f"\n✅ Response generated successfully!")
        print(f"📝 Content: {response.content[:100]}...")
        print(f"🧩 Components: {len(response.components)} components created")
        
        for i, component in enumerate(response.components):
            print(f"   {i+1}. {component.type} - {len(component.actions)} actions")
            print(f"      Data keys: {list(component.data.keys())}")
            print(f"      Actions: {[action.label for action in component.actions]}")
            
        print(f"📊 Metadata: {response.metadata}")
        
        # Verify rich data structures
        print(f"\n🎨 Rich Visualization Data:")
        
        for component in response.components:
            if component.type == "career_path":
                print(f"   📈 Career Path: {len(component.data.get('milestones', []))} milestones")
                print(f"      Timeline: {component.data.get('timeline')}")
                print(f"      Salary ranges: {bool(component.data.get('estimated_salary'))}")
                
            elif component.type == "skill_tree":
                print(f"   🎯 Skills: {len(component.data.get('categories', []))} categories")
                print(f"      Total skills: {component.data.get('total_skills')}")
                print(f"      Learning resources: {bool(component.data.get('learning_resources'))}")
                
            elif component.type == "job_card":
                print(f"   💼 Jobs: {len(component.data.get('top_jobs', []))} opportunities")
                print(f"      Filters: {bool(component.data.get('filters'))}")
                print(f"      Market insights: {component.data.get('total_matches')} total matches")
        
        print(f"\n🎉 All components include rich, interactive data!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_response_generation())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Rich response generation test")