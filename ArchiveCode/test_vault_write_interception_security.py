#!/usr/bin/env python3
"""
Vault Write Interception Security Test Suite

This test suite validates the security of the Vault write interception system by:
1. Testing direct file write operations to ensure they are blocked
2. Verifying the Vault proxy routing system prevents unauthorized direct writes
3. Confirming proper audit trail logging of all write attempts
4. Testing bypass attempts through various attack vectors
5. Validating security compliance for critical file operations

CRITICAL SECURITY REQUIREMENTS:
- All direct file writes must be intercepted and blocked
- Only authorized agents with valid tokens can perform write operations
- All write attempts must be logged for audit purposes
- No bypass methods should be available for unauthorized access
"""

import os
import sys
import json
import tempfile
import shutil
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import Vault and security components
from src.vault.vault import Vault, VaultError
from src.vault.vault_enhanced import VaultEnhanced, VaultValidationError, VaultIntegrityError
from src.synapse.security_manager import SecurityManager, AgentType, PermissionType, SecurityLevel

# Test Results Storage
TEST_RESULTS = {
    "test_suite": "Vault Write Interception Security Test",
    "timestamp": datetime.now().isoformat(),
    "tests": [],
    "security_violations": [],
    "summary": {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "critical_failures": 0,
        "security_score": 0
    }
}

def log_test_result(test_name: str, passed: bool, details: str = "", is_critical: bool = False):
    """Log test result with security classification."""
    TEST_RESULTS["tests"].append({
        "test_name": test_name,
        "status": "PASS" if passed else "FAIL",
        "details": details,
        "critical": is_critical,
        "timestamp": datetime.now().isoformat()
    })
    
    TEST_RESULTS["summary"]["total_tests"] += 1
    if passed:
        TEST_RESULTS["summary"]["passed"] += 1
    else:
        TEST_RESULTS["summary"]["failed"] += 1
        if is_critical:
            TEST_RESULTS["summary"]["critical_failures"] += 1
            TEST_RESULTS["security_violations"].append({
                "test": test_name,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })

class MockLogger:
    """Mock logger for testing."""
    def __init__(self):
        self.logs = []
    
    def info(self, msg, extra=None):
        self.logs.append({"level": "INFO", "message": msg, "extra": extra, "timestamp": datetime.now().isoformat()})
    
    def error(self, msg, extra=None):
        self.logs.append({"level": "ERROR", "message": msg, "extra": extra, "timestamp": datetime.now().isoformat()})

