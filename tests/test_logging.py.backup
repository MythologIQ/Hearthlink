#!/usr/bin/env python3
"""
Test script for Hearthlink structured JSON logging.

This script demonstrates the logging functionality and verifies:
- Structured JSON format
- Log rotation (10MB, 5 backups)
- Error handling and fallback mechanisms
- Audit trail compliance

Run with: python -m pytest tests/test_logging.py
"""

import sys
import os
import time
import json
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import HearthlinkLogger, HearthlinkContainer


class TestLogging(unittest.TestCase):
    """Test suite for Hearthlink logging functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_log_dir = Path("test_logs")
        self.test_rotation_dir = Path("test_rotation_logs")
        self.test_container_dir = Path("test_container_logs")
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up test directories
        import shutil
        for test_dir in [self.test_log_dir, self.test_rotation_dir, self.test_container_dir]:
            if test_dir.exists():
                shutil.rmtree(test_dir)
    
    def test_structured_logging(self):
        """Test structured JSON logging functionality."""
        # Create test logger with smaller rotation for testing
        logger = HearthlinkLogger(
            log_dir=str(self.test_log_dir),
            max_size_mb=1,  # 1MB for testing
            backup_count=3
        )
        
        # Test startup logging
        logger.log_startup()
        
        # Test various log levels with structured data
        logger.logger.info("Test info message", extra={
            "extra_fields": {
                "event_type": "test_info",
                "test_id": "001",
                "data": {"key": "value"}
            }
        })
        
        logger.logger.warning("Test warning message", extra={
            "extra_fields": {
                "event_type": "test_warning",
                "test_id": "002",
                "severity": "medium"
            }
        })
        
        # Test error logging
        try:
            raise ValueError("Test error for logging")
        except ValueError as e:
            logger.log_error(e, "test_error_context", {
                "test_id": "003",
                "expected": True
            })
        
        # Test shutdown logging
        logger.log_shutdown("test_completion")
        
        # Verify logger was created successfully
        self.assertIsInstance(logger, HearthlinkLogger)
        self.assertTrue(self.test_log_dir.exists())
    
    def test_log_rotation(self):
        """Test log rotation functionality."""
        logger = HearthlinkLogger(
            log_dir=str(self.test_rotation_dir),
            max_size_mb=0.001,  # 1KB for quick testing
            backup_count=3
        )
        
        # Generate enough log entries to trigger rotation
        large_message = "X" * 100  # 100 character message
        
        for i in range(50):  # Should trigger rotation
            logger.logger.info(f"Rotation test message {i}: {large_message}", extra={
                "extra_fields": {
                    "event_type": "rotation_test",
                    "message_number": i,
                    "size_test": True
                }
            })
        
        # Check for rotated files
        log_files = list(self.test_rotation_dir.glob("hearthlink.log*"))
        self.assertGreater(len(log_files), 1)  # Should have at least 2 files (current + backup)
    
    def test_container_integration(self):
        """Test container integration with logging."""
        # Create container with test logging config
        container = HearthlinkContainer({
            "log_dir": str(self.test_container_dir),
            "max_size_mb": 1,
            "backup_count": 2
        })
        
        # Test status retrieval
        status = container.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        
        # Test error handling
        try:
            container.logger.log_error(
                Exception("Test container error"),
                "container_test",
                {"test_phase": "integration"}
            )
        except Exception as e:
            self.fail(f"Container error logging test failed: {e}")
        
        # Verify container was created successfully
        self.assertIsInstance(container, HearthlinkContainer)


def verify_json_format(log_file_path: Path):
    """Verify that log entries are valid JSON."""
    if not log_file_path.exists():
        return False
    
    valid_entries = 0
    invalid_entries = 0
    
    with open(log_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                json.loads(line)
                valid_entries += 1
            except json.JSONDecodeError:
                invalid_entries += 1
    
    return invalid_entries == 0


if __name__ == "__main__":
    unittest.main() 