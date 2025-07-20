# Test Reference Documentation

## Overview
This document provides traceability for all UI tests to their originating design prompts, audit line items, or sprint documentation. Test requirements are distributed across multiple source documents rather than centralized in a single test plan.

## Source Documents for Test Requirements
- **Test Planning Requirements**: `/docs/process_refinement.md`
- **Voice Functionality Tests**: `/docs/VOICE_ACCESS_POLICY.md`
- **UI Screen Validation**: `/docs/UI_ALIGNMENT_AUDIT.md`
- **Test Reference & Traceability**: `/docs/TEST_REFERENCE.md` (this document)

## Test Traceability Requirements
- All test files must include a comment or metadata block referencing:
  - Audit section
  - Feature ID (if any)
  - Policy docs (VOICE_ACCESS_POLICY, process_refinement)
- Central reporting: UI test results must be fed into central test pipeline
- Result logs stored in `/tests/results/ui/summary.json`

## Voice Policy Test Requirements
- **Source**: `/docs/VOICE_ACCESS_POLICY.md`
- **Requirements**:
  - Simulated voice interaction with trigger phrase, fallback handling, and agent confirmation
  - UI response must match expected routing behavior
  - Vault logging validation at API or mock layer
  - Voice handoff confirmation ("You're speaking with…") must be tested explicitly

## UI Test Success Criteria
- **Tier 1**: Same weight as error-handling tests
- **Pass Rate**: 100% pass required for merge
- **Edge Cases**: Negative cases must be present
- **JSON Logging**: Required where state/data is involved
- **Cross-Platform**: Windows 10 minimum, Ubuntu fallback validation

## Test Categories and References

### Voice Routing Compliance Tests
- **Feature ID**: VOICE-001
- **Source**: Owner Directive - UI Test Compliance & Execution
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Audit Section**: Voice Access States, Local Agent Voice Interaction Rules, External Agent Voice Permissions
- **Test Files**:
  - `tests/feature/ui-test-voice-routing/test_voice_routing_compliance.py`
  - `tests/feature/ui-test-voice-routing/test_voice_interaction.py`

### Agent Interaction Screen Tests
- **Feature ID**: UI-001
- **Source**: Owner Directive - Review all agent interaction screens
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Audit Section**: Voice Routing Logic, Agent Identity & Confirmation
- **Test Files**:
  - `tests/feature/ui-test-agent-interaction/test_agent_identity_display.py`
  - `tests/feature/ui-test-agent-interaction/test_voice_routing_ui.py`

### Voice Interface Component Tests
- **Feature ID**: UI-002
- **Source**: Voice routing logic implementation
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Audit Section**: Voice Authentication, Offline Mode Behavior
- **Test Files**:
  - `tests/feature/ui-test-voice-interface/test_voice_interface_component.py`
  - `tests/feature/ui-test-voice-interface/test_voice_controls.py`

### Vault Logging Tests
- **Feature ID**: VAULT-001
- **Source**: Voice session logging requirements
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Audit Section**: Logging & Transparency, Vault Logging
- **Test Files**:
  - `tests/feature/ui-test-vault-logging/test_voice_session_logging.py`
  - `tests/feature/ui-test-vault-logging/test_audit_trail.py`

## Test Infrastructure

### Environment Setup
- **File**: `tests/env/setup_ui_env.py`
- **Purpose**: Enforce UI test preconditions
- **Requirements**:
  - Fresh session state initialization
  - Logging to `/logs/tests/ui/` with timestamp
  - Resource monitoring for Voice/AI Agent interface tests

### Test Runner
- **File**: `tests/ui/runner_ui_tests.sh`
- **Purpose**: Unified test execution
- **Requirements**:
  - Same runner and report structure as Core/system tests
  - JSON format logging to `/tests/results`
  - Standalone job or integrated into nightly CI

### Central Reporting
- **File**: `/tests/results/ui/summary.json`
- **Purpose**: Centralized test results
- **Format**: JSON with test results, resource data, and environment info

## Commit Requirements

### Feature Branch Format
- All UI tests must be committed under `feature/ui-test-[module/scope]`
- Examples:
  - `feature/ui-test-voice-routing`
  - `feature/ui-test-agent-interaction`
  - `feature/ui-test-voice-interface`
  - `feature/ui-test-vault-logging`

### Commit Message Format
- Must include `UI_TEST`, feature ID (if applicable), and source of test directive
- Examples:
  - `UI_TEST: VOICE-001 - Voice routing compliance tests (Owner Directive)`
  - `UI_TEST: UI-001 - Agent interaction screen tests (Audit)`
  - `UI_TEST: VAULT-001 - Voice session logging tests (Policy)`

### QA Review Requirements
- Before merge, all test files must be peer-reviewed or verified via prompt from Owner
- All tests must link to originating design prompt, audit line item, or sprint doc

## Test Scope & Functional Depth

### Required Test Coverage
- **UI Presence**: Required
- **Functional Interactivity**: Required
- **Data Flow Validation**: Required where form or state update is expected
- **Performance Benchmarks**: Required for multi-agent screens

### Performance Requirements
- **Multi-Agent Screens**: Core Command Center, Vault Memory Manager
- **Voice Interface**: Real-time response validation
- **Resource Monitoring**: CPU, memory, disk usage tracking

## Policy Compliance References

### VOICE_ACCESS_POLICY.md References
- Voice Access States (Enabled/Disabled)
- Local Agent Voice Interaction Rules
- External Agent Voice Permissions
- Voice Routing Logic (Agnostic/Isolated modes)
- Voice Authentication (Secure Mode Activation)
- Offline Mode Behavior
- Fallback & Error States
- Logging & Transparency
- Agent Identity & Confirmation
- Vault Logging

### Process Refinement References
- Test-driven development approach
- Platinum compliance requirements
- Documentation standards
- Change management procedures

## Test Execution Workflow

1. **Environment Setup**: Initialize fresh session state via `setup_ui_env.py`
2. **Resource Monitoring**: Start monitoring for Voice/AI Agent interface tests
3. **Test Execution**: Run tests with proper feature branch structure
4. **Result Logging**: Save results to `/tests/results/ui/` in JSON format
5. **Central Reporting**: Update `/tests/results/ui/summary.json`
6. **Cleanup**: Clean up test environment and temporary files

## Compliance Checklist

- [ ] All tests committed under proper feature branches
- [ ] Commit messages include UI_TEST, feature ID, and source
- [ ] Tests reference audit sections and policy docs
- [ ] 100% pass rate achieved with edge cases
- [ ] JSON logging implemented where required
- [ ] Cross-platform validation completed
- [ ] Resource monitoring implemented for Voice/AI tests
- [ ] Central reporting updated
- [ ] QA review completed before merge
- [ ] Traceability documented in this file 