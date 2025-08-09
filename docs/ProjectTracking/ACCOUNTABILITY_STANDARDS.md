# Hearthlink Project Tracking Accountability Standards
## Mandatory Requirements for All Project Documentation

**Version**: 1.0  
**Date**: 2025-07-24  
**Status**: ACTIVE - All project tracking must follow these standards  

---

## DOCUMENTATION STANDARDS (MANDATORY)

### Required Elements for ALL Project Components
Every project component tracking document MUST include:

1. **Goal**: Clear, measurable objective statement
2. **Plan**: Step-by-step implementation strategy  
3. **Strategy**: Technical approach and architecture decisions
4. **Work Completed**: Evidence-based progress with verification
5. **Verification**: Testing results, command outputs, timestamps
6. **Success Criteria**: Measurable completion metrics (percentage-based)
7. **Status Measurement**: Current completion percentage with evidence

### Document Structure Template
```markdown
# Component Name: [Completion %] STATUS
**Last Updated**: YYYY-MM-DD HH:MM:SS UTC  
**Status**: [Active/Blocked/Complete/Failed]  
**Evidence Location**: [Path to verification files]

## Goal
[Clear objective statement]

## Plan  
[Implementation strategy]

## Strategy
[Technical approach]

## Work Completed
[Evidence-based progress with timestamps]

## Verification
[Test results, command outputs, proof of functionality]

## Success Criteria
[Measurable completion metrics]

## Status Measurement
[Current percentage with calculation basis]
```

---

## ACCOUNTABILITY PROTOCOL (CRITICAL)

### Third-Party Evaluation Mindset
- **Perspective**: All assessments must be as if reviewed by external auditor
- **Skepticism**: Challenge all claims with evidence requirements
- **Objectivity**: Remove personal bias from status assessments
- **Rigor**: Apply professional-level scrutiny to all progress claims

### Evidence-Based Claims Only
ALL progress statements must include:
- **Timestamp**: Exact date and time of verification
- **Command Used**: Complete command executed for testing
- **Full Output**: Complete response or error message (no truncation)
- **Evidence Location**: File path to logs, screenshots, or verification data
- **Reproducibility**: Sufficient detail for independent verification

### "No Data Available" Standard
When information is missing or unknown:
- **Explicit Statement**: Must state "No data available" clearly
- **No Assumptions**: Never assume functionality without testing
- **No Placeholders**: No "TODO" or "TBD" without timeline
- **Investigation Required**: Mark areas needing data collection

---

## PROHIBITED PRACTICES

### Absolutely Forbidden
- ❌ **Simulated Data**: No demo values, mock responses, or example outputs
- ❌ **Assumed Functionality**: No status claims without direct testing
- ❌ **Generic Progress**: No "working on it" without specific evidence
- ❌ **Percentage Guessing**: No completion percentages without measurable basis
- ❌ **Future Tense Claims**: No "will work" statements without current proof

### Required Replacements
- ✅ **Real Test Data**: Only actual command outputs and responses
- ✅ **Verified Functionality**: Only tested and confirmed capabilities
- ✅ **Specific Evidence**: Detailed progress with timestamps and commands
- ✅ **Calculated Percentages**: Completion based on measurable criteria
- ✅ **Present Tense Facts**: Only current, verified status statements

---

## DAILY LOG REQUIREMENTS

### Log Creation Standards
- **File Naming**: `YYYY-MM-DD.md` format only
- **Location**: `docs/ProjectTracking/Daily/` directory
- **Content**: Evidence-based work completed that day
- **Verification**: All claims backed by timestamps and commands

### Retention Policy
- **Duration**: 7-day retention cycle
- **Cleanup**: Delete logs older than 7 days
- **Archive**: No archival - logs are for current context only
- **Purpose**: Maintain recent work history for continuity

### Daily Log Template
```markdown
# Daily Project Log: YYYY-MM-DD
## [Session Description]

**Timestamp**: YYYY-MM-DD HH:MM:SS UTC  
**Session Type**: [Description]  
**Accountability Standard**: Third-party evaluation mindset applied  

## WORK COMPLETED (Evidence-Based)
[List all work with evidence]

## CRITICAL FINDINGS DOCUMENTED  
[Any blocker discoveries or major findings]

## NEXT SESSION REQUIREMENTS
[Specific actions for next session]

## ACCOUNTABILITY VERIFICATION
[Confirmation of standards applied]
```

---

## PROGRESS MEASUREMENT STANDARDS

### Completion Percentage Calculation
Percentages must be based on measurable criteria:
- **0%**: No work started or planning only
- **25%**: Basic implementation exists with major gaps
- **50%**: Core functionality working but incomplete
- **75%**: Most features complete with minor issues
- **100%**: Full functionality verified and tested

### Status Classifications
- **ACTIVE**: Currently being worked on with recent progress
- **BLOCKED**: Cannot proceed due to dependencies or issues  
- **COMPLETE**: All success criteria met with verification
- **FAILED**: Cannot be completed as designed (requires redesign)
- **PAUSED**: Temporarily stopped but can resume

### Evidence Requirements by Status
- **ACTIVE**: Recent work evidence (within 2 days)
- **BLOCKED**: Clear blocker identification with impact assessment
- **COMPLETE**: Full verification testing with results
- **FAILED**: Detailed failure analysis with lessons learned
- **PAUSED**: Reason for pause and resumption criteria

---

## QUALITY ASSURANCE CHECKLIST

### Before Updating Any Document
- [ ] Third-party perspective applied to all assessments
- [ ] All claims backed by specific evidence with timestamps
- [ ] "No data available" explicitly stated where information missing
- [ ] No simulated or demo data included
- [ ] Completion percentages based on measurable criteria
- [ ] Commands and outputs included for verification
- [ ] File paths provided for evidence location
- [ ] Status matches actual current state (not aspirational)

### Document Review Requirements  
- [ ] Evidence chain is complete and verifiable
- [ ] No assumptions made about untested functionality
- [ ] All claims would pass external audit review
- [ ] Specific rather than generic progress statements
- [ ] Timeline information included where applicable

---

## ENFORCEMENT

### Compliance Monitoring
- All project tracking documents subject to accountability review
- Evidence requirements are mandatory, not optional
- Non-compliance must be corrected before proceeding
- Standards apply to all team members and external contributors

### Standard Violations
Violations requiring immediate correction:
- Progress claims without evidence
- Simulated or demo data usage  
- Assumed functionality without testing
- Generic status updates without specifics
- Missing timestamps or command documentation

**These standards are mandatory for all Hearthlink project tracking and documentation.**