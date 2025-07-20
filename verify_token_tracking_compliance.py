#!/usr/bin/env python3
"""
Token Tracking Compliance Verification Script

This script verifies that the token tracking system is operational and compliant
with the Claude Integration Protocol specifications.
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from log_handling.agent_token_tracker import AgentTokenTracker, get_compliance_report


def verify_log_format_compliance():
    """Verify that the log file format matches Claude Integration Protocol spec."""
    print("=" * 60)
    print("VERIFYING LOG FORMAT COMPLIANCE")
    print("=" * 60)
    
    tracker = AgentTokenTracker()
    log_file = tracker.get_log_file_path()
    
    print(f"Log file location: {log_file}")
    print(f"Log file exists: {log_file.exists()}")
    
    if not log_file.exists():
        print("❌ FAILURE: Log file does not exist")
        return False
    
    # Check format compliance
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Check header format
    if not lines[0].startswith("# Agent Token Tracker Log"):
        print("❌ FAILURE: Log file header format incorrect")
        return False
    
    # Check for required format line
    format_line_found = False
    for line in lines:
        if "Format: [timestamp] [agent_name] used X tokens for [task] in [module]" in line:
            format_line_found = True
            break
    
    if not format_line_found:
        print("❌ FAILURE: Required format specification not found in log file")
        return False
    
    # Check for actual log entries
    log_entries = []
    json_entries = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('[') and '] used ' in line and ' tokens for ' in line:
            log_entries.append(line)
        elif line.startswith('{') and line.endswith('}'):
            try:
                json_entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    
    print(f"Simple format entries found: {len(log_entries)}")
    print(f"JSON format entries found: {len(json_entries)}")
    
    if len(log_entries) == 0 or len(json_entries) == 0:
        print("❌ FAILURE: No log entries found or incorrect format")
        return False
    
    # Verify each simple format entry matches the specified format
    for entry in log_entries:
        if not (entry.startswith('[') and '] [' in entry and '] used ' in entry and ' tokens for [' in entry and '] in [' in entry):
            print(f"❌ FAILURE: Entry format incorrect: {entry}")
            return False
    
    print("✅ SUCCESS: Log format compliance verified")
    return True


def verify_agent_tracking():
    """Verify that all required agents are being tracked."""
    print("\n" + "=" * 60)
    print("VERIFYING AGENT TRACKING")
    print("=" * 60)
    
    required_agents = ['claude', 'alden', 'mimic', 'gemini', 'alice']
    
    tracker = AgentTokenTracker()
    exported_logs = tracker.export_logs(format='json')
    
    if not exported_logs:
        print("❌ FAILURE: No logs available for analysis")
        return False
    
    log_data = json.loads(exported_logs)
    tracked_agents = set()
    
    for record in log_data:
        tracked_agents.add(record['agent_name'])
    
    print(f"Required agents: {required_agents}")
    print(f"Tracked agents: {sorted(tracked_agents)}")
    
    missing_agents = [agent for agent in required_agents if agent not in tracked_agents]
    
    if missing_agents:
        print(f"❌ FAILURE: Missing agents: {missing_agents}")
        return False
    
    print("✅ SUCCESS: All required agents are being tracked")
    return True


def verify_performance_metrics():
    """Verify that performance metrics are being captured."""
    print("\n" + "=" * 60)
    print("VERIFYING PERFORMANCE METRICS")
    print("=" * 60)
    
    tracker = AgentTokenTracker()
    exported_logs = tracker.export_logs(format='json')
    
    if not exported_logs:
        print("❌ FAILURE: No logs available for metrics analysis")
        return False
    
    log_data = json.loads(exported_logs)
    
    # Check required fields in log entries
    required_fields = [
        'timestamp', 'agent_name', 'agent_type', 'task_description', 
        'module', 'tokens_used', 'operation_type', 'success'
    ]
    
    for i, record in enumerate(log_data):
        for field in required_fields:
            if field not in record:
                print(f"❌ FAILURE: Missing required field '{field}' in record {i}")
                return False
    
    # Check that tokens_used is numeric
    for record in log_data:
        if not isinstance(record['tokens_used'], (int, float)):
            print(f"❌ FAILURE: tokens_used must be numeric, got {type(record['tokens_used'])}")
            return False
    
    print(f"✅ SUCCESS: Performance metrics verified for {len(log_data)} records")
    return True


def verify_export_functionality():
    """Verify that log export functionality works correctly."""
    print("\n" + "=" * 60)
    print("VERIFYING EXPORT FUNCTIONALITY")
    print("=" * 60)
    
    tracker = AgentTokenTracker()
    
    # Test JSON export
    json_export = tracker.export_logs(format='json')
    if not json_export:
        print("❌ FAILURE: JSON export returned empty result")
        return False
    
    try:
        json.loads(json_export)
        print("✅ SUCCESS: JSON export format valid")
    except json.JSONDecodeError:
        print("❌ FAILURE: JSON export format invalid")
        return False
    
    # Test CSV export
    csv_export = tracker.export_logs(format='csv')
    if not csv_export:
        print("❌ FAILURE: CSV export returned empty result")
        return False
    
    if not csv_export.startswith('agent_name,'):
        print("❌ FAILURE: CSV export format incorrect")
        return False
    
    print("✅ SUCCESS: CSV export format valid")
    
    # Test simple export
    simple_export = tracker.export_logs(format='simple')
    if not simple_export:
        print("❌ FAILURE: Simple export returned empty result")
        return False
    
    if not simple_export.startswith('['):
        print("❌ FAILURE: Simple export format incorrect")
        return False
    
    print("✅ SUCCESS: Simple export format valid")
    return True


def verify_claude_integration_protocol():
    """Verify compliance with Claude Integration Protocol."""
    print("\n" + "=" * 60)
    print("VERIFYING CLAUDE INTEGRATION PROTOCOL COMPLIANCE")
    print("=" * 60)
    
    compliance_report = get_compliance_report()
    
    print("Compliance Report:")
    print(json.dumps(compliance_report, indent=2))
    
    # Check compliance status
    status = compliance_report['compliance_status']
    
    if not status['log_file_exists']:
        print("❌ FAILURE: Log file does not exist")
        return False
    
    if not status['log_format_compliant']:
        print("❌ FAILURE: Log format not compliant")
        return False
    
    print("✅ SUCCESS: Claude Integration Protocol compliance verified")
    return True


def main():
    """Main verification function."""
    print("TOKEN TRACKING COMPLIANCE VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Log Format Compliance", verify_log_format_compliance),
        ("Agent Tracking", verify_agent_tracking),
        ("Performance Metrics", verify_performance_metrics),
        ("Export Functionality", verify_export_functionality),
        ("Claude Integration Protocol", verify_claude_integration_protocol)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ FAILURE: {test_name} - Exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - TOKEN TRACKING SYSTEM IS FULLY OPERATIONAL")
        return True
    else:
        print(f"\n❌ {total - passed} TESTS FAILED - SYSTEM NEEDS ATTENTION")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)