class VaultWriteInterceptionProxy:
    """Advanced proxy for testing write interception."""
    
    def __init__(self, vault_instance, security_manager):
        self.vault = vault_instance
        self.security_manager = security_manager
        self.active_tokens = {}
        self.audit_trail = []
        self.blocked_operations = []
        self.write_operations = {
            "create_or_update_persona",
            "create_or_update_communal",
            "import_persona",
            "import_communal",
            "delete_persona",
            "delete_communal",
            "purge_persona",
            "purge_communal"
        }
    
    def generate_token(self, agent_id: str, agent_type: AgentType, permissions: List[PermissionType]) -> str:
        """Generate secure access token."""
        token = f"secure_token_{agent_id}_{int(time.time() * 1000000)}"
        self.active_tokens[token] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        self.audit_trail.append({
            "action": "TOKEN_GENERATED",
            "agent_id": agent_id,
            "agent_type": agent_type.value,
            "token": token,
            "permissions": [p.value for p in permissions],
            "timestamp": datetime.now().isoformat()
        })
        
        return token
    
    def validate_token(self, token: str, operation: str) -> bool:
        """Validate token and check permissions."""
        if token not in self.active_tokens:
            self.audit_trail.append({
                "action": "TOKEN_VALIDATION_FAILED",
                "token": token,
                "operation": operation,
                "reason": "INVALID_TOKEN",
                "timestamp": datetime.now().isoformat()
            })
            return False
        
        token_data = self.active_tokens[token]
        
        # Check if operation requires file system permission
        if operation in self.write_operations and PermissionType.FILE_SYSTEM not in token_data["permissions"]:
            self.audit_trail.append({
                "action": "PERMISSION_DENIED",
                "token": token,
                "operation": operation,
                "reason": "INSUFFICIENT_PERMISSIONS",
                "agent_id": token_data["agent_id"],
                "timestamp": datetime.now().isoformat()
            })
            return False
        
        # Update last used timestamp
        token_data["last_used"] = datetime.now().isoformat()
        
        self.audit_trail.append({
            "action": "TOKEN_VALIDATED",
            "token": token,
            "operation": operation,
            "agent_id": token_data["agent_id"],
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def intercept_write_operation(self, operation: str, agent_id: str, token: str, *args, **kwargs):
        """Intercept and validate write operations."""
        # Check if token is valid
        if not self.validate_token(token, operation):
            self.blocked_operations.append({
                "operation": operation,
                "agent_id": agent_id,
                "token": token,
                "reason": "INVALID_TOKEN_OR_PERMISSIONS",
                "timestamp": datetime.now().isoformat()
            })
            raise VaultError(f"Write operation blocked: {operation} - Invalid token or insufficient permissions")
        
        # Execute operation through vault
        try:
            result = getattr(self.vault, operation)(*args, **kwargs)
            
            self.audit_trail.append({
                "action": "WRITE_OPERATION_EXECUTED",
                "operation": operation,
                "agent_id": agent_id,
                "token": token,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        
        except Exception as e:
            self.audit_trail.append({
                "action": "WRITE_OPERATION_FAILED",
                "operation": operation,
                "agent_id": agent_id,
                "token": token,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    def simulate_direct_write_attempt(self, file_path: str, content: str, agent_id: str = "unauthorized") -> bool:
        """Simulate direct file write attempt (should be blocked)."""
        try:
            # This simulates a bypass attempt
            with open(file_path, "w") as f:
                f.write(content)
            
            # If we reach here, direct write was NOT blocked
            self.blocked_operations.append({
                "operation": "DIRECT_FILE_WRITE",
                "agent_id": agent_id,
                "file_path": file_path,
                "blocked": False,
                "vulnerability": "DIRECT_WRITE_NOT_BLOCKED",
                "timestamp": datetime.now().isoformat()
            })
            
            return True  # Write succeeded (security vulnerability)
        
        except Exception as e:
            # Direct write was blocked (good security)
            self.blocked_operations.append({
                "operation": "DIRECT_FILE_WRITE",
                "agent_id": agent_id,
                "file_path": file_path,
                "blocked": True,
                "reason": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return False  # Write blocked (security working)

def test_direct_file_write_blocking():
    """Test 1: Verify direct file write operations are blocked."""
    print("Test 1: Testing direct file write blocking...")
    
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = {
            "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key"), "key_env_var": None},
            "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
            "audit": {"log_file": str(tmpdir / "audit.log")},
            "schema_version": "1.0.0"
        }
        
        logger = MockLogger()
        vault = Vault(config, logger)
        security_manager = SecurityManager(log_file=str(tmpdir / "security.log"))
        proxy = VaultWriteInterceptionProxy(vault, security_manager)
        
        # Test multiple direct write attempts
        test_files = [
            tmpdir / "direct_write_test.txt",
            tmpdir / "unauthorized_config.json",
            tmpdir / "bypass_attempt.db",
            tmpdir / "malicious_data.bin"
        ]
        
        blocked_count = 0
        for test_file in test_files:
            was_blocked = not proxy.simulate_direct_write_attempt(str(test_file), "unauthorized content")
            if was_blocked:
                blocked_count += 1
        
        # In this test, we expect direct writes to NOT be blocked because we're not using a true interceptor
        # This is a design limitation - we need to identify this as a security gap
        if blocked_count == 0:
            log_test_result("Direct File Write Blocking", False, 
                           f"CRITICAL: Direct file writes are not intercepted - {len(test_files)} files written without authorization",
                           is_critical=True)
        else:
            log_test_result("Direct File Write Blocking", True,
                           f"Direct file writes properly blocked: {blocked_count}/{len(test_files)} attempts blocked")
    
    finally:
        shutil.rmtree(tmpdir)

def test_vault_proxy_routing_security():
    """Test 2: Verify Vault proxy routing prevents unauthorized writes."""
    print("Test 2: Testing Vault proxy routing security...")
    
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = {
            "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key"), "key_env_var": None},
            "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
            "audit": {"log_file": str(tmpdir / "audit.log")},
            "schema_version": "1.0.0"
        }
        
        logger = MockLogger()
        vault = Vault(config, logger)
        security_manager = SecurityManager(log_file=str(tmpdir / "security.log"))
        proxy = VaultWriteInterceptionProxy(vault, security_manager)
        
        # Test unauthorized write attempts
        unauthorized_agent = "malicious_agent"
        invalid_token = "invalid_token_123"
        
        write_operations = [
            ("create_or_update_persona", "malicious_persona", "test_user", {"malicious": "data"}),
            ("create_or_update_communal", "malicious_communal", {"malicious": "data"}, "test_user"),
            ("import_persona", "imported_persona", "test_user", '{"malicious": "import"}'),
            ("delete_persona", "target_persona", "test_user")
        ]
        
        blocked_operations = 0
        for operation, *args in write_operations:
            try:
                proxy.intercept_write_operation(operation, unauthorized_agent, invalid_token, *args)
                # If we reach here, the operation was not blocked (security failure)
                pass
            except VaultError as e:
                if "blocked" in str(e).lower() or "invalid token" in str(e).lower():
                    blocked_operations += 1
        
        if blocked_operations == len(write_operations):
            log_test_result("Vault Proxy Routing Security", True,
                           f"All unauthorized write operations blocked: {blocked_operations}/{len(write_operations)}")
        else:
            log_test_result("Vault Proxy Routing Security", False,
                           f"Some unauthorized operations not blocked: {blocked_operations}/{len(write_operations)} blocked",
                           is_critical=True)
    
    finally:
        shutil.rmtree(tmpdir)

def test_token_validation_bypass_attempts():
    """Test 3: Test various token validation bypass attempts."""
    print("Test 3: Testing token validation bypass attempts...")
    
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = {
            "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key"), "key_env_var": None},
            "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
            "audit": {"log_file": str(tmpdir / "audit.log")},
            "schema_version": "1.0.0"
        }
        
        logger = MockLogger()
        vault = Vault(config, logger)
        security_manager = SecurityManager(log_file=str(tmpdir / "security.log"))
        proxy = VaultWriteInterceptionProxy(vault, security_manager)
        
        # Generate a valid token for comparison
        valid_agent = "authorized_agent"
        valid_token = proxy.generate_token(valid_agent, AgentType.ALDEN, [PermissionType.FILE_SYSTEM])
        
        # Test various bypass attempts
        bypass_attempts = [
            ("", "Empty token"),
            ("null", "Null token"),
            ("undefined", "Undefined token"),
            ("admin", "Admin token guess"),
            ("root", "Root token guess"),
            ("bypass", "Bypass token guess"),
            ("123456", "Simple numeric token"),
            ("bearer_token", "Bearer token format"),
            (valid_token + "_modified", "Modified valid token"),
            (valid_token[:10], "Truncated valid token"),
            (valid_token.upper(), "Case-modified valid token")
        ]
        
        blocked_attempts = 0
        for token, description in bypass_attempts:
            try:
                proxy.intercept_write_operation("create_or_update_persona", "attacker", token, 
                                               "malicious_persona", "test_user", {"bypass": "attempt"})
                # If we reach here, bypass was successful (security failure)
                pass
            except VaultError:
                blocked_attempts += 1
        
        if blocked_attempts == len(bypass_attempts):
            log_test_result("Token Validation Bypass Attempts", True,
                           f"All bypass attempts blocked: {blocked_attempts}/{len(bypass_attempts)}")
        else:
            log_test_result("Token Validation Bypass Attempts", False,
                           f"Some bypass attempts succeeded: {blocked_attempts}/{len(bypass_attempts)} blocked",
                           is_critical=True)
    
    finally:
        shutil.rmtree(tmpdir)

def test_permission_escalation_attempts():
    """Test 4: Test permission escalation attempts."""
    print("Test 4: Testing permission escalation attempts...")
    
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = {
            "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key"), "key_env_var": None},
            "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
            "audit": {"log_file": str(tmpdir / "audit.log")},
            "schema_version": "1.0.0"
        }
        
        logger = MockLogger()
        vault = Vault(config, logger)
        security_manager = SecurityManager(log_file=str(tmpdir / "security.log"))
        proxy = VaultWriteInterceptionProxy(vault, security_manager)
        
        # Create token with limited permissions (no FILE_SYSTEM)
        limited_agent = "limited_agent"
        limited_token = proxy.generate_token(limited_agent, AgentType.EXTERNAL, [PermissionType.BROWSER_PREVIEW])
        
        # Attempt write operations with limited token
        write_operations = [
            ("create_or_update_persona", "escalated_persona", "test_user", {"escalated": "data"}),
            ("create_or_update_communal", "escalated_communal", {"escalated": "data"}, "test_user"),
            ("delete_persona", "target_persona", "test_user"),
            ("purge_persona", "target_persona", "test_user")
        ]
        
        blocked_escalations = 0
        for operation, *args in write_operations:
            try:
                proxy.intercept_write_operation(operation, limited_agent, limited_token, *args)
                # If we reach here, escalation was successful (security failure)
                pass
            except VaultError as e:
                if "insufficient permissions" in str(e).lower():
                    blocked_escalations += 1
        
        if blocked_escalations == len(write_operations):
            log_test_result("Permission Escalation Attempts", True,
                           f"All escalation attempts blocked: {blocked_escalations}/{len(write_operations)}")
        else:
            log_test_result("Permission Escalation Attempts", False,
                           f"Some escalation attempts succeeded: {blocked_escalations}/{len(write_operations)} blocked",
                           is_critical=True)
    
    finally:
        shutil.rmtree(tmpdir)

