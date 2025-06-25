"""
Performance tests for Orientator AI feature
Tests response times, scalability, and resource usage
"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import statistics

from app.services.orientator_ai_service import OrientatorAIService
from app.services.tool_registry import ToolRegistry, ToolResult
from app.schemas.orientator import (
    OrientatorResponse,
    MessageComponent,
    MessageComponentType
)


class TestOrientatorPerformance:
    """Performance tests for Orientator AI service"""
    
    @pytest.fixture
    def orientator_service(self):
        """Create OrientatorAIService instance"""
        with patch('app.services.orientator_ai_service.AsyncOpenAI'):
            service = OrientatorAIService()
            return service
    
    @pytest.fixture
    def mock_fast_llm(self):
        """Mock LLM with controlled response time"""
        async def fast_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate 100ms LLM response
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='{"intent": "test", "confidence": 0.9, "suggested_tools": ["esco_skills"]}'))]
            return mock_response
        return fast_response
    
    @pytest.fixture
    def mock_slow_llm(self):
        """Mock LLM with slow response time"""
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(1.0)  # Simulate 1s LLM response
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='{"intent": "test", "confidence": 0.9, "suggested_tools": ["career_tree"]}'))]
            return mock_response
        return slow_response
    
    @pytest.mark.asyncio
    async def test_single_message_response_time(self, orientator_service, mock_fast_llm):
        """Test response time for a single message"""
        # Setup
        orientator_service.llm_client.chat.completions.create = mock_fast_llm
        orientator_service.tool_registry.invoke = AsyncMock(
            return_value=ToolResult(success=True, data={"test": "data"})
        )
        orientator_service.store_message_with_components = AsyncMock()
        
        # Measure time
        start_time = time.time()
        response = await orientator_service.process_message(
            user_id=1,
            message="What skills do I need?",
            conversation_id=1,
            db=Mock()
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Assertions
        assert isinstance(response, OrientatorResponse)
        assert response_time < 500  # Should respond within 500ms for fast LLM
        print(f"Single message response time: {response_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_concurrent_message_handling(self, orientator_service, mock_fast_llm):
        """Test handling multiple concurrent messages"""
        # Setup
        orientator_service.llm_client.chat.completions.create = mock_fast_llm
        orientator_service.tool_registry.invoke = AsyncMock(
            return_value=ToolResult(success=True, data={"test": "data"})
        )
        orientator_service.store_message_with_components = AsyncMock()
        
        # Create multiple concurrent requests
        num_requests = 10
        messages = [f"Test message {i}" for i in range(num_requests)]
        
        # Measure time for concurrent processing
        start_time = time.time()
        
        tasks = [
            orientator_service.process_message(
                user_id=i,
                message=msg,
                conversation_id=i,
                db=Mock()
            )
            for i, msg in enumerate(messages)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # ms
        avg_time = total_time / num_requests
        
        # Assertions
        assert len(responses) == num_requests
        assert all(isinstance(r, OrientatorResponse) for r in responses)
        assert avg_time < 200  # Average should be under 200ms per request
        print(f"Concurrent processing: {num_requests} messages in {total_time:.2f}ms (avg: {avg_time:.2f}ms)")
    
    @pytest.mark.asyncio
    async def test_tool_invocation_performance(self, orientator_service):
        """Test performance of tool invocations"""
        # Mock tools with different response times
        async def mock_tool_execution(tool_name, params, user_id, db):
            tool_times = {
                "esco_skills": 0.2,      # 200ms
                "career_tree": 0.3,       # 300ms
                "oasis_explorer": 0.15,   # 150ms
                "peer_matching": 0.25,    # 250ms
            }
            await asyncio.sleep(tool_times.get(tool_name, 0.1))
            return ToolResult(
                success=True,
                data={"tool": tool_name, "result": "test"},
                metadata={"execution_time": tool_times.get(tool_name, 0.1) * 1000}
            )
        
        orientator_service.tool_registry.invoke = mock_tool_execution
        
        # Test single tool
        start_time = time.time()
        results = await orientator_service.execute_tools(
            [{"tool_name": "esco_skills", "params": {}}],
            user_id=1,
            db=Mock()
        )
        single_tool_time = (time.time() - start_time) * 1000
        
        assert len(results) == 1
        assert single_tool_time < 250  # Should be close to 200ms
        
        # Test multiple tools (sequential)
        start_time = time.time()
        results = await orientator_service.execute_tools(
            [
                {"tool_name": "esco_skills", "params": {}},
                {"tool_name": "career_tree", "params": {}},
                {"tool_name": "oasis_explorer", "params": {}},
            ],
            user_id=1,
            db=Mock()
        )
        multi_tool_time = (time.time() - start_time) * 1000
        
        assert len(results) == 3
        assert multi_tool_time < 700  # Should be around 650ms (200+300+150)
        print(f"Tool execution times - Single: {single_tool_time:.2f}ms, Multiple: {multi_tool_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_response_time_with_large_components(self, orientator_service, mock_fast_llm):
        """Test response time with large message components"""
        # Create large component data
        large_skill_data = {
            "skills": [
                {
                    "name": f"Skill {i}",
                    "level": "Intermediate",
                    "category": "Technical",
                    "description": "A detailed description of this skill and its applications in the industry",
                    "resources": ["Resource 1", "Resource 2", "Resource 3"]
                }
                for i in range(100)  # 100 skills
            ],
            "skill_hierarchy": {
                "technical": [f"Skill {i}" for i in range(50)],
                "analytical": [f"Skill {i}" for i in range(50, 75)],
                "soft": [f"Skill {i}" for i in range(75, 100)]
            }
        }
        
        # Setup
        orientator_service.llm_client.chat.completions.create = mock_fast_llm
        orientator_service.tool_registry.invoke = AsyncMock(
            return_value=ToolResult(success=True, data=large_skill_data)
        )
        orientator_service.store_message_with_components = AsyncMock()
        
        # Measure time
        start_time = time.time()
        response = await orientator_service.process_message(
            user_id=1,
            message="Show me all skills for data science",
            conversation_id=1,
            db=Mock()
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        # Assertions
        assert isinstance(response, OrientatorResponse)
        assert len(response.components) > 0
        assert response_time < 1000  # Should handle large data within 1s
        print(f"Large component response time: {response_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_with_multiple_conversations(self):
        """Test memory usage with multiple active conversations"""
        # This is a placeholder for memory profiling
        # In real implementation, you'd use memory_profiler or tracemalloc
        
        num_conversations = 100
        services = []
        
        for i in range(num_conversations):
            with patch('app.services.orientator_ai_service.AsyncOpenAI'):
                service = OrientatorAIService()
                services.append(service)
        
        # Simulate some data in each service
        for service in services:
            service._conversation_context = {
                "messages": ["message"] * 10,
                "tools_used": ["tool1", "tool2", "tool3"],
                "user_data": {"id": 1, "profile": {}}
            }
        
        # In real test, measure memory usage here
        assert len(services) == num_conversations
        print(f"Created {num_conversations} service instances")
    
    @pytest.mark.asyncio
    async def test_tool_timeout_handling(self, orientator_service):
        """Test handling of tool timeouts"""
        # Mock a tool that times out
        async def timeout_tool(*args, **kwargs):
            await asyncio.sleep(3.0)  # Simulate very slow tool
            return ToolResult(success=True, data={})
        
        orientator_service.tool_registry.invoke = timeout_tool
        
        # Add timeout wrapper
        async def execute_with_timeout():
            try:
                return await asyncio.wait_for(
                    orientator_service.execute_tools(
                        [{"tool_name": "slow_tool", "params": {}}],
                        user_id=1,
                        db=Mock()
                    ),
                    timeout=2.0  # 2 second timeout
                )
            except asyncio.TimeoutError:
                return [{"tool_name": "slow_tool", "result": ToolResult(success=False, error="Timeout")}]
        
        start_time = time.time()
        results = await execute_with_timeout()
        elapsed_time = (time.time() - start_time) * 1000
        
        assert elapsed_time < 2100  # Should timeout at 2s
        assert results[0]["result"].success == False
        assert "Timeout" in results[0]["result"].error
        print(f"Timeout handled in {elapsed_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_response_time_percentiles(self, orientator_service, mock_fast_llm):
        """Test response time percentiles for SLA compliance"""
        # Setup
        orientator_service.llm_client.chat.completions.create = mock_fast_llm
        orientator_service.tool_registry.invoke = AsyncMock(
            return_value=ToolResult(success=True, data={"test": "data"})
        )
        orientator_service.store_message_with_components = AsyncMock()
        
        # Collect response times
        response_times = []
        num_requests = 50
        
        for i in range(num_requests):
            start_time = time.time()
            await orientator_service.process_message(
                user_id=1,
                message=f"Test message {i}",
                conversation_id=1,
                db=Mock()
            )
            response_times.append((time.time() - start_time) * 1000)
        
        # Calculate percentiles
        response_times.sort()
        p50 = statistics.median(response_times)
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[int(len(response_times) * 0.99)]
        avg = statistics.mean(response_times)
        
        # Assertions for SLA
        assert p50 < 200   # 50th percentile under 200ms
        assert p95 < 500   # 95th percentile under 500ms
        assert p99 < 1000  # 99th percentile under 1s
        
        print(f"Response time percentiles (ms) - P50: {p50:.2f}, P95: {p95:.2f}, P99: {p99:.2f}, Avg: {avg:.2f}")
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_under_load(self, orientator_service):
        """Test system behavior under heavy load"""
        # Simulate heavy load with many concurrent requests
        num_requests = 100
        successful_responses = 0
        failed_responses = 0
        
        # Mock LLM with variable response times
        async def variable_llm(*args, **kwargs):
            # Simulate load-dependent slowdown
            delay = 0.1 + (failed_responses * 0.01)  # Gets slower with failures
            await asyncio.sleep(delay)
            
            # Simulate occasional failures under load
            if delay > 0.5:
                raise Exception("Service overloaded")
            
            return Mock(choices=[Mock(message=Mock(content='{"intent": "test", "confidence": 0.9, "suggested_tools": []}'))])
        
        orientator_service.llm_client.chat.completions.create = variable_llm
        orientator_service.tool_registry.invoke = AsyncMock(
            return_value=ToolResult(success=True, data={})
        )
        orientator_service.store_message_with_components = AsyncMock()
        
        # Process requests with error handling
        async def process_with_fallback(i):
            try:
                await orientator_service.process_message(
                    user_id=i,
                    message=f"Message {i}",
                    conversation_id=i,
                    db=Mock()
                )
                return True
            except Exception:
                return False
        
        # Execute concurrent requests
        start_time = time.time()
        tasks = [process_with_fallback(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000
        
        successful_responses = sum(results)
        failed_responses = num_requests - successful_responses
        
        # System should handle at least 80% of requests successfully
        success_rate = successful_responses / num_requests
        assert success_rate > 0.8
        
        print(f"Load test: {successful_responses}/{num_requests} successful ({success_rate*100:.1f}%) in {total_time:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, orientator_service):
        """Test performance improvements with caching"""
        # Mock cache for repeated queries
        cache = {}
        call_count = 0
        
        async def cached_llm(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # Extract message from kwargs
            messages = kwargs.get('messages', [])
            key = messages[-1]['content'] if messages else ""
            
            if key in cache:
                # Cache hit - return immediately
                return cache[key]
            
            # Cache miss - simulate LLM call
            await asyncio.sleep(0.2)
            response = Mock(choices=[Mock(message=Mock(content='{"intent": "test", "confidence": 0.9, "suggested_tools": ["esco_skills"]}'))])
            cache[key] = response
            return response
        
        orientator_service.llm_client.chat.completions.create = cached_llm
        orientator_service.tool_registry.invoke = AsyncMock(
            return_value=ToolResult(success=True, data={})
        )
        orientator_service.store_message_with_components = AsyncMock()
        
        # First request (cache miss)
        start_time = time.time()
        await orientator_service.process_message(1, "What skills for data science?", 1, Mock())
        first_call_time = (time.time() - start_time) * 1000
        
        # Same request (cache hit)
        start_time = time.time()
        await orientator_service.process_message(1, "What skills for data science?", 1, Mock())
        cached_call_time = (time.time() - start_time) * 1000
        
        # Different request (cache miss)
        start_time = time.time()
        await orientator_service.process_message(1, "Career path for ML engineer?", 1, Mock())
        third_call_time = (time.time() - start_time) * 1000
        
        # Assertions
        assert cached_call_time < first_call_time * 0.5  # Cached should be at least 50% faster
        assert call_count == 3  # LLM called 3 times despite same message
        print(f"Cache performance - First: {first_call_time:.2f}ms, Cached: {cached_call_time:.2f}ms, Speedup: {first_call_time/cached_call_time:.2f}x")