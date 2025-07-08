#!/usr/bin/env python3
"""
Debug script for RBAC/ABAC access evaluation issue.
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.enterprise.rbac_abac_security import RBACABACSecurity, PolicyEffect

class DummyLogger:
    def __init__(self):
        self.logger = logging.getLogger("DummyLogger")
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)
    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)
    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)
    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

def debug_access_evaluation():
    """Debug the access evaluation issue."""
    
    # Create security system
    logger = DummyLogger()
    security = RBACABACSecurity(logger)
    
    # Create test user and role (same as test)
    user_id = "accessuser"
    role_id = security.create_role(
        name="Access Test Role",
        description="Role for access testing",
        permissions=["read:data", "write:own"],
        parent_roles=[]
    )
    security.assign_role_to_user(user_id, role_id, "admin")
    
    print(f"Created role: {role_id}")
    print(f"User permissions: {security.get_user_permissions(user_id)}")
    
    # Test the failing case
    print("\n=== Testing access evaluation ===")
    decision = security.evaluate_access(
        user_id=user_id,
        resource="data",
        action="read",
        context={}
    )
    
    print(f"Decision: {decision.decision}")
    print(f"Reason: {decision.reason}")
    print(f"Policies applied: {decision.policies_applied}")
    print(f"Metadata: {decision.metadata}")
    
    # Check what policies exist
    print("\n=== Available policies ===")
    for policy_id, policy in security.policies.items():
        print(f"Policy {policy_id}: {policy.name}")
        print(f"  Effect: {policy.effect}")
        print(f"  Resources: {policy.resources}")
        print(f"  Actions: {policy.actions}")
        print(f"  Conditions: {policy.conditions}")
        print(f"  Priority: {policy.priority}")
        print()

if __name__ == "__main__":
    debug_access_evaluation() 