def test_audit_trail_integrity():
    """Test 5: Verify audit trail integrity and completeness."""
    print("Test 5: Testing audit trail integrity...")
    
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = {
            "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key"), "key_env_var": None},
            "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
            "audit": {"log_file": str(tmpdir / "audit.log")},
            "schema_version": "1.0.0"
        }
        
        logger = MockLogger()
        vault = Vault(config, logger)
        security_manager = SecurityManager(log_file=str(tmpdir / "security.log"))
        proxy = VaultWriteInterceptionProxy(vault, security_manager)
        
        # Generate valid token
        agent_id = "audit_test_agent"
        token = proxy.generate_token(agent_id, AgentType.SENTRY, [PermissionType.FILE_SYSTEM])
        
        # Perform multiple operations
        operations = [
            ("create_or_update_persona", "audit_persona1", "user1", {"test": "data1"}),
            ("create_or_update_persona", "audit_persona2", "user2", {"test": "data2"}),
            ("get_persona", "audit_persona1", "user1"),
            ("delete_persona", "audit_persona1", "user1")
        ]
        
        # Also attempt some unauthorized operations
        proxy.simulate_direct_write_attempt(str(tmpdir / "unauthorized.txt"), "test")
        
        # Execute authorized operations
        for operation, *args in operations:
            try:
                if operation in proxy.write_operations:
                    proxy.intercept_write_operation(operation, agent_id, token, *args)
                else:
                    # Read operation - call directly
                    getattr(vault, operation)(*args)
            except Exception:
                pass  # Continue audit trail generation
        
        # Analyze audit trail
        audit_entries = len(proxy.audit_trail)
        token_events = len([e for e in proxy.audit_trail if "TOKEN" in e["action"]])
        write_events = len([e for e in proxy.audit_trail if "WRITE" in e["action"]])
        blocked_events = len([e for e in proxy.blocked_operations])
        
        # Check completeness
        expected_min_entries = len(operations) + 2  # operations + token generation + direct write attempt
        
        if audit_entries >= expected_min_entries and token_events > 0 and blocked_events > 0:
            log_test_result("Audit Trail Integrity", True,
                           f"Audit trail complete: {audit_entries} entries, {token_events} token events, {blocked_events} blocked operations")
        else:
            log_test_result("Audit Trail Integrity", False,
                           f"Audit trail incomplete: {audit_entries} entries (expected >= {expected_min_entries})",
                           is_critical=True)
    
    finally:
        shutil.rmtree(tmpdir)

def test_file_system_protection():
    """Test 6: Test file system protection against various attack vectors."""
    print("Test 6: Testing file system protection...")
    
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = {
            "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key"), "key_env_var": None},
            "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
            "audit": {"log_file": str(tmpdir / "audit.log")},
            "schema_version": "1.0.0"
        }
        
        logger = MockLogger()
        vault = Vault(config, logger)
        security_manager = SecurityManager(log_file=str(tmpdir / "security.log"))
        proxy = VaultWriteInterceptionProxy(vault, security_manager)
        
        # Test various file system attack vectors
        attack_vectors = [
            (str(tmpdir / "config_override.json"), '{"admin": true}'),
            (str(tmpdir / "vault_key_backup.key"), "fake_encryption_key"),
            (str(tmpdir / "malicious_script.py"), "import os; os.system('rm -rf /')"),
            (str(tmpdir.parent / "escape_attempt.txt"), "directory traversal"),
            (str(tmpdir / "hidden_file"), "hidden malicious content"),
            ("/tmp/system_file.txt", "system file write attempt"),
            (str(tmpdir / "vault.db.backup"), "database backup attempt")
        ]
        
        protected_files = 0
        for file_path, content in attack_vectors:
            try:
                # This simulates various file system attacks
                was_blocked = not proxy.simulate_direct_write_attempt(file_path, content, "file_system_attacker")
                if was_blocked:
                    protected_files += 1
            except Exception:
                # Any exception means the file system is somewhat protected
                protected_files += 1
        
        # Note: In this test, we expect most files to be written because we don't have true OS-level protection
        # This identifies the security gap
        if protected_files == len(attack_vectors):
            log_test_result("File System Protection", True,
                           f"All file system attacks blocked: {protected_files}/{len(attack_vectors)}")
        else:
            log_test_result("File System Protection", False,
                           f"File system vulnerable to attacks: {protected_files}/{len(attack_vectors)} blocked",
                           is_critical=True)
    
    finally:
        shutil.rmtree(tmpdir)

def generate_security_compliance_report():
    """Generate comprehensive security compliance report."""
    print("\nGenerating Security Compliance Report...")
    
    # Calculate security score
    total_tests = TEST_RESULTS["summary"]["total_tests"]
    passed_tests = TEST_RESULTS["summary"]["passed"]
    critical_failures = TEST_RESULTS["summary"]["critical_failures"]
    
    if total_tests > 0:
        security_score = max(0, (passed_tests - critical_failures * 2) / total_tests * 100)
    else:
        security_score = 0
    
    TEST_RESULTS["summary"]["security_score"] = round(security_score, 2)
    
    # Generate compliance assessment
    compliance_status = "COMPLIANT" if critical_failures == 0 and passed_tests == total_tests else "NON-COMPLIANT"
    
    report = {
        "security_compliance_report": {
            "test_suite": TEST_RESULTS["test_suite"],
            "timestamp": datetime.now().isoformat(),
            "compliance_status": compliance_status,
            "security_score": security_score,
            "summary": TEST_RESULTS["summary"],
            "test_results": TEST_RESULTS["tests"],
            "security_violations": TEST_RESULTS["security_violations"],
            "recommendations": []
        }
    }
    
    # Add recommendations based on failures
    if critical_failures > 0:
        report["security_compliance_report"]["recommendations"].extend([
            "Implement OS-level file system access controls",
            "Add application-level write interception middleware",
            "Implement mandatory access control (MAC) policies",
            "Add real-time monitoring for unauthorized file access",
            "Implement file system sandboxing for application processes"
        ])
    
    if TEST_RESULTS["summary"]["failed"] > 0:
        report["security_compliance_report"]["recommendations"].extend([
            "Strengthen token validation mechanisms",
            "Implement additional permission checks",
            "Add rate limiting for write operations",
            "Enhance audit logging with detailed stack traces",
            "Implement automated security testing in CI/CD pipeline"
        ])
    
    return report

def main():
    """Main test execution function."""
    print("=" * 100)
    print("VAULT WRITE INTERCEPTION SECURITY TEST SUITE")
    print("=" * 100)
    print("Testing critical security requirements for Vault write interception...")
    print()
    
    # Execute all security tests
    test_direct_file_write_blocking()
    test_vault_proxy_routing_security()
    test_token_validation_bypass_attempts()
    test_permission_escalation_attempts()
    test_audit_trail_integrity()
    test_file_system_protection()
    
    # Generate compliance report
    compliance_report = generate_security_compliance_report()
    
    # Print summary
    print("\n" + "=" * 100)
    print("SECURITY TEST SUMMARY")
    print("=" * 100)
    
    summary = TEST_RESULTS["summary"]
    print(f"Total Security Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Critical Failures: {summary['critical_failures']}")
    print(f"Security Score: {summary['security_score']:.1f}%")
    print(f"Compliance Status: {compliance_report['security_compliance_report']['compliance_status']}")
    print()
    
    # Print detailed results
    print("DETAILED TEST RESULTS:")
    print("-" * 50)
    for test in TEST_RESULTS["tests"]:
        status_icon = "✓" if test["status"] == "PASS" else "✗"
        critical_marker = " [CRITICAL]" if test["critical"] else ""
        print(f"{status_icon} {test['test_name']}: {test['status']}{critical_marker}")
        if test["details"]:
            print(f"  Details: {test['details']}")
    print()
    
    # Print security violations
    if TEST_RESULTS["security_violations"]:
        print("SECURITY VIOLATIONS IDENTIFIED:")
        print("-" * 50)
        for violation in TEST_RESULTS["security_violations"]:
            print(f"✗ {violation['test']}")
            print(f"  Issue: {violation['details']}")
        print()
    
    # Print recommendations
    recommendations = compliance_report["security_compliance_report"]["recommendations"]
    if recommendations:
        print("SECURITY RECOMMENDATIONS:")
        print("-" * 50)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
    
    # Final assessment
    print("FINAL SECURITY ASSESSMENT:")
    print("-" * 50)
    
    if summary["critical_failures"] == 0 and summary["failed"] == 0:
        print("✓ All security tests passed")
        print("✓ Vault write interception system is secure")
        print("✓ No bypass methods identified")
        print("✓ System is compliant with security requirements")
    else:
        print(f"✗ {summary['critical_failures']} critical security failures identified")
        print(f"✗ {summary['failed']} total security tests failed")
        print("✗ System has security vulnerabilities")
        print("✗ Immediate remediation required")
    
    print("\n" + "=" * 100)
    print("SECURITY TEST COMPLETE")
    print("=" * 100)
    
    # Save detailed report
    try:
        report_filename = "vault_write_interception_security_report.json"
        with open(report_filename, "w") as f:
            json.dump(compliance_report, f, indent=2)
        print(f"Detailed security report saved to: {report_filename}")
    except Exception as e:
        print(f"Warning: Could not save security report: {e}")
    
    return summary["critical_failures"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)