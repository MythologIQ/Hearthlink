# Hearthlink

## Overview
Hearthlink is an AI agent orchestration system with voice interaction capabilities, designed for secure, multi-agent collaboration and user assistance.

## Voice Interaction System

### Voice Routing & Agent Management
- **Multi-Agent Support**: Alden, Alice, Mimic, Sentry, and external agents
- **Voice HUD**: Real-time voice input display and agent selection interface
- **Misroute Recovery**: Alden handles all voice misroutes via intelligent recovery dialogue
- **Agent Deference**: Agents can suggest better-suited agents for specific tasks

### Voice Policy Compliance
- **Local Agents**: Fully conversational with name-based addressing
- **External Agents**: Disabled by default, require explicit permission activation
- **Offline Mode**: Dynamic detection with local agent fallback
- **Authentication**: Secure mode activation with challenge/PIN system

## Test-Driven Development

### Distributed Test Policy Structure
Test requirements are distributed across multiple source documents rather than centralized in a single test plan:

- **Test Planning Requirements**: `/docs/process_refinement.md`
- **Voice Functionality Tests**: `/docs/VOICE_ACCESS_POLICY.md`
- **UI Screen Validation**: `/docs/UI_ALIGNMENT_AUDIT.md`
- **Test Reference & Traceability**: `/docs/TEST_REFERENCE.md`

### Test Implementation Standards
- **Feature Branches**: All tests under `feature/ui-test-*` branches
- **Commit Format**: `UI_TEST: [FEATURE_ID] - [Description] (Source: [audit/sprint/etc.])`
- **Pass Rate**: 100% required for merge approval
- **JSON Logging**: Required for all state/data tests

## Documentation Structure

### Core Policy Documents
- **Voice Access Policy**: `/docs/VOICE_ACCESS_POLICY.md` - Voice interaction rules and system behavior
- **UI Alignment Audit**: `/docs/UI_ALIGNMENT_AUDIT.md` - Approved UI screens and validation requirements
- **Process Refinement**: `/docs/process_refinement.md` - Development standards and compliance requirements

### User Documentation
- **User Manual**: `/docs/USER_MANUAL.md` - Voice interaction guide and troubleshooting
- **Feature Map**: `/docs/FEATURE_MAP.md` - Feature implementation status and traceability

### Test Documentation
- **Test Reference**: `/docs/TEST_REFERENCE.md` - Test traceability and compliance documentation
- **Sprint Completion Log**: `/docs/SPRINT_COMPLETION_LOG.md` - Sprint status and implementation uncertainties

## Quick Start

### Voice Interaction
1. **Enable Voice**: Ensure voice interaction is enabled in settings
2. **Address Agents**: Say "Hey Alden" or "Alice, can you help me..."
3. **Use Voice HUD**: Visual interface for agent selection and input display
4. **Trust Recovery**: Let Alden handle misroutes and suggest better agents

### Development
1. **Feature Branches**: Create `feature/ui-test-*` branches for all UI work
2. **Test Compliance**: Ensure 100% test pass rate before merge
3. **Documentation**: Update relevant policy and audit documents
4. **Traceability**: Link all changes to source documents and feature IDs

## Architecture

### Core Components
- **Core**: Agent orchestration and session management
- **Vault**: Memory management and audit logging
- **Synapse**: Plugin management and external integrations
- **Sentry**: Security monitoring and kill switch functionality

### Voice System
- **Voice HUD**: Universal voice interface with live transcript
- **Agent Routing**: Intelligent routing with misroute recovery
- **Authentication**: Secure mode activation for system modifications
- **Logging**: Complete session logging and audit trail

## Support

For questions about voice interaction, testing, or development:
- **Voice Policy**: `/docs/VOICE_ACCESS_POLICY.md`
- **UI Requirements**: `/docs/UI_ALIGNMENT_AUDIT.md`
- **Process Standards**: `/docs/process_refinement.md`
- **Contact**: `system@hearthlink.local`
