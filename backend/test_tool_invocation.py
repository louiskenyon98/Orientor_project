#!/usr/bin/env python3
"""
Test tool invocation directly to debug the issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orientator_ai_service import OrientatorAIService


async def test_tool_invocation():
    """Test if tool invocation works with different messages"""
    
    print("🧪 Testing Orientator AI Tool Invocation...")
    
    service = OrientatorAIService()
    
    test_messages = [
        "I want to become a data scientist",
        "What skills do I need for software engineering?", 
        "Tell me about careers in healthcare",
        "I need help with my career path",
        "What jobs are available for someone with my skills?",
        "Hello, how are you?"  # Should trigger fallback
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        
        try:
            # Test intent analysis
            intent = await service.analyze_intent(message)
            print(f"   Intent: {intent.get('intent', 'unknown')}")
            print(f"   Confidence: {intent.get('confidence', 0)}")
            print(f"   LLM suggested tools: {intent.get('suggested_tools', [])}")
            
            # Test tool determination
            tools = service.determine_tools(intent, message)
            print(f"   Selected tools: {[tool['tool_name'] for tool in tools]}")
            
            # Show tool parameters
            for tool in tools:
                print(f"     - {tool['tool_name']}: {tool['params']}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n✅ Tool invocation test completed!")


if __name__ == "__main__":
    asyncio.run(test_tool_invocation())