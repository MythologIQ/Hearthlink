"""
E2E API Smoke Tests - Semantic Pipeline Validation

Comprehensive pytest collection for:
- /api/semantic/retrieve - Context retrieval from Vault
- /api/llm/infer - LLM inference processing  
- /api/semantic/store - Memory persistence

Tests the complete pipeline: retrieve → infer → store with real services
"""

import pytest
import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Test configuration
API_BASE_URL = "http://localhost:8002"
PERFORMANCE_THRESHOLD_MS = 500
REQUEST_TIMEOUT_S = 10
TEST_USER_ID = "e2e-test-user"


class E2EAPITestSuite:
    """Comprehensive API test suite for semantic pipeline validation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._get_test_token()}',
            'User-Agent': 'HearthlinkE2E/1.0'
        })
        self.test_results = []
        self.start_time = time.time()
    
    def _get_test_token(self) -> str:
        """Get authentication token for testing"""
        return "e2e-test-token-12345"  # Use environment variable in production
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with timing and error handling"""
        start_time = time.time()
        
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = self.session.request(method, url, timeout=REQUEST_TIMEOUT_S, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'latency_ms': latency_ms,
                'headers': dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'error': str(e),
                'latency_ms': latency_ms,
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0
            }
    
    def _record_result(self, test_name: str, passed: bool, latency_ms: int, details: str = ""):
        """Record test result for reporting"""
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'latency_ms': latency_ms,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {latency_ms}ms")
        if details and not passed:
            print(f"   Details: {details}")


@pytest.fixture(scope="session")
def api_suite():
    """Create API test suite instance"""
    return E2EAPITestSuite()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(api_suite):
    """Set up test environment and cleanup after all tests"""
    # Pre-test setup
    print("🚀 Starting E2E API Pipeline Tests")
    
    # Seed test data
    seed_response = api_suite._make_request('POST', '/api/test/seed', json={
        'seed': '12345',
        'user_id': TEST_USER_ID
    })
    
    if not seed_response['success']:
        print("⚠️ Warning: Failed to seed test data")
    
    yield
    
    # Post-test cleanup
    print("🧹 Cleaning up test environment")
    cleanup_response = api_suite._make_request('POST', '/api/test/cleanup', json={
        'user_id': TEST_USER_ID,
        'preserve_metrics': True
    })
    
    # Generate final report
    _generate_final_report(api_suite)


def _generate_final_report(api_suite: E2EAPITestSuite):
    """Generate comprehensive test report"""
    total_tests = len(api_suite.test_results)
    passed_tests = sum(1 for r in api_suite.test_results if r['passed'])
    
    if total_tests == 0:
        return
    
    avg_latency = sum(r['latency_ms'] for r in api_suite.test_results) / total_tests
    max_latency = max(r['latency_ms'] for r in api_suite.test_results)
    performance_violations = sum(1 for r in api_suite.test_results if r['latency_ms'] > PERFORMANCE_THRESHOLD_MS)
    
    report = {
        'summary': {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'pass_rate': f"{(passed_tests / total_tests * 100):.1f}%",
            'avg_latency_ms': int(avg_latency),
            'max_latency_ms': max_latency,
            'performance_violations': performance_violations,
            'execution_time_s': int(time.time() - api_suite.start_time)
        },
        'detailed_results': api_suite.test_results
    }
    
    # Save report
    with open('tests/e2e/reports/api-smoke-test-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("🎯 E2E API SMOKE TEST SUMMARY")
    print('='*60)
    print(f"📊 Tests: {total_tests} total, {passed_tests} passed, {total_tests - passed_tests} failed")
    print(f"📈 Pass Rate: {report['summary']['pass_rate']}")
    print(f"⏱️  Average Latency: {report['summary']['avg_latency_ms']}ms")
    print(f"🚀 Max Latency: {report['summary']['max_latency_ms']}ms")
    print(f"⚡ Performance Violations: {performance_violations}/{total_tests}")
    print('='*60)


class TestSemanticRetrieve:
    """Test suite for /api/semantic/retrieve endpoint"""
    
    def test_basic_context_retrieval(self, api_suite):
        """Test basic context retrieval functionality"""
        test_query = "What is machine learning?"
        
        response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': test_query,
            'user_id': TEST_USER_ID,
            'max_results': 5,
            'similarity_threshold': 0.7
        })
        
        passed = (
            response['success'] and
            response['status_code'] == 200 and
            'results' in response['data'] and
            response['latency_ms'] < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"Status: {response['status_code']}, Results: {len(response['data'].get('results', []))}"
        api_suite._record_result('Basic Context Retrieval', passed, response['latency_ms'], details)
        
        assert passed, f"Context retrieval failed: {details}"
    
    def test_empty_query_handling(self, api_suite):
        """Test handling of empty queries"""
        response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': '',
            'user_id': TEST_USER_ID
        })
        
        passed = (
            response['success'] is False or
            (response['success'] and response['status_code'] == 400) or
            (response['success'] and len(response['data'].get('results', [])) == 0)
        )
        
        details = f"Status: {response['status_code']}, Empty query handled gracefully"
        api_suite._record_result('Empty Query Handling', passed, response['latency_ms'], details)
        
        assert passed, "Empty query not handled properly"
    
    def test_user_specific_retrieval(self, api_suite):
        """Test user-specific context retrieval"""
        # First, store some user-specific context
        store_response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': 'User-specific information about quantum computing preferences',
            'user_id': TEST_USER_ID,
            'metadata': {'type': 'user_preference', 'topic': 'quantum_computing'}
        })
        
        time.sleep(1)  # Allow for indexing
        
        # Then retrieve it
        retrieve_response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': 'quantum computing preferences',
            'user_id': TEST_USER_ID,
            'max_results': 10
        })
        
        passed = (
            store_response['success'] and
            retrieve_response['success'] and
            retrieve_response['status_code'] == 200 and
            len(retrieve_response['data'].get('results', [])) > 0 and
            retrieve_response['latency_ms'] < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"Store: {store_response['status_code']}, Retrieve: {retrieve_response['status_code']}"
        api_suite._record_result('User-Specific Retrieval', passed, retrieve_response['latency_ms'], details)
        
        assert passed, f"User-specific retrieval failed: {details}"
    
    def test_similarity_threshold_filtering(self, api_suite):
        """Test similarity threshold filtering"""
        # Test with high threshold (should return fewer results)
        high_threshold_response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': 'artificial intelligence concepts',
            'user_id': TEST_USER_ID,
            'similarity_threshold': 0.9,
            'max_results': 10
        })
        
        # Test with low threshold (should return more results)
        low_threshold_response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': 'artificial intelligence concepts',
            'user_id': TEST_USER_ID,
            'similarity_threshold': 0.3,
            'max_results': 10
        })
        
        high_results = len(high_threshold_response['data'].get('results', []))
        low_results = len(low_threshold_response['data'].get('results', []))
        
        passed = (
            high_threshold_response['success'] and
            low_threshold_response['success'] and
            low_results >= high_results  # Low threshold should return >= results
        )
        
        details = f"High threshold: {high_results} results, Low threshold: {low_results} results"
        avg_latency = (high_threshold_response['latency_ms'] + low_threshold_response['latency_ms']) // 2
        api_suite._record_result('Similarity Threshold Filtering', passed, avg_latency, details)
        
        assert passed, f"Similarity threshold filtering failed: {details}"


class TestLLMInfer:
    """Test suite for /api/llm/infer endpoint"""
    
    def test_basic_inference(self, api_suite):
        """Test basic LLM inference functionality"""
        response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': 'What is the capital of France?',
            'user_id': TEST_USER_ID,
            'context': ['France is a country in Europe', 'Paris is a major city in France'],
            'agent': 'alden'
        })
        
        passed = (
            response['success'] and
            response['status_code'] == 200 and
            'response' in response['data'] and
            len(response['data']['response']) > 0 and
            response['latency_ms'] < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"Status: {response['status_code']}, Response length: {len(response['data'].get('response', ''))}"
        api_suite._record_result('Basic LLM Inference', passed, response['latency_ms'], details)
        
        assert passed, f"LLM inference failed: {details}"
    
    def test_context_aware_inference(self, api_suite):
        """Test context-aware inference"""
        context = [
            'The user is planning a trip to Japan',
            'They are interested in cultural experiences',
            'Budget is approximately $3000'
        ]
        
        response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': 'What would you recommend for my trip?',
            'user_id': TEST_USER_ID,
            'context': context,
            'agent': 'alden',
            'max_tokens': 200
        })
        
        inference_text = response['data'].get('response', '').lower()
        contextual_response = (
            'japan' in inference_text or
            'cultural' in inference_text or
            'trip' in inference_text or
            'budget' in inference_text
        )
        
        passed = (
            response['success'] and
            response['status_code'] == 200 and
            contextual_response and
            response['latency_ms'] < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"Contextual response: {contextual_response}, Length: {len(inference_text)}"
        api_suite._record_result('Context-Aware Inference', passed, response['latency_ms'], details)
        
        assert passed, f"Context-aware inference failed: {details}"
    
    def test_agent_specific_inference(self, api_suite):
        """Test agent-specific inference behavior"""
        security_prompt = "Analyze potential security vulnerabilities in the system"
        
        # Test with Sentry agent (should provide security-focused response)
        sentry_response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': security_prompt,
            'user_id': TEST_USER_ID,
            'agent': 'sentry',
            'context': ['System has multiple MCP servers', 'Authentication is token-based']
        })
        
        # Test with Alden agent (should provide more general response)
        alden_response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': security_prompt,
            'user_id': TEST_USER_ID,
            'agent': 'alden',
            'context': ['System has multiple MCP servers', 'Authentication is token-based']
        })
        
        sentry_text = sentry_response['data'].get('response', '').lower()
        alden_text = alden_response['data'].get('response', '').lower()
        
        # Sentry should be more security-focused
        sentry_security_focused = any(term in sentry_text for term in 
                                    ['vulnerability', 'security', 'threat', 'risk', 'authentication'])
        
        passed = (
            sentry_response['success'] and
            alden_response['success'] and
            sentry_security_focused and
            max(sentry_response['latency_ms'], alden_response['latency_ms']) < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"Sentry security focus: {sentry_security_focused}"
        avg_latency = (sentry_response['latency_ms'] + alden_response['latency_ms']) // 2
        api_suite._record_result('Agent-Specific Inference', passed, avg_latency, details)
        
        assert passed, f"Agent-specific inference failed: {details}"
    
    def test_inference_with_memory(self, api_suite):
        """Test inference with conversation memory"""
        # First message
        first_response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': 'I am learning Python programming',
            'user_id': TEST_USER_ID,
            'agent': 'alden',
            'conversation_id': f'test-conv-{uuid.uuid4()}'
        })
        
        time.sleep(0.5)  # Brief pause
        
        # Follow-up message (should reference previous context)
        second_response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': 'What are some good resources for it?',
            'user_id': TEST_USER_ID,
            'agent': 'alden',
            'conversation_id': first_response['data'].get('conversation_id')
        })
        
        second_text = second_response['data'].get('response', '').lower()
        references_python = 'python' in second_text or 'programming' in second_text
        
        passed = (
            first_response['success'] and
            second_response['success'] and
            references_python and
            second_response['latency_ms'] < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"References Python: {references_python}"
        api_suite._record_result('Inference with Memory', passed, second_response['latency_ms'], details)
        
        assert passed, f"Inference with memory failed: {details}"


class TestSemanticStore:
    """Test suite for /api/semantic/store endpoint"""
    
    def test_basic_memory_storage(self, api_suite):
        """Test basic memory storage functionality"""
        test_content = f"Test memory content - {uuid.uuid4()}"
        
        response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': test_content,
            'user_id': TEST_USER_ID,
            'metadata': {
                'type': 'test_memory',
                'timestamp': datetime.now().isoformat()
            }
        })
        
        passed = (
            response['success'] and
            response['status_code'] == 200 and
            'memory_id' in response['data'] and
            response['latency_ms'] < PERFORMANCE_THRESHOLD_MS
        )
        
        details = f"Status: {response['status_code']}, Memory ID: {response['data'].get('memory_id', 'None')}"
        api_suite._record_result('Basic Memory Storage', passed, response['latency_ms'], details)
        
        assert passed, f"Memory storage failed: {details}"
    
    def test_conversation_storage(self, api_suite):
        """Test conversation storage"""
        conversation_id = f'test-conv-{uuid.uuid4()}'
        
        response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': 'User asked about artificial intelligence, I explained basic concepts',
            'user_id': TEST_USER_ID,
            'conversation_id': conversation_id,
            'metadata': {
                'type': 'conversation_turn',
                'user_message': 'What is AI?',
                'assistant_message': 'AI stands for Artificial Intelligence...'
            }
        })
        
        passed = (
            response['success'] and
            response['status_code'] == 200 and
            'memory_id' in response['data'] and
            response['data'].get('conversation_id') == conversation_id
        )
        
        details = f"Conversation ID: {conversation_id[:8]}..."
        api_suite._record_result('Conversation Storage', passed, response['latency_ms'], details)
        
        assert passed, f"Conversation storage failed: {details}"
    
    def test_memory_metadata_enrichment(self, api_suite):
        """Test memory storage with rich metadata"""
        rich_metadata = {
            'type': 'user_preference',
            'category': 'technical',
            'topics': ['machine learning', 'data science'],
            'confidence': 0.95,
            'source': 'direct_user_input',
            'timestamp': datetime.now().isoformat()
        }
        
        response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': 'User prefers machine learning explanations with practical examples',
            'user_id': TEST_USER_ID,
            'metadata': rich_metadata
        })
        
        passed = (
            response['success'] and
            response['status_code'] == 200 and
            'memory_id' in response['data'] and
            response['data'].get('metadata_processed') is True
        )
        
        details = f"Metadata fields: {len(rich_metadata)}"
        api_suite._record_result('Memory Metadata Enrichment', passed, response['latency_ms'], details)
        
        assert passed, f"Memory metadata enrichment failed: {details}"
    
    def test_duplicate_memory_handling(self, api_suite):
        """Test handling of duplicate memory content"""
        duplicate_content = f"Duplicate test content - {uuid.uuid4()}"
        
        # Store first instance
        first_response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': duplicate_content,
            'user_id': TEST_USER_ID,
            'metadata': {'type': 'duplicate_test'}
        })
        
        time.sleep(0.5)  # Brief pause
        
        # Store duplicate
        second_response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': duplicate_content,
            'user_id': TEST_USER_ID,
            'metadata': {'type': 'duplicate_test'}
        })
        
        # System should either reject duplicate or merge it intelligently
        passed = (
            first_response['success'] and
            second_response['success'] and
            (
                second_response['data'].get('is_duplicate') is True or
                second_response['data'].get('merged_with_existing') is True or
                first_response['data']['memory_id'] != second_response['data']['memory_id']
            )
        )
        
        details = f"First: {first_response['data'].get('memory_id', 'None')[:8]}, Second: {second_response['data'].get('memory_id', 'None')[:8]}"
        avg_latency = (first_response['latency_ms'] + second_response['latency_ms']) // 2
        api_suite._record_result('Duplicate Memory Handling', passed, avg_latency, details)
        
        assert passed, f"Duplicate memory handling failed: {details}"


class TestPipelineIntegration:
    """Test suite for complete retrieve → infer → store pipeline"""
    
    def test_complete_pipeline_flow(self, api_suite):
        """Test complete pipeline: retrieve → infer → store"""
        pipeline_start = time.time()
        
        # Step 1: Retrieve context
        retrieve_response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': 'machine learning algorithms',
            'user_id': TEST_USER_ID,
            'max_results': 3
        })
        
        context = [result['content'] for result in retrieve_response['data'].get('results', [])]
        
        # Step 2: Infer with retrieved context
        infer_response = api_suite._make_request('POST', '/api/llm/infer', json={
            'prompt': 'Explain the benefits of ensemble methods',
            'user_id': TEST_USER_ID,
            'context': context,
            'agent': 'alden'
        })
        
        # Step 3: Store the conversation
        store_response = api_suite._make_request('POST', '/api/semantic/store', json={
            'content': f"User asked about ensemble methods. Context retrieved: {len(context)} items. Response: {infer_response['data'].get('response', '')[:100]}...",
            'user_id': TEST_USER_ID,
            'metadata': {
                'type': 'qa_interaction',
                'pipeline_test': True,
                'context_items': len(context)
            }
        })
        
        total_latency = int((time.time() - pipeline_start) * 1000)
        
        passed = (
            retrieve_response['success'] and
            infer_response['success'] and
            store_response['success'] and
            total_latency < (PERFORMANCE_THRESHOLD_MS * 3)  # Allow 3x threshold for full pipeline
        )
        
        details = f"Retrieve: {retrieve_response['latency_ms']}ms, Infer: {infer_response['latency_ms']}ms, Store: {store_response['latency_ms']}ms"
        api_suite._record_result('Complete Pipeline Flow', passed, total_latency, details)
        
        assert passed, f"Complete pipeline flow failed: {details}"
    
    def test_pipeline_error_resilience(self, api_suite):
        """Test pipeline behavior with partial failures"""
        # Test with invalid user_id to trigger potential errors
        invalid_user_id = "invalid-user-12345"
        
        retrieve_response = api_suite._make_request('POST', '/api/semantic/retrieve', json={
            'query': 'test query',
            'user_id': invalid_user_id
        })
        
        # Even with invalid user, system should handle gracefully
        graceful_handling = (
            retrieve_response['success'] is False or
            (retrieve_response['success'] and len(retrieve_response['data'].get('results', [])) == 0)
        )
        
        api_suite._record_result('Pipeline Error Resilience', graceful_handling, retrieve_response['latency_ms'])
        
        assert graceful_handling, "Pipeline error resilience failed"
    
    def test_concurrent_pipeline_operations(self, api_suite):
        """Test concurrent pipeline operations"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def pipeline_worker(worker_id):
            try:
                # Quick pipeline operation
                retrieve_resp = api_suite._make_request('POST', '/api/semantic/retrieve', json={
                    'query': f'concurrent test {worker_id}',
                    'user_id': f'{TEST_USER_ID}-{worker_id}',
                    'max_results': 2
                })
                
                infer_resp = api_suite._make_request('POST', '/api/llm/infer', json={
                    'prompt': f'Test prompt {worker_id}',
                    'user_id': f'{TEST_USER_ID}-{worker_id}',
                    'agent': 'alden'
                })
                
                results_queue.put({
                    'worker_id': worker_id,
                    'success': retrieve_resp['success'] and infer_resp['success'],
                    'total_latency': retrieve_resp['latency_ms'] + infer_resp['latency_ms']
                })
            except Exception as e:
                results_queue.put({'worker_id': worker_id, 'success': False, 'error': str(e)})
        
        # Launch concurrent workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=pipeline_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful_workers = sum(1 for r in results if r.get('success', False))
        avg_latency = sum(r.get('total_latency', 0) for r in results) // len(results) if results else 0
        
        passed = successful_workers >= 2  # At least 2 out of 3 should succeed
        
        details = f"Successful workers: {successful_workers}/3"
        api_suite._record_result('Concurrent Pipeline Operations', passed, avg_latency, details)
        
        assert passed, f"Concurrent pipeline operations failed: {details}"


# Pytest configuration and fixtures
def pytest_configure(config):
    """Configure pytest for API testing"""
    # Ensure reports directory exists
    import os
    os.makedirs('tests/e2e/reports', exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add custom markers"""
    for item in items:
        # Add performance marker to tests that check latency
        if 'latency' in item.name.lower() or 'performance' in item.name.lower():
            item.add_marker(pytest.mark.performance)
        
        # Add integration marker to pipeline tests  
        if 'pipeline' in item.name.lower() or 'integration' in item.name.lower():
            item.add_marker(pytest.mark.integration)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, '-v', '--tb=short'])