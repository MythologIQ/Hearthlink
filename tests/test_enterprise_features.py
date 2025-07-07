#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Enterprise Features

Tests all enterprise features including:
- Multi-User Collaboration
- RBAC/ABAC Security
- SIEM Monitoring
- Advanced Monitoring

Includes integration testing, edge cases, and negative testing.

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import time
import asyncio
import unittest
import tempfile
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.enterprise.multi_user_collaboration import (
    MultiUserCollaboration, User, CollaborativeSession, 
    UserRole, SessionType, Permission, CollaborationError
)
from src.enterprise.rbac_abac_security import (
    RBACABACSecurity, Role, Policy, UserRole as SecurityUserRole,
    ResourceType, Action, PolicyEffect, SecurityError
)
from src.enterprise.siem_monitoring import (
    SIEMMonitoring, SecurityEvent, ThreatIndicator,
    SecurityAlert, SecurityIncident, EventSeverity,
    EventCategory, ThreatType, SIEMError
)
from src.enterprise.advanced_monitoring import (
    AdvancedMonitoring, Metric, AlertRule, Alert,
    HealthCheck, PerformanceMetrics, MetricType,
    AlertSeverity, HealthStatus, MonitoringError
)
from main import HearthlinkLogger


class TestEnterpriseFeatures(unittest.TestCase):
    """Comprehensive test suite for enterprise features."""
    
    def setUp(self):
        """Set up test environment."""
        self.logger = HearthlinkLogger()
        
        # Initialize enterprise modules
        self.collaboration = MultiUserCollaboration(logger=self.logger)
        self.security = RBACABACSecurity(logger=self.logger)
        self.siem = SIEMMonitoring(logger=self.logger)
        self.monitoring = AdvancedMonitoring(logger=self.logger)
        
        # Test data
        self.test_users = []
        self.test_sessions = []
        self.test_roles = []
        self.test_policies = []
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up test data
        self.test_users.clear()
        self.test_sessions.clear()
        self.test_roles.clear()
        self.test_policies.clear()


class TestMultiUserCollaboration(TestEnterpriseFeatures):
    """Test suite for multi-user collaboration features."""
    
    def test_01_user_registration(self):
        """Test user registration functionality."""
        # Test valid user registration
        user_id = self.collaboration.register_user(
            username="testuser1",
            email="test1@example.com",
            role=UserRole.USER
        )
        self.assertIsNotNone(user_id)
        self.assertIn(user_id, self.collaboration.users)
        
        # Test duplicate username
        with self.assertRaises(CollaborationError):
            self.collaboration.register_user(
                username="testuser1",
                email="test2@example.com",
                role=UserRole.USER
            )
        
        # Test duplicate email
        with self.assertRaises(CollaborationError):
            self.collaboration.register_user(
                username="testuser2",
                email="test1@example.com",
                role=UserRole.USER
            )
        
        # Test invalid input
        with self.assertRaises(CollaborationError):
            self.collaboration.register_user("", "test@example.com", UserRole.USER)
        
        with self.assertRaises(CollaborationError):
            self.collaboration.register_user("testuser", "", UserRole.USER)
    
    def test_02_user_authentication(self):
        """Test user authentication."""
        # Register test user
        user_id = self.collaboration.register_user(
            username="authuser",
            email="auth@example.com",
            role=UserRole.USER
        )
        
        # Test authentication
        auth_user_id = self.collaboration.authenticate_user("authuser", "password_hash")
        self.assertEqual(auth_user_id, user_id)
        
        # Test invalid authentication
        invalid_auth = self.collaboration.authenticate_user("nonexistent", "password")
        self.assertIsNone(invalid_auth)
        
        # Test inactive user
        self.collaboration.users[user_id].is_active = False
        inactive_auth = self.collaboration.authenticate_user("authuser", "password_hash")
        self.assertIsNone(inactive_auth)
    
    def test_03_session_creation(self):
        """Test collaborative session creation."""
        # Create test user
        user_id = self.collaboration.register_user(
            username="sessionuser",
            email="session@example.com",
            role=UserRole.USER
        )
        
        # Test valid session creation
        session_id = self.collaboration.create_collaborative_session(
            name="Test Session",
            description="Test session description",
            session_type=SessionType.COLLABORATIVE,
            created_by=user_id
        )
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.collaboration.sessions)
        
        # Test session properties
        session = self.collaboration.sessions[session_id]
        self.assertEqual(session.name, "Test Session")
        self.assertEqual(session.created_by, user_id)
        self.assertIn(user_id, session.participants)
        self.assertTrue(session.is_active)
        
        # Test invalid session creation
        with self.assertRaises(CollaborationError):
            self.collaboration.create_collaborative_session(
                name="",
                description="Test",
                session_type=SessionType.COLLABORATIVE,
                created_by="nonexistent_user"
            )
    
    def test_04_session_joining(self):
        """Test session joining functionality."""
        # Create test users
        creator_id = self.collaboration.register_user(
            username="creator",
            email="creator@example.com",
            role=UserRole.USER
        )
        joiner_id = self.collaboration.register_user(
            username="joiner",
            email="joiner@example.com",
            role=UserRole.USER
        )
        
        # Create session
        session_id = self.collaboration.create_collaborative_session(
            name="Join Test Session",
            description="Test session for joining",
            session_type=SessionType.COLLABORATIVE,
            created_by=creator_id
        )
        
        # Test successful join
        join_result = self.collaboration.join_session(session_id, joiner_id)
        self.assertTrue(join_result)
        
        session = self.collaboration.sessions[session_id]
        self.assertIn(joiner_id, session.participants)
        
        # Test joining already joined session
        join_again = self.collaboration.join_session(session_id, joiner_id)
        self.assertTrue(join_again)  # Should return True for already joined
        
        # Test joining non-existent session
        with self.assertRaises(CollaborationError):
            self.collaboration.join_session("nonexistent_session", joiner_id)
    
    def test_05_session_sharing(self):
        """Test session sharing functionality."""
        # Create test users
        owner_id = self.collaboration.register_user(
            username="owner",
            email="owner@example.com",
            role=UserRole.USER
        )
        sharee_id = self.collaboration.register_user(
            username="sharee",
            email="sharee@example.com",
            role=UserRole.USER
        )
        
        # Create session
        session_id = self.collaboration.create_collaborative_session(
            name="Share Test Session",
            description="Test session for sharing",
            session_type=SessionType.COLLABORATIVE,
            created_by=owner_id
        )
        
        # Test successful sharing
        share_result = self.collaboration.share_session(
            session_id=session_id,
            from_user_id=owner_id,
            to_user_id=sharee_id,
            permissions=[Permission.READ, Permission.WRITE]
        )
        self.assertTrue(share_result)
        
        session = self.collaboration.sessions[session_id]
        self.assertIn(sharee_id, session.participants)
        self.assertIn(Permission.READ, session.permissions[sharee_id])
        self.assertIn(Permission.WRITE, session.permissions[sharee_id])
        
        # Test sharing without permission
        unauthorized_id = self.collaboration.register_user(
            username="unauthorized",
            email="unauthorized@example.com",
            role=UserRole.GUEST
        )
        
        with self.assertRaises(CollaborationError):
            self.collaboration.share_session(
                session_id=session_id,
                from_user_id=unauthorized_id,
                to_user_id=sharee_id,
                permissions=[Permission.READ]
            )
    
    def test_06_collaboration_events(self):
        """Test collaboration event recording."""
        # Create test user and session
        user_id = self.collaboration.register_user(
            username="eventuser",
            email="event@example.com",
            role=UserRole.USER
        )
        session_id = self.collaboration.create_collaborative_session(
            name="Event Test Session",
            description="Test session for events",
            session_type=SessionType.COLLABORATIVE,
            created_by=user_id
        )
        
        # Test event recording
        event_id = self.collaboration.record_collaboration_event(
            session_id=session_id,
            user_id=user_id,
            event_type="test_event",
            data={"key": "value", "number": 42}
        )
        self.assertIsNotNone(event_id)
        
        # Test state update event
        state_event_id = self.collaboration.record_collaboration_event(
            session_id=session_id,
            user_id=user_id,
            event_type="state_update",
            data={"new_state": "updated"}
        )
        self.assertIsNotNone(state_event_id)
        
        # Verify state was updated
        session = self.collaboration.sessions[session_id]
        self.assertIn("new_state", session.state)
        self.assertEqual(session.state["new_state"], "updated")
    
    def test_07_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with maximum users
        max_users = 100
        user_ids = []
        
        for i in range(max_users):
            user_id = self.collaboration.register_user(
                username=f"maxuser{i}",
                email=f"maxuser{i}@example.com",
                role=UserRole.USER
            )
            user_ids.append(user_id)
        
        # Verify all users created
        self.assertEqual(len(self.collaboration.users), max_users + 1)  # +1 for admin
        
        # Test session with many participants
        creator_id = user_ids[0]
        session_id = self.collaboration.create_collaborative_session(
            name="Large Session",
            description="Session with many participants",
            session_type=SessionType.COLLABORATIVE,
            created_by=creator_id
        )
        
        # Add many participants
        for user_id in user_ids[1:10]:  # Add 9 more participants
            self.collaboration.join_session(session_id, user_id)
        
        session = self.collaboration.sessions[session_id]
        self.assertEqual(len(session.participants), 10)  # Creator + 9 participants
        
        # Test leaving session
        leave_result = self.collaboration.leave_session(session_id, user_ids[1])
        self.assertTrue(leave_result)
        self.assertNotIn(user_ids[1], session.participants)


class TestRBACABACSecurity(TestEnterpriseFeatures):
    """Test suite for RBAC/ABAC security features."""
    
    def test_01_role_creation(self):
        """Test role creation functionality."""
        # Test valid role creation
        role_id = self.security.create_role(
            name="Test Role",
            description="Test role description",
            permissions=["read:data", "write:own"],
            parent_roles=[]
        )
        self.assertIsNotNone(role_id)
        self.assertIn(role_id, self.security.roles)
        
        # Test role properties
        role = self.security.roles[role_id]
        self.assertEqual(role.name, "Test Role")
        self.assertEqual(role.description, "Test role description")
        self.assertIn("read:data", role.permissions)
        self.assertIn("write:own", role.permissions)
        self.assertTrue(role.is_active)
        
        # Test duplicate role name
        with self.assertRaises(SecurityError):
            self.security.create_role(
                name="Test Role",
                description="Duplicate role",
                permissions=["read:data"],
                parent_roles=[]
            )
        
        # Test invalid input
        with self.assertRaises(SecurityError):
            self.security.create_role("", "Test", ["read:data"], [])
        
        with self.assertRaises(SecurityError):
            self.security.create_role("Test", "Test", [], [])
    
    def test_02_role_assignment(self):
        """Test role assignment functionality."""
        # Create test role
        role_id = self.security.create_role(
            name="Assignment Test Role",
            description="Role for assignment testing",
            permissions=["read:data"],
            parent_roles=[]
        )
        
        # Test valid role assignment
        assign_result = self.security.assign_role_to_user(
            user_id="testuser",
            role_id=role_id,
            assigned_by="admin"
        )
        self.assertTrue(assign_result)
        
        # Verify assignment
        user_roles = self.security.get_user_roles("testuser")
        role_names = [role.name for role in user_roles]
        self.assertIn("Assignment Test Role", role_names)
        
        # Test duplicate assignment
        duplicate_result = self.security.assign_role_to_user(
            user_id="testuser",
            role_id=role_id,
            assigned_by="admin"
        )
        self.assertTrue(duplicate_result)  # Should return True for already assigned
        
        # Test assignment to non-existent role
        with self.assertRaises(SecurityError):
            self.security.assign_role_to_user(
                user_id="testuser",
                role_id="nonexistent_role",
                assigned_by="admin"
            )
    
    def test_03_policy_creation(self):
        """Test policy creation functionality."""
        # Test valid policy creation
        policy_id = self.security.create_policy(
            name="Test Policy",
            description="Test policy description",
            effect=PolicyEffect.ALLOW,
            resources=["data:*"],
            actions=["read", "write"],
            conditions={"user_role": "user"},
            priority=50
        )
        self.assertIsNotNone(policy_id)
        self.assertIn(policy_id, self.security.policies)
        
        # Test policy properties
        policy = self.security.policies[policy_id]
        self.assertEqual(policy.name, "Test Policy")
        self.assertEqual(policy.effect, PolicyEffect.ALLOW)
        self.assertIn("data:*", policy.resources)
        self.assertIn("read", policy.actions)
        self.assertEqual(policy.priority, 50)
        self.assertTrue(policy.is_active)
        
        # Test duplicate policy name
        with self.assertRaises(SecurityError):
            self.security.create_policy(
                name="Test Policy",
                description="Duplicate policy",
                effect=PolicyEffect.DENY,
                resources=["*"],
                actions=["*"],
                conditions={}
            )
    
    def test_04_access_evaluation(self):
        """Test access control evaluation."""
        # Create test user and role
        user_id = "accessuser"
        role_id = self.security.create_role(
            name="Access Test Role",
            description="Role for access testing",
            permissions=["read:data", "write:own"],
            parent_roles=[]
        )
        self.security.assign_role_to_user(user_id, role_id, "admin")
        
        # Test allowed access
        decision = self.security.evaluate_access(
            user_id=user_id,
            resource="data",
            action="read",
            context={}
        )
        self.assertEqual(decision.decision, PolicyEffect.ALLOW)
        
        # Test denied access
        decision = self.security.evaluate_access(
            user_id=user_id,
            resource="admin",
            action="read",
            context={}
        )
        self.assertEqual(decision.decision, PolicyEffect.DENY)
        
        # Test with context
        decision = self.security.evaluate_access(
            user_id=user_id,
            resource="data",
            action="read",
            context={"time_hour": 23}
        )
        self.assertEqual(decision.decision, PolicyEffect.DENY)  # Time-based policy should deny
    
    def test_05_role_inheritance(self):
        """Test role inheritance functionality."""
        # Create parent role
        parent_role_id = self.security.create_role(
            name="Parent Role",
            description="Parent role",
            permissions=["read:data"],
            parent_roles=[]
        )
        
        # Create child role
        child_role_id = self.security.create_role(
            name="Child Role",
            description="Child role",
            permissions=["write:own"],
            parent_roles=[parent_role_id]
        )
        
        # Assign child role to user
        user_id = "inheritanceuser"
        self.security.assign_role_to_user(user_id, child_role_id, "admin")
        
        # Get user roles (should include inherited)
        user_roles = self.security.get_user_roles(user_id)
        role_names = [role.name for role in user_roles]
        
        # Should have both child and parent roles
        self.assertIn("Child Role", role_names)
        self.assertIn("Parent Role", role_names)
        
        # Test permissions inheritance
        user_permissions = self.security.get_user_permissions(user_id)
        self.assertIn("read:data", user_permissions)
        self.assertIn("write:own", user_permissions)
    
    def test_06_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with many roles
        role_ids = []
        for i in range(10):
            role_id = self.security.create_role(
                name=f"Test Role {i}",
                description=f"Test role {i}",
                permissions=[f"action:{i}"],
                parent_roles=[]
            )
            role_ids.append(role_id)
        
        # Test complex inheritance chain
        chain_role_id = self.security.create_role(
            name="Chain Role",
            description="Role in inheritance chain",
            permissions=["chain:permission"],
            parent_roles=role_ids[:3]  # Inherit from first 3 roles
        )
        
        # Assign to user
        user_id = "chainuser"
        self.security.assign_role_to_user(user_id, chain_role_id, "admin")
        
        # Verify all inherited permissions
        user_permissions = self.security.get_user_permissions(user_id)
        self.assertIn("chain:permission", user_permissions)
        for i in range(3):
            self.assertIn(f"action:{i}", user_permissions)


class TestSIEMMonitoring(TestEnterpriseFeatures):
    """Test suite for SIEM monitoring features."""
    
    def test_01_event_collection(self):
        """Test security event collection."""
        # Test valid event collection
        event_id = self.siem.collect_event(
            source="test_source",
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.MEDIUM,
            user_id="testuser",
            details={"action": "login", "ip": "192.168.1.1"}
        )
        self.assertIsNotNone(event_id)
        self.assertGreater(len(self.siem.events), 0)
        
        # Test event properties
        event = self.siem.events[0]
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.category, EventCategory.AUTHENTICATION)
        self.assertEqual(event.severity, EventSeverity.MEDIUM)
        self.assertEqual(event.user_id, "testuser")
        self.assertIn("action", event.details)
        
        # Test different event categories
        categories = [
            EventCategory.AUTHORIZATION,
            EventCategory.DATA_ACCESS,
            EventCategory.SYSTEM_ACCESS,
            EventCategory.NETWORK_ACCESS,
            EventCategory.MALWARE,
            EventCategory.COMPLIANCE,
            EventCategory.AUDIT
        ]
        
        for category in categories:
            event_id = self.siem.collect_event(
                source="test_source",
                category=category,
                severity=EventSeverity.LOW,
                user_id="testuser"
            )
            self.assertIsNotNone(event_id)
    
    def test_02_threat_detection(self):
        """Test threat detection functionality."""
        # Collect multiple failed auth events to trigger brute force detection
        for i in range(6):
            self.siem.collect_event(
                source="auth_system",
                category=EventCategory.AUTHENTICATION,
                severity=EventSeverity.MEDIUM,
                user_id="bruteforceuser",
                details={"action": "login_failed"}
            )
        
        # Check for brute force alert
        alerts = self.siem.get_active_alerts()
        self.assertGreater(len(alerts), 0)
        
        # Verify alert properties
        alert = alerts[0]
        self.assertEqual(alert.threat_type, ThreatType.BRUTE_FORCE)
        self.assertGreater(len(alert.events), 0)
        self.assertEqual(alert.status, "new")
    
    def test_03_incident_management(self):
        """Test incident management functionality."""
        # Create high severity event to trigger incident
        self.siem.collect_event(
            source="security_system",
            category=EventCategory.COMPLIANCE,
            severity=EventSeverity.CRITICAL,
            user_id="incidentuser",
            details={"violation_type": "data_breach"}
        )
        
        # Check for incident creation
        incidents = self.siem.get_active_incidents()
        self.assertGreater(len(incidents), 0)
        
        # Test incident status update
        incident = incidents[0]
        update_result = self.siem.update_incident_status(
            incident_id=incident.incident_id,
            status=IncidentStatus.INVESTIGATING,
            assigned_to="security_admin",
            action_taken="Incident investigation started"
        )
        self.assertTrue(update_result)
        
        # Verify status update
        updated_incident = self.siem.incidents[incident.incident_id]
        self.assertEqual(updated_incident.status, IncidentStatus.INVESTIGATING)
        self.assertEqual(updated_incident.assigned_to, "security_admin")
        self.assertGreater(len(updated_incident.actions_taken), 0)
    
    def test_04_security_metrics(self):
        """Test security metrics functionality."""
        # Collect various events
        for i in range(10):
            self.siem.collect_event(
                source="test_source",
                category=EventCategory.AUTHENTICATION,
                severity=EventSeverity.MEDIUM,
                user_id=f"user{i}",
                details={"action": "login"}
            )
        
        for i in range(5):
            self.siem.collect_event(
                source="test_source",
                category=EventCategory.DATA_ACCESS,
                severity=EventSeverity.HIGH,
                user_id=f"user{i}",
                details={"action": "data_read"}
            )
        
        # Get security metrics
        metrics = self.siem.get_security_metrics()
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.total_events, 15)
        self.assertIn("medium", metrics.events_by_severity)
        self.assertIn("high", metrics.events_by_severity)
        self.assertIn("authentication", metrics.events_by_category)
        self.assertIn("data_access", metrics.events_by_category)
    
    def test_05_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with many events
        for i in range(100):
            self.siem.collect_event(
                source="bulk_source",
                category=EventCategory.AUDIT,
                severity=EventSeverity.LOW,
                user_id=f"bulkuser{i}",
                details={"event_number": i}
            )
        
        # Verify all events collected
        self.assertEqual(len(self.siem.events), 100)
        
        # Test event retrieval
        events = self.siem.get_session_events("nonexistent_session", "testuser")
        self.assertEqual(len(events), 0)
        
        # Test metrics with date range
        start_date = (datetime.now() - timedelta(hours=1)).isoformat()
        end_date = datetime.now().isoformat()
        metrics = self.siem.get_security_metrics(start_date, end_date)
        self.assertIsNotNone(metrics)


class TestAdvancedMonitoring(TestEnterpriseFeatures):
    """Test suite for advanced monitoring features."""
    
    def test_01_metric_recording(self):
        """Test metric recording functionality."""
        # Test valid metric recording
        metric_id = self.monitoring.record_metric(
            name="test.metric",
            value=100.0,
            metric_type=MetricType.GAUGE,
            labels={"endpoint": "/api/test", "method": "GET"}
        )
        self.assertIsNotNone(metric_id)
        self.assertIn("test.metric", self.monitoring.metrics)
        
        # Test metric properties
        metric = self.monitoring.metrics["test.metric"][0]
        self.assertEqual(metric.name, "test.metric")
        self.assertEqual(metric.value, 100.0)
        self.assertEqual(metric.metric_type, MetricType.GAUGE)
        self.assertIn("endpoint", metric.labels)
        
        # Test different metric types
        metric_types = [MetricType.COUNTER, MetricType.HISTOGRAM, MetricType.SUMMARY]
        for metric_type in metric_types:
            metric_id = self.monitoring.record_metric(
                name=f"test.{metric_type.value}",
                value=50.0,
                metric_type=metric_type
            )
            self.assertIsNotNone(metric_id)
    
    def test_02_alert_rule_creation(self):
        """Test alert rule creation functionality."""
        # Create test metric
        self.monitoring.record_metric("test.alert.metric", 100.0, MetricType.GAUGE)
        
        # Create alert rule
        rule_id = self.monitoring.create_alert_rule(
            name="Test Alert Rule",
            description="Test alert rule description",
            metric_name="test.alert.metric",
            condition=">",
            threshold=50.0,
            severity=AlertSeverity.WARNING,
            duration_minutes=2
        )
        self.assertIsNotNone(rule_id)
        self.assertIn(rule_id, self.monitoring.alert_rules)
        
        # Test rule properties
        rule = self.monitoring.alert_rules[rule_id]
        self.assertEqual(rule.name, "Test Alert Rule")
        self.assertEqual(rule.metric_name, "test.alert.metric")
        self.assertEqual(rule.condition, ">")
        self.assertEqual(rule.threshold, 50.0)
        self.assertEqual(rule.severity, AlertSeverity.WARNING)
        self.assertTrue(rule.is_active)
    
    def test_03_health_checks(self):
        """Test health check functionality."""
        # Get health status
        health_status = self.monitoring.get_health_status()
        self.assertIsNotNone(health_status)
        
        # Verify all components have health checks
        expected_components = ["system", "database", "network", "application"]
        for component in expected_components:
            self.assertIn(component, health_status)
            check = health_status[component]
            self.assertIsInstance(check, HealthCheck)
            self.assertIn(check.status, [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN])
    
    def test_04_performance_metrics(self):
        """Test performance metrics functionality."""
        # Record various metrics
        for i in range(10):
            self.monitoring.record_metric(
                name="performance.cpu",
                value=50.0 + i,
                metric_type=MetricType.GAUGE
            )
            self.monitoring.record_metric(
                name="performance.memory",
                value=60.0 + i,
                metric_type=MetricType.GAUGE
            )
        
        # Get performance metrics
        performance = self.monitoring.get_performance_metrics(duration_minutes=60)
        self.assertIsNotNone(performance)
        self.assertGreater(performance.cpu_usage_percent, 0)
        self.assertGreater(performance.memory_usage_percent, 0)
        self.assertGreater(performance.disk_usage_percent, 0)
    
    def test_05_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with many metrics
        for i in range(100):
            self.monitoring.record_metric(
                name=f"bulk.metric.{i}",
                value=float(i),
                metric_type=MetricType.GAUGE
            )
        
        # Verify metrics recorded
        self.assertGreater(len(self.monitoring.metrics), 0)
        
        # Test alert acknowledgment
        # Create alert first
        self.monitoring.record_metric("ack.metric", 200.0, MetricType.GAUGE)
        rule_id = self.monitoring.create_alert_rule(
            name="Ack Test Rule",
            description="Test rule for acknowledgment",
            metric_name="ack.metric",
            condition=">",
            threshold=100.0,
            severity=AlertSeverity.WARNING
        )
        
        # Wait for alert to be created
        time.sleep(1)
        
        # Get active alerts
        alerts = self.monitoring.get_active_alerts()
        if alerts:
            alert = alerts[0]
            ack_result = self.monitoring.acknowledge_alert(
                alert_id=alert.alert_id,
                user_id="testuser"
            )
            self.assertTrue(ack_result)


class TestEnterpriseIntegration(TestEnterpriseFeatures):
    """Test suite for enterprise feature integration."""
    
    def test_01_cross_module_integration(self):
        """Test integration between enterprise modules."""
        # Create user in collaboration system
        user_id = self.collaboration.register_user(
            username="integrationuser",
            email="integration@example.com",
            role=UserRole.USER
        )
        
        # Create role in security system
        role_id = self.security.create_role(
            name="Integration Role",
            description="Role for integration testing",
            permissions=["read:data", "write:own"],
            parent_roles=[]
        )
        
        # Assign role to user
        self.security.assign_role_to_user(user_id, role_id, "admin")
        
        # Create session in collaboration system
        session_id = self.collaboration.create_collaborative_session(
            name="Integration Session",
            description="Session for integration testing",
            session_type=SessionType.COLLABORATIVE,
            created_by=user_id
        )
        
        # Record events in SIEM
        siem_event_id = self.siem.collect_event(
            source="integration_test",
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.MEDIUM,
            user_id=user_id,
            details={"session_id": session_id}
        )
        
        # Record metrics in monitoring
        metric_id = self.monitoring.record_metric(
            name="integration.metric",
            value=100.0,
            metric_type=MetricType.GAUGE,
            labels={"user_id": user_id, "session_id": session_id}
        )
        
        # Verify all systems have the data
        self.assertIn(user_id, self.collaboration.users)
        self.assertIn(session_id, self.collaboration.sessions)
        
        user_roles = self.security.get_user_roles(user_id)
        self.assertGreater(len(user_roles), 0)
        
        self.assertGreater(len(self.siem.events), 0)
        self.assertIn("integration.metric", self.monitoring.metrics)
    
    def test_02_security_integration(self):
        """Test security integration across modules."""
        # Create user with specific role
        user_id = self.collaboration.register_user(
            username="securityuser",
            email="security@example.com",
            role=UserRole.USER
        )
        
        # Create restrictive role
        restrictive_role_id = self.security.create_role(
            name="Restrictive Role",
            description="Role with limited permissions",
            permissions=["read:own"],
            parent_roles=[]
        )
        
        # Assign restrictive role
        self.security.assign_role_to_user(user_id, restrictive_role_id, "admin")
        
        # Test access control integration
        # Should be able to read own data
        decision = self.security.evaluate_access(
            user_id=user_id,
            resource="data",
            action="read",
            context={"resource_owner": user_id}
        )
        self.assertEqual(decision.decision, PolicyEffect.ALLOW)
        
        # Should not be able to read other data
        decision = self.security.evaluate_access(
            user_id=user_id,
            resource="data",
            action="read",
            context={"resource_owner": "otheruser"}
        )
        self.assertEqual(decision.decision, PolicyEffect.DENY)
        
        # Record security events
        self.siem.collect_event(
            source="security_integration",
            category=EventCategory.AUTHORIZATION,
            severity=EventSeverity.MEDIUM,
            user_id=user_id,
            details={"decision": decision.decision.value}
        )
    
    def test_03_monitoring_integration(self):
        """Test monitoring integration across modules."""
        # Create test scenario
        user_id = self.collaboration.register_user(
            username="monitoruser",
            email="monitor@example.com",
            role=UserRole.USER
        )
        
        # Simulate high activity
        for i in range(10):
            # Create session
            session_id = self.collaboration.create_collaborative_session(
                name=f"Monitor Session {i}",
                description=f"Session {i} for monitoring",
                session_type=SessionType.COLLABORATIVE,
                created_by=user_id
            )
            
            # Record collaboration events
            self.collaboration.record_collaboration_event(
                session_id=session_id,
                user_id=user_id,
                event_type="activity",
                data={"session_number": i}
            )
            
            # Record SIEM events
            self.siem.collect_event(
                source="monitoring_integration",
                category=EventCategory.DATA_ACCESS,
                severity=EventSeverity.MEDIUM,
                user_id=user_id,
                details={"session_id": session_id}
            )
            
            # Record monitoring metrics
            self.monitoring.record_metric(
                name="integration.activity",
                value=float(i),
                metric_type=MetricType.COUNTER,
                labels={"user_id": user_id, "session_id": session_id}
            )
        
        # Verify monitoring data
        performance = self.monitoring.get_performance_metrics()
        self.assertIsNotNone(performance)
        
        health_status = self.monitoring.get_health_status()
        self.assertIsNotNone(health_status)
        
        siem_metrics = self.siem.get_security_metrics()
        self.assertGreater(siem_metrics.total_events, 0)
    
    def test_04_error_handling_integration(self):
        """Test error handling across enterprise modules."""
        # Test invalid operations across modules
        with self.assertRaises(CollaborationError):
            self.collaboration.register_user("", "test@example.com", UserRole.USER)
        
        with self.assertRaises(SecurityError):
            self.security.create_role("", "Test", [], [])
        
        with self.assertRaises(SIEMError):
            self.siem.collect_event("", EventCategory.AUTHENTICATION, EventSeverity.MEDIUM)
        
        with self.assertRaises(MonitoringError):
            self.monitoring.record_metric("", 100.0, MetricType.GAUGE)
        
        # Verify systems remain stable after errors
        self.assertIsNotNone(self.collaboration.users)
        self.assertIsNotNone(self.security.roles)
        self.assertIsNotNone(self.siem.events)
        self.assertIsNotNone(self.monitoring.metrics)


def run_comprehensive_tests():
    """Run comprehensive test suite."""
    print("🚀 Starting Comprehensive Enterprise Features Test Suite")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestMultiUserCollaboration,
        TestRBACABACSecurity,
        TestSIEMMonitoring,
        TestAdvancedMonitoring,
        TestEnterpriseIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result


if __name__ == "__main__":
    run_comprehensive_tests() 