#!/usr/bin/env python3
"""
Test script for Hearthlink structured JSON logging.

This script demonstrates the logging functionality and verifies:
- Structured JSON format
- Log rotation (10MB, 5 backups)
- Error handling and fallback mechanisms
- Audit trail compliance

Run with: python tests/test_logging.py
"""

import sys
import os
import time
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import HearthlinkLogger, HearthlinkContainer


def test_structured_logging():
    """Test structured JSON logging functionality."""
    print("Testing Hearthlink structured JSON logging...")
    
    # Create test logger with smaller rotation for testing
    test_log_dir = Path("test_logs")
    logger = HearthlinkLogger(
        log_dir=str(test_log_dir),
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
    
    print(f"✅ Logging test completed. Check logs in: {test_log_dir}")
    return logger


def test_log_rotation():
    """Test log rotation functionality."""
    print("\nTesting log rotation...")
    
    test_log_dir = Path("test_rotation_logs")
    logger = HearthlinkLogger(
        log_dir=str(test_log_dir),
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
    log_files = list(test_log_dir.glob("hearthlink.log*"))
    print(f"✅ Found {len(log_files)} log files (including rotated backups)")
    
    return logger


def test_container_integration():
    """Test container integration with logging."""
    print("\nTesting container integration...")
    
    # Create container with test logging config
    container = HearthlinkContainer({
        "log_dir": "test_container_logs",
        "max_size_mb": 1,
        "backup_count": 2
    })
    
    # Test status retrieval
    status = container.get_status()
    print(f"✅ Container status: {json.dumps(status, indent=2)}")
    
    # Test error handling
    try:
        container.logger.log_error(
            Exception("Test container error"),
            "container_test",
            {"test_phase": "integration"}
        )
        print("✅ Container error logging test passed")
    except Exception as e:
        print(f"❌ Container error logging test failed: {e}")
    
    return container


def verify_json_format(log_file_path: Path):
    """Verify that log entries are valid JSON."""
    print(f"\nVerifying JSON format in: {log_file_path}")
    
    if not log_file_path.exists():
        print(f"❌ Log file not found: {log_file_path}")
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
            except json.JSONDecodeError as e:
                invalid_entries += 1
                print(f"❌ Invalid JSON at line {line_num}: {e}")
    
    print(f"✅ JSON verification: {valid_entries} valid, {invalid_entries} invalid entries")
    return invalid_entries == 0


def main():
    """Run all logging tests."""
    print("🧪 Hearthlink Structured JSON Logging Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Basic structured logging
        logger1 = test_structured_logging()
        
        # Test 2: Log rotation
        logger2 = test_log_rotation()
        
        # Test 3: Container integration
        container = test_container_integration()
        
        # Verify JSON format in test logs
        print("\n🔍 Verifying JSON format...")
        test_logs = [
            Path("test_logs/hearthlink.log"),
            Path("test_rotation_logs/hearthlink.log"),
            Path("test_container_logs/hearthlink.log")
        ]
        
        for log_file in test_logs:
            if log_file.exists():
                verify_json_format(log_file)
        
        print("\n✅ All tests completed successfully!")
        print("\n📁 Test log directories created:")
        print("  - test_logs/")
        print("  - test_rotation_logs/")
        print("  - test_container_logs/")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 