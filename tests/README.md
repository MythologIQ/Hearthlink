# Hearthlink Test Suite

## Overview
This directory contains comprehensive tests for the Hearthlink system, including core functionality, UI components, voice routing, and agent interactions.

## UI Test Success Criteria

### Tier 1 Priority
UI Tests have the same weight as error-handling tests and are considered critical for system reliability.

### Pass Rate Requirements
- **100% pass rate required** for merge approval
- **Edge cases must be present** and tested
- **Negative test cases** are mandatory

### Logging Requirements
- **JSON logging required** where state/data is involved
- **Visual UI only tests** are exempt from JSON logging
- **All test runs must log** to `/logs/tests/ui/` with timestamp

### Cross-Platform Validation
- **Windows 10**: Minimum validation required
- **Ubuntu**: Fallback validation (dev/test logs only)
- **Resource monitoring**: Required for Voice/AI Agent interface tests

## Voice Policy Test Requirements

### Simulated Voice Interaction
- **Trigger phrase simulation** required
- **Fallback handling** must be tested
- **Agent confirmation** ("You're speaking with…") must be tested explicitly
- **UI response validation** must match expected routing behavior

### Vault Logging Validation
- **API or mock layer validation** required
- **UI-only validation is insufficient**
- **Session logging** must be verified
- **Audit trail** must be complete

### Policy Compliance
- **Reference `/docs/VOICE_ACCESS_POLICY.md`** explicitly in each test file
- **All voice access states** must be tested
- **Local and external agent permissions** must be validated
- **Routing logic** (agnostic/isolated modes) must be tested

## Test Environment Requirements

### Environment Cleanliness
- **Fresh session state** must be initialized for each test run
- **UI context reuse** allowed if idempotent
- **Resource cleanup** required after each test

### Logging Infrastructure
- **All test runs logged** to `/logs/tests/ui/` with timestamp
- **Resource monitoring** for Voice/AI Agent interface tests
- **Central reporting** to `/tests/results/ui/summary.json`

### Environment Setup
- **File**: `tests/env/setup_ui_env.py`
- **Purpose**: Enforce UI test preconditions
- **Requirements**: Fresh session state, logging, resource monitoring

## Test Structure

### Feature Branch Requirements
All UI tests must be committed under feature branches with format:
- `feature/ui-test-[module/scope]`
- Examples:
  - `feature/ui-test-voice-routing`
  - `feature/ui-test-agent-interaction`
  - `feature/ui-test-voice-interface`
  - `feature/ui-test-vault-logging`

### Commit Message Format
Must include:
- `UI_TEST` prefix
- Feature ID (if applicable)
- Source of test directive (audit, sprint, etc.)

Examples:
- `UI_TEST: VOICE-001 - Voice routing compliance tests (Owner Directive)`
- `UI_TEST: UI-001 - Agent interaction screen tests (Audit)`
- `UI_TEST: VAULT-001 - Voice session logging tests (Policy)`

## Test Categories

### Voice Routing Compliance Tests
- **Feature ID**: VOICE-001
- **Source**: Owner Directive - UI Test Compliance & Execution
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Location**: `tests/feature/ui-test-voice-routing/`

### Agent Interaction Screen Tests
- **Feature ID**: UI-001
- **Source**: Owner Directive - Review all agent interaction screens
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Location**: `tests/feature/ui-test-agent-interaction/`

### Voice Interface Component Tests
- **Feature ID**: UI-002
- **Source**: Voice routing logic implementation
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Location**: `tests/feature/ui-test-voice-interface/`

### Vault Logging Tests
- **Feature ID**: VAULT-001
- **Source**: Voice session logging requirements
- **Policy Reference**: `/docs/VOICE_ACCESS_POLICY.md`
- **Location**: `tests/feature/ui-test-vault-logging/`

## Test Execution

### Prerequisites
1. **Environment setup**: Run `tests/env/setup_ui_env.py`
2. **Feature branch**: Ensure tests are on proper feature branch
3. **Dependencies**: Install required test dependencies

### Running Tests
```bash
# Run specific test category
python -m pytest tests/feature/ui-test-voice-routing/

# Run all UI tests
python -m pytest tests/feature/ui-test-*/

# Run with resource monitoring
python tests/env/setup_ui_env.py && python -m pytest tests/feature/ui-test-*/
```

### Test Results
- **Results stored**: `/tests/results/ui/` in JSON format
- **Central summary**: `/tests/results/ui/summary.json`
- **Logs**: `/logs/tests/ui/` with timestamp

## QA Review Requirements

### Before Merge
- **Peer review required** for all test files
- **Owner verification** via prompt if needed
- **Traceability documented** in `tests/TEST_REFERENCE.md`

### Compliance Checklist
- [ ] All tests committed under proper feature branches
- [ ] Commit messages include UI_TEST, feature ID, and source
- [ ] Tests reference audit sections and policy docs
- [ ] 100% pass rate achieved with edge cases
- [ ] JSON logging implemented where required
- [ ] Cross-platform validation completed
- [ ] Resource monitoring implemented for Voice/AI tests
- [ ] Central reporting updated
- [ ] QA review completed before merge
- [ ] Traceability documented in TEST_REFERENCE.md

## Infrastructure Integration

### Test Runner
- **File**: `tests/ui/runner_ui_tests.sh`
- **Purpose**: Unified test execution
- **Requirements**: Same runner and report structure as Core/system tests

### Pipeline Integration
- **Standalone job**: UI test suite executable independently
- **Nightly CI**: Integrated into continuous integration pipeline
- **JSON format**: All results logged to `/tests/results` in JSON format

## Documentation References

### Policy Documents
- `/docs/VOICE_ACCESS_POLICY.md` - Voice access rules and system behavior
- `/docs/process_refinement.md` - Process standards and compliance requirements

### Test Documentation
- `tests/TEST_REFERENCE.md` - Test traceability and references
- `/docs/process_refinement.md` - Test planning requirements and implementation standards
- `/docs/VOICE_ACCESS_POLICY.md` - Voice functionality test requirements
- `/docs/UI_ALIGNMENT_AUDIT.md` - UI screen validation requirements

### Audit Documentation
- Voice Access States
- Local Agent Voice Interaction Rules
- External Agent Voice Permissions
- Voice Routing Logic
- Voice Authentication
- Offline Mode Behavior
- Fallback & Error States
- Logging & Transparency
- Agent Identity & Confirmation
- Vault Logging

## Support

For questions about test implementation or compliance requirements, refer to:
- `tests/TEST_REFERENCE.md` for traceability
- `/docs/VOICE_ACCESS_POLICY.md` for voice policy requirements
- Owner directives for compliance standards 