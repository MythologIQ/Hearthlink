#!/usr/bin/env python3
"""
SPEC-3 Week 3: Bug Reporting Unit Tests
Comprehensive test suite for bug reporting functionality
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

# Import the modules to test
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from api.bug_reporting import (
    BugReportRequest, BugReportResponse, BugReportStorage,
    router, bug_storage
)

class TestBugReportRequest:
    """Test BugReportRequest model validation"""
    
    def test_valid_bug_report(self):
        """Test valid bug report creation"""
        report = BugReportRequest(
            title="Test Bug",
            description="This is a test bug description",
            category="bug"
        )
        assert report.title == "Test Bug"
        assert report.description == "This is a test bug description"
        assert report.category == "bug"
        assert report.user_role == "user"  # default value
    
    def test_title_validation(self):
        """Test title field validation"""
        # Empty title
        with pytest.raises(ValueError, match="Title is required"):
            BugReportRequest(title="", description="Valid description")
        
        # Whitespace only title
        with pytest.raises(ValueError, match="Title is required"):
            BugReportRequest(title="   ", description="Valid description")
        
        # Too long title
        with pytest.raises(ValueError, match="Title must be 200 characters or less"):
            BugReportRequest(title="x" * 201, description="Valid description")
    
    def test_description_validation(self):
        """Test description field validation"""
        # Empty description
        with pytest.raises(ValueError, match="Description is required"):
            BugReportRequest(title="Valid title", description="")
        
        # Whitespace only description
        with pytest.raises(ValueError, match="Description is required"):
            BugReportRequest(title="Valid title", description="   ")
        
        # Too long description
        with pytest.raises(ValueError, match="Description must be 10,000 characters or less"):
            BugReportRequest(title="Valid title", description="x" * 10001)
    
    def test_category_validation(self):
        """Test category field validation"""
        # Valid categories
        for category in ['bug', 'feature', 'UI', 'performance', 'security']:
            report = BugReportRequest(
                title="Test",
                description="Test description",
                category=category
            )
            assert report.category == category
        
        # Invalid category
        with pytest.raises(ValueError, match="Category must be one of"):
            BugReportRequest(
                title="Test",
                description="Test description",
                category="invalid"
            )
    
    def test_user_role_validation(self):
        """Test user role field validation"""
        # Valid roles
        for role in ['user', 'admin', 'developer', 'tester']:
            report = BugReportRequest(
                title="Test",
                description="Test description",
                user_role=role
            )
            assert report.user_role == role
        
        # Invalid role
        with pytest.raises(ValueError, match="User role must be one of"):
            BugReportRequest(
                title="Test",
                description="Test description",
                user_role="invalid"
            )
        
        # None role defaults to 'user'
        report = BugReportRequest(
            title="Test",
            description="Test description",
            user_role=None
        )
        assert report.user_role == "user"

class TestBugReportStorage:
    """Test BugReportStorage functionality"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing"""
        temp_dir = Path(tempfile.mkdtemp())
        storage = BugReportStorage()
        storage.storage_path = temp_dir / "bug_reports"
        storage.storage_path.mkdir(parents=True, exist_ok=True)
        yield storage
        shutil.rmtree(temp_dir)
    
    def test_generate_bug_id(self, temp_storage):
        """Test bug ID generation"""
        bug_id = temp_storage.generate_bug_id()
        assert bug_id.startswith("BUG_")
        assert len(bug_id) > 10  # Should have timestamp and random suffix
        
        # Should be unique
        bug_id2 = temp_storage.generate_bug_id()
        assert bug_id != bug_id2
    
    @patch('subprocess.run')
    def test_generate_build_hash_with_git(self, mock_run, temp_storage):
        """Test build hash generation with git"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "abc123\n"
        
        build_hash = temp_storage.generate_build_hash()
        assert build_hash == "abc123"
    
    @patch('subprocess.run', side_effect=Exception())
    def test_generate_build_hash_fallback(self, mock_run, temp_storage):
        """Test build hash generation fallback"""
        build_hash = temp_storage.generate_build_hash()
        assert len(build_hash) == 8  # MD5 hash truncated to 8 chars
        assert build_hash.isalnum()
    
    def test_store_bug_report(self, temp_storage):
        """Test bug report storage"""
        report_data = {
            'title': 'Test Bug',
            'description': 'Test description',
            'category': 'bug',
            'user_role': 'user'
        }
        
        bug_id = temp_storage.store_bug_report(report_data)
        
        # Check bug ID format
        assert bug_id.startswith("BUG_")
        
        # Check file was created
        report_file = temp_storage.storage_path / f"{bug_id}.json"
        assert report_file.exists()
        
        # Check file contents
        with open(report_file, 'r') as f:
            stored_data = json.load(f)
        
        assert stored_data['bug_id'] == bug_id
        assert stored_data['title'] == 'Test Bug'
        assert stored_data['description'] == 'Test description'
        assert stored_data['status'] == 'open'
        assert 'created_at' in stored_data
        assert 'build_hash' in stored_data
        assert 'priority' in stored_data
        assert 'tags' in stored_data
        assert 'bug' in stored_data['tags']
        assert 'feedback' in stored_data['tags']
    
    def test_priority_determination(self, temp_storage):
        """Test automatic priority determination"""
        # High priority keywords
        high_priority_data = {
            'title': 'App crashes immediately',
            'description': 'Critical error occurs',
            'category': 'bug'
        }
        bug_id = temp_storage.store_bug_report(high_priority_data)
        report = temp_storage.get_bug_report(bug_id)
        assert report['priority'] == 'high'
        
        # Security category
        security_data = {
            'title': 'Security issue',
            'description': 'Security vulnerability found',
            'category': 'security'
        }
        bug_id = temp_storage.store_bug_report(security_data)
        report = temp_storage.get_bug_report(bug_id)
        assert report['priority'] == 'high'
        
        # Regular bug
        regular_data = {
            'title': 'Minor UI issue',
            'description': 'Button is slightly misaligned',
            'category': 'UI'
        }
        bug_id = temp_storage.store_bug_report(regular_data)
        report = temp_storage.get_bug_report(bug_id)
        assert report['priority'] == 'low'
    
    def test_get_bug_report(self, temp_storage):
        """Test bug report retrieval"""
        # Store a report
        report_data = {
            'title': 'Test Bug',
            'description': 'Test description',
            'category': 'bug'
        }
        bug_id = temp_storage.store_bug_report(report_data)
        
        # Retrieve the report
        retrieved_report = temp_storage.get_bug_report(bug_id)
        assert retrieved_report is not None
        assert retrieved_report['bug_id'] == bug_id
        assert retrieved_report['title'] == 'Test Bug'
        
        # Try to get non-existent report
        non_existent = temp_storage.get_bug_report("BUG_NONEXISTENT")
        assert non_existent is None
    
    def test_list_bug_reports(self, temp_storage):
        """Test bug report listing"""
        # Store multiple reports
        for i in range(5):
            report_data = {
                'title': f'Test Bug {i}',
                'description': f'Test description {i}',
                'category': 'bug'
            }
            temp_storage.store_bug_report(report_data)
        
        # List all reports
        all_reports = temp_storage.list_bug_reports()
        assert len(all_reports) == 5
        
        # List with limit
        limited_reports = temp_storage.list_bug_reports(limit=3)
        assert len(limited_reports) == 3
        
        # Test status filtering (all reports are 'open' by default)
        open_reports = temp_storage.list_bug_reports(status='open')
        assert len(open_reports) == 5
        
        closed_reports = temp_storage.list_bug_reports(status='closed')
        assert len(closed_reports) == 0

class TestBugReportAPI:
    """Test bug reporting API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    @pytest.fixture
    def temp_storage(self):
        """Override storage with temporary directory"""
        temp_dir = Path(tempfile.mkdtemp())
        original_storage_path = bug_storage.storage_path
        bug_storage.storage_path = temp_dir / "bug_reports"
        bug_storage.storage_path.mkdir(parents=True, exist_ok=True)
        yield bug_storage
        bug_storage.storage_path = original_storage_path
        shutil.rmtree(temp_dir)
    
    def test_submit_bug_report_success(self, client, temp_storage):
        """Test successful bug report submission"""
        report_data = {
            'title': 'Test API Bug',
            'description': 'This is a test bug report via API',
            'category': 'bug',
            'user_role': 'user'
        }
        
        response = client.post('/api/bugs', json=report_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert 'bug_id' in result
        assert result['status'] == 'submitted'
        assert 'Reference ID:' in result['message']
        assert 'timestamp' in result
        assert result['bug_id'].startswith('BUG_')
    
    def test_submit_bug_report_validation_error(self, client, temp_storage):
        """Test bug report submission with validation errors"""
        # Missing title
        report_data = {
            'description': 'This is a test bug report',
            'category': 'bug'
        }
        
        response = client.post('/api/bugs', json=report_data)
        assert response.status_code == 422  # Validation error
        
        # Invalid category
        report_data = {
            'title': 'Test Bug',
            'description': 'This is a test bug report',
            'category': 'invalid_category'
        }
        
        response = client.post('/api/bugs', json=report_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_bug_report(self, client, temp_storage):
        """Test bug report retrieval endpoint"""
        # First submit a report
        report_data = {
            'title': 'Test API Bug',
            'description': 'This is a test bug report',
            'category': 'bug'
        }
        
        submit_response = client.post('/api/bugs', json=report_data)
        bug_id = submit_response.json()['bug_id']
        
        # Now retrieve it
        get_response = client.get(f'/api/bugs/{bug_id}')
        assert get_response.status_code == 200
        
        result = get_response.json()
        assert result['bug_id'] == bug_id
        assert result['title'] == 'Test API Bug'
    
    def test_get_nonexistent_bug_report(self, client, temp_storage):
        """Test retrieval of non-existent bug report"""
        response = client.get('/api/bugs/BUG_NONEXISTENT')
        assert response.status_code == 404
    
    def test_list_bug_reports(self, client, temp_storage):
        """Test bug reports listing endpoint"""
        # Submit multiple reports
        for i in range(3):
            report_data = {
                'title': f'Test Bug {i}',
                'description': f'Description {i}',
                'category': 'bug'
            }
            client.post('/api/bugs', json=report_data)
        
        # List all reports
        response = client.get('/api/bugs')
        assert response.status_code == 200
        
        result = response.json()
        assert 'reports' in result
        assert 'count' in result
        assert result['count'] == 3
        assert len(result['reports']) == 3
    
    def test_bug_stats_endpoint(self, client, temp_storage):
        """Test bug statistics endpoint"""
        # Submit reports with different categories
        categories = ['bug', 'feature', 'UI']
        for category in categories:
            report_data = {
                'title': f'Test {category}',
                'description': f'Test {category} description',
                'category': category
            }
            client.post('/api/bugs', json=report_data)
        
        # Get stats
        response = client.get('/api/bugs/stats')
        assert response.status_code == 200
        
        result = response.json()
        assert 'total_reports' in result
        assert 'open_reports' in result
        assert 'categories' in result
        assert 'priorities' in result
        
        assert result['total_reports'] == 3
        assert result['open_reports'] == 3
        assert 'bug' in result['categories']
        assert 'feature' in result['categories']
        assert 'UI' in result['categories']
    
    def test_health_check_endpoint(self, client, temp_storage):
        """Test health check endpoint"""
        response = client.get('/api/bugs/health')
        assert response.status_code == 200
        
        result = response.json()
        assert 'status' in result
        assert 'storage_accessible' in result
        assert 'metrics_available' in result
        assert 'timestamp' in result
        
        assert result['status'] in ['healthy', 'degraded', 'unhealthy']
        assert isinstance(result['storage_accessible'], bool)
        assert isinstance(result['metrics_available'], bool)

class TestMetricsIntegration:
    """Test Prometheus metrics integration"""
    
    @patch('api.bug_reporting.METRICS_AVAILABLE', True)
    @patch('api.bug_reporting.bug_reports_total')
    def test_metrics_increment(self, mock_counter):
        """Test that metrics are incremented on bug report submission"""
        from api.bug_reporting import submit_bug_report
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        report_data = {
            'title': 'Metrics Test Bug',
            'description': 'Testing metrics integration',
            'category': 'bug',
            'user_role': 'developer'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Override storage temporarily
            original_storage_path = bug_storage.storage_path
            bug_storage.storage_path = Path(temp_dir) / "bug_reports"
            bug_storage.storage_path.mkdir(parents=True, exist_ok=True)
            
            try:
                response = client.post('/api/bugs', json=report_data)
                assert response.status_code == 200
                
                # Verify metrics were called
                mock_counter.labels.assert_called_with(
                    category='bug',
                    user_role='developer'
                )
                mock_counter.labels().inc.assert_called_once()
                
            finally:
                bug_storage.storage_path = original_storage_path

if __name__ == '__main__':
    pytest.main([__file__, '-v'])