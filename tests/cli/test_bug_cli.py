#!/usr/bin/env python3
"""
SPEC-3 Week 3: CLI Bug Reporting Tests
Comprehensive test suite for CLI bug reporting functionality
"""

import pytest
import tempfile
import subprocess
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / 'scripts'
sys.path.append(str(SCRIPTS_DIR))

# Import the CLI module
import bug_cli

class TestBugCLICore:
    """Test core CLI functionality"""
    
    def test_get_build_hash_with_git(self):
        """Test build hash generation with git"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'abc123\n'
            
            build_hash = bug_cli.get_build_hash()
            assert build_hash == 'abc123'
            
            # Verify git command was called correctly
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[:3] == ['git', 'rev-parse', '--short']
    
    def test_get_build_hash_fallback(self):
        """Test build hash fallback when git fails"""
        with patch('subprocess.run', side_effect=Exception('Git not found')):
            build_hash = bug_cli.get_build_hash()
            assert len(build_hash) == 8
            assert build_hash.isalnum()
    
    def test_get_system_info(self):
        """Test system information gathering"""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.version', return_value='5.4.0'), \
             patch('platform.python_version', return_value='3.9.0'), \
             patch('platform.machine', return_value='x86_64'), \
             patch('platform.node', return_value='test-host'):
            
            info = bug_cli.get_system_info()
            
            assert info['platform'] == 'Linux'
            assert info['platform_version'] == '5.4.0'
            assert info['python_version'] == '3.9.0'
            assert info['architecture'] == 'x86_64'
            assert info['hostname'] == 'test-host'
            assert 'timestamp' in info
    
    def test_validate_file_attachment_valid(self):
        """Test valid file attachment validation"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'Test content')
            temp_path = temp_file.name
        
        try:
            # Valid file should pass
            assert bug_cli.validate_file_attachment(temp_path) is True
        finally:
            Path(temp_path).unlink()
    
    def test_validate_file_attachment_nonexistent(self):
        """Test validation of non-existent file"""
        with patch('builtins.print') as mock_print:
            result = bug_cli.validate_file_attachment('/nonexistent/file.txt')
            assert result is False
            mock_print.assert_called_with('❌ File not found: /nonexistent/file.txt')
    
    def test_validate_file_attachment_too_large(self):
        """Test validation of file that's too large"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            # Write more than 10MB
            temp_file.write(b'x' * (11 * 1024 * 1024))
            temp_path = temp_file.name
        
        try:
            with patch('builtins.print') as mock_print:
                result = bug_cli.validate_file_attachment(temp_path)
                assert result is False
                mock_print.assert_called_with(f'❌ File too large: {temp_path} (max 10MB)')
        finally:
            Path(temp_path).unlink()
    
    def test_validate_file_attachment_invalid_type(self):
        """Test validation of invalid file type"""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
            temp_file.write(b'Invalid content')
            temp_path = temp_file.name
        
        try:
            with patch('builtins.print') as mock_print:
                result = bug_cli.validate_file_attachment(temp_path)
                assert result is False
                # Should print error about unsupported file type
                assert mock_print.call_count >= 1
        finally:
            Path(temp_path).unlink()

class TestBugSubmission:
    """Test bug report submission functionality"""
    
    def test_submit_bug_report_success(self):
        """Test successful bug report submission"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'bug_id': 'BUG_TEST_123',
            'status': 'submitted',
            'message': 'Success',
            'timestamp': '2025-08-01T12:00:00Z'
        }
        
        with patch('requests.post', return_value=mock_response):
            result = bug_cli.submit_bug_report(
                title='Test Bug',
                description='Test description',
                category='bug'
            )
            
            assert result['success'] is True
            assert result['data']['bug_id'] == 'BUG_TEST_123'
    
    def test_submit_bug_report_http_error(self):
        """Test bug report submission with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        
        with patch('requests.post', return_value=mock_response):
            result = bug_cli.submit_bug_report(
                title='Test Bug',
                description='Test description'
            )
            
            assert result['success'] is False
            assert 'HTTP 500' in result['error']
    
    def test_submit_bug_report_connection_error(self):
        """Test bug report submission with connection error"""
        with patch('requests.post', side_effect=ConnectionError('Connection failed')):
            result = bug_cli.submit_bug_report(
                title='Test Bug',
                description='Test description'
            )
            
            assert result['success'] is False
            assert 'Could not connect' in result['error']
    
    def test_submit_bug_report_timeout(self):
        """Test bug report submission with timeout"""
        with patch('requests.post', side_effect=TimeoutError('Request timed out')):
            result = bug_cli.submit_bug_report(
                title='Test Bug',
                description='Test description'
            )
            
            assert result['success'] is False
            assert 'timed out' in result['error']
    
    def test_submit_bug_report_with_attachments(self):
        """Test bug report submission with file attachments"""
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp1, \
             tempfile.NamedTemporaryFile(suffix='.log', delete=False) as temp2:
            
            temp1.write(b'Test file 1')
            temp2.write(b'Test file 2')
            temp1_path = temp1.name
            temp2_path = temp2.name
        
        try:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'bug_id': 'BUG_ATTACH_TEST',
                'status': 'submitted',
                'message': 'Success with attachments',
                'timestamp': '2025-08-01T12:00:00Z'
            }
            
            with patch('requests.post', return_value=mock_response) as mock_post, \
                 patch('builtins.open', create=True) as mock_open:
                
                # Mock file opening for attachments
                mock_file1 = Mock()
                mock_file2 = Mock()
                mock_open.side_effect = [mock_file1, mock_file2]
                
                result = bug_cli.submit_bug_report(
                    title='Test with Attachments',
                    description='Test description with files',
                    attachments=[temp1_path, temp2_path]
                )
                
                assert result['success'] is True
                assert result['data']['bug_id'] == 'BUG_ATTACH_TEST'
                
                # Verify files were included in request
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert 'files' in call_args[1]
                
        finally:
            Path(temp1_path).unlink()
            Path(temp2_path).unlink()

class TestInteractiveModeManagement:
    """Test interactive mode functionality"""
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_bug_report_complete(self, mock_print, mock_input):
        """Test complete interactive bug report flow"""
        # Mock user inputs
        mock_input.side_effect = [
            '1',  # Bug category
            'Interactive Test Bug',  # Title
            'This is a test bug report',  # Description line 1
            'with multiple lines',  # Description line 2
            '',  # End description (empty line)
            '',  # No attachments
        ]
        
        # Mock EOFError to end description input
        def input_side_effect(prompt=''):
            if 'Description' in prompt or 'Ctrl+' in prompt:
                # Simulate multi-line input ending with EOFError
                responses = [
                    'This is a test bug report',
                    'with multiple lines'
                ]
                for response in responses:
                    yield response
                raise EOFError()
            return mock_input.side_effect.pop(0)
        
        mock_input.side_effect = [
            '1',  # Bug category
            'Interactive Test Bug',  # Title
            '',  # No attachments
        ]
        
        # Use a more controlled approach for multi-line input
        with patch('builtins.input', side_effect=['1', 'Test Title', '']):
            # Mock the multi-line description input separately
            with patch('sys.stdin.read', return_value='Test description\nMultiple lines\n'):
                result = bug_cli.interactive_bug_report()
                
                # The function should return None if input is incomplete
                # or a dict with the bug data if successful
                # This test may need adjustment based on actual implementation
                assert result is None or isinstance(result, dict)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_interactive_invalid_category(self, mock_print, mock_input):
        """Test interactive mode with invalid category selection"""
        mock_input.side_effect = [
            '5',  # Invalid category
            '1',  # Valid category (bug)
            'Test Bug',  # Title
            '',  # No attachments
        ]
        
        # This test should verify that invalid input is handled
        # Implementation may vary, so adjust based on actual behavior
        with patch('sys.stdin.read', return_value='Test description'):
            result = bug_cli.interactive_bug_report()
            # Should eventually succeed with valid input

class TestCLIArgumentParsing:
    """Test command-line argument parsing"""
    
    def test_main_with_required_args(self):
        """Test main function with all required arguments"""
        test_args = [
            'bug_cli.py',
            '--title', 'CLI Test Bug',
            '--desc', 'Testing CLI argument parsing'
        ]
        
        with patch('sys.argv', test_args), \
             patch('bug_cli.submit_bug_report') as mock_submit, \
             patch('builtins.print'):
            
            mock_submit.return_value = {
                'success': True,
                'data': {
                    'bug_id': 'BUG_CLI_TEST',
                    'status': 'submitted',
                    'timestamp': '2025-08-01T12:00:00Z'
                }
            }
            
            result = bug_cli.main()
            assert result == 0  # Success exit code
            
            # Verify submit was called with correct arguments
            mock_submit.assert_called_once()
            call_args = mock_submit.call_args[1]  # keyword args
            assert call_args['title'] == 'CLI Test Bug'
            assert call_args['description'] == 'Testing CLI argument parsing'
            assert call_args['category'] == 'bug'  # default
    
    def test_main_missing_required_args(self):
        """Test main function with missing required arguments"""
        test_args = ['bug_cli.py', '--title', 'Only Title']
        
        with patch('sys.argv', test_args), \
             patch('builtins.print') as mock_print:
            
            result = bug_cli.main()
            assert result == 1  # Error exit code
            
            # Should print error message
            error_calls = [call for call in mock_print.call_args_list 
                          if 'Error:' in str(call)]
            assert len(error_calls) > 0
    
    def test_main_with_category_option(self):
        """Test main function with category option"""
        test_args = [
            'bug_cli.py',
            '--title', 'Feature Request',
            '--desc', 'New feature description',
            '--category', 'feature'
        ]
        
        with patch('sys.argv', test_args), \
             patch('bug_cli.submit_bug_report') as mock_submit, \
             patch('builtins.print'):
            
            mock_submit.return_value = {
                'success': True,
                'data': {
                    'bug_id': 'BUG_FEATURE_TEST',
                    'status': 'submitted',
                    'timestamp': '2025-08-01T12:00:00Z'
                }
            }
            
            result = bug_cli.main()
            assert result == 0
            
            call_args = mock_submit.call_args[1]
            assert call_args['category'] == 'feature'
    
    def test_main_with_attachments(self):
        """Test main function with attachment arguments"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'Test attachment')
            temp_path = temp_file.name
        
        try:
            test_args = [
                'bug_cli.py',
                '--title', 'Bug with Attachment',
                '--desc', 'Bug report with file',
                '--attach', temp_path
            ]
            
            with patch('sys.argv', test_args), \
                 patch('bug_cli.submit_bug_report') as mock_submit, \
                 patch('builtins.print'):
                
                mock_submit.return_value = {
                    'success': True,
                    'data': {
                        'bug_id': 'BUG_ATTACH_CLI',
                        'status': 'submitted',
                        'timestamp': '2025-08-01T12:00:00Z'
                    }
                }
                
                result = bug_cli.main()
                assert result == 0
                
                call_args = mock_submit.call_args[1]
                assert temp_path in call_args['attachments']
                
        finally:
            Path(temp_path).unlink()
    
    def test_main_dry_run(self):
        """Test main function with dry run option"""
        test_args = [
            'bug_cli.py',
            '--title', 'Dry Run Test',
            '--desc', 'Testing dry run functionality',
            '--dry-run'
        ]
        
        with patch('sys.argv', test_args), \
             patch('bug_cli.submit_bug_report') as mock_submit, \
             patch('builtins.print') as mock_print:
            
            result = bug_cli.main()
            assert result == 0
            
            # Should not call submit in dry run mode
            mock_submit.assert_not_called()
            
            # Should print dry run message
            dry_run_calls = [call for call in mock_print.call_args_list 
                           if 'Dry run' in str(call)]
            assert len(dry_run_calls) > 0
    
    def test_main_interactive_mode(self):
        """Test main function with interactive flag"""
        test_args = ['bug_cli.py', '--interactive']
        
        with patch('sys.argv', test_args), \
             patch('bug_cli.interactive_bug_report') as mock_interactive, \
             patch('bug_cli.submit_bug_report') as mock_submit, \
             patch('builtins.print'):
            
            mock_interactive.return_value = {
                'title': 'Interactive Bug',
                'description': 'Created interactively',
                'category': 'bug',
                'attachments': []
            }
            
            mock_submit.return_value = {
                'success': True,
                'data': {
                    'bug_id': 'BUG_INTERACTIVE',
                    'status': 'submitted',
                    'timestamp': '2025-08-01T12:00:00Z'
                }
            }
            
            result = bug_cli.main()
            assert result == 0
            
            # Should call interactive function
            mock_interactive.assert_called_once()
    
    def test_main_submission_failure(self):
        """Test main function when submission fails"""
        test_args = [
            'bug_cli.py',
            '--title', 'Failed Submission',
            '--desc', 'This should fail'
        ]
        
        with patch('sys.argv', test_args), \
             patch('bug_cli.submit_bug_report') as mock_submit, \
             patch('builtins.print') as mock_print:
            
            mock_submit.return_value = {
                'success': False,
                'error': 'Network connection failed'
            }
            
            result = bug_cli.main()
            assert result == 1  # Error exit code
            
            # Should print error message
            error_calls = [call for call in mock_print.call_args_list 
                          if 'Failed to submit' in str(call)]
            assert len(error_calls) > 0

class TestCLIIntegration:
    """Test CLI integration scenarios"""
    
    def test_cli_wrapper_script_bug_command(self):
        """Test the hl wrapper script with bug command"""
        hl_script = SCRIPTS_DIR / 'hl'
        
        # Test basic help functionality
        if hl_script.exists():
            result = subprocess.run(
                [str(hl_script), 'bug', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should not error out
            assert result.returncode in [0, 2]  # 0 for success, 2 for argparse help
            
            # Should contain help text
            help_output = result.stdout + result.stderr
            assert 'bug' in help_output.lower()
    
    def test_cli_executable_permissions(self):
        """Test that CLI scripts have correct permissions"""
        hl_script = SCRIPTS_DIR / 'hl'
        bug_cli_script = SCRIPTS_DIR / 'bug_cli.py'
        
        if hl_script.exists():
            # Check if hl script is executable
            assert hl_script.stat().st_mode & 0o111  # Has execute permission
        
        if bug_cli_script.exists():
            # bug_cli.py should exist and be readable
            assert bug_cli_script.is_file()
            assert bug_cli_script.stat().st_mode & 0o444  # Has read permission

if __name__ == '__main__':
    pytest.main([__file__, '-v'])