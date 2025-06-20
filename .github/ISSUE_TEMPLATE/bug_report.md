---
name: 🐛 Bug Report (Task-Structured)
about: Report a bug with structured investigation and fix workflow
title: '[BUG] '
labels: 'bug, claude-ready, needs-investigation, task-workflow'
assignees: ''
---

## 🐛 Bug Report Overview
**Bug Type**: [ ] Crash/Error [ ] Incorrect Output [ ] Performance [ ] CLI Interface [ ] Other: ___
**Severity**: [ ] Critical [ ] High [ ] Medium [ ] Low

## 📋 Bug Resolution Workflow
This bug report follows a **structured investigation → diagnosis → fix → validation** workflow:

1. **🔍 Investigation**: Reproduce and analyze the issue
2. **📊 Diagnosis**: Identify root cause and impact
3. **🛠️ Fix Planning**: Create task list for resolution
4. **⚡ Implementation**: Execute fix tasks with validation

---

## 🔍 BUG INVESTIGATION SECTION

### 🐛 Problem Description
<!-- Provide a clear and concise description of the bug -->

### 🎯 Expected vs Actual Behavior
**Expected**: [What should happen]
**Actual**: [What actually happens]
**Impact**: [How this affects users]

### 🔄 Reproduction Steps
<!-- Provide detailed, repeatable steps -->
1. **Environment Setup**: [initial conditions]
2. **Command Executed**: `pyforge [command] [arguments]`
3. **Input Data**: [file type, size, source]
4. **Trigger Action**: [specific action that causes bug]
5. **Observed Result**: [what happens]

**Reproducibility**: [ ] Always [ ] Sometimes [ ] Rarely [ ] Once

### 💻 Environment Context
**System Information**:
- **OS**: [Windows 11, macOS 14.5, Ubuntu 22.04]
- **Python**: [3.10.12]
- **PyForge CLI**: [0.2.0 or commit hash]
- **Install Method**: [pip, source, conda]

**File Context** (if applicable):
- **Type**: [.xlsx, .mdb, .dbf, .pdf]
- **Size**: [2.5MB]
- **Source**: [Excel 2019, Access 2016, dBASE IV]
- **Sample**: [ ] Attached [ ] Available [ ] Sensitive

### 🚨 Error Evidence
```bash
# Command that fails
pyforge convert example.xlsx

# Complete error output
[Paste complete error message and stack trace here]
```

### 🔍 Investigation Commands for Claude
```bash
# Basic diagnostics
pyforge info [problem_file] --verbose
pyforge validate [problem_file]
pyforge formats | grep [file_type]

# System diagnostics  
python --version
pip show pyforge-cli
ls -la [problem_file]

# Debug mode
pyforge convert [problem_file] --debug --verbose
```

---

## 📊 ROOT CAUSE ANALYSIS

### 🎯 Initial Hypothesis
<!-- What do you think is causing this issue? -->

### 🔍 Areas to Investigate
- [ ] **Input Validation**: File format parsing issues
- [ ] **Data Processing**: Conversion logic errors
- [ ] **Error Handling**: Missing exception handling
- [ ] **CLI Interface**: Command parsing problems
- [ ] **Dependencies**: Library version conflicts
- [ ] **Environment**: OS/Python version specific
- [ ] **Performance**: Memory/resource limitations

### 📋 Investigation Tasks
**When Claude investigates, break down into these tasks:**

#### Investigation Phase
- [ ] **Reproduce Issue**: Confirm bug with provided steps
- [ ] **Analyze Error**: Examine stack trace and error patterns
- [ ] **Test Scope**: Determine which files/scenarios are affected
- [ ] **Check Recent Changes**: Review recent commits for related changes

#### Diagnosis Phase  
- [ ] **Root Cause**: Identify exact cause of the issue
- [ ] **Impact Assessment**: Determine scope of user impact
- [ ] **Fix Strategy**: Plan approach for resolution
- [ ] **Testing Strategy**: Define how to validate the fix

#### Implementation Phase
- [ ] **Fix Development**: Implement the actual fix
- [ ] **Unit Tests**: Add tests to prevent regression
- [ ] **Integration Tests**: Validate end-to-end scenarios
- [ ] **Documentation**: Update docs if behavior changes

#### Validation Phase
- [ ] **Original Case**: Verify original issue is resolved
- [ ] **Edge Cases**: Test related scenarios
- [ ] **Regression Testing**: Ensure no new issues introduced
- [ ] **Performance Impact**: Verify no performance degradation

---

## 🛠️ CLAUDE FIX IMPLEMENTATION

### File Areas to Examine
```bash
# Find related code patterns
grep -r "error_pattern" src/pyforge_cli/
grep -r "function_name" src/pyforge_cli/

# Key files likely involved
# - src/pyforge_cli/converters/[relevant_converter].py
# - src/pyforge_cli/main.py (CLI interface)
# - src/pyforge_cli/utils/ (utility functions)
# - tests/ (test coverage)
```

### Fix Implementation Checklist
- [ ] **Core Fix**: Primary issue resolution implemented
- [ ] **Error Handling**: Improved error messages and handling
- [ ] **Input Validation**: Enhanced validation if needed
- [ ] **Backwards Compatibility**: Existing functionality preserved
- [ ] **Performance**: No performance regression introduced

### Test Coverage Requirements
- [ ] **Unit Tests**: Test the specific fix
- [ ] **Integration Tests**: End-to-end scenarios
- [ ] **Regression Tests**: Prevent this specific bug
- [ ] **Edge Case Tests**: Handle similar scenarios

---

## ✅ RESOLUTION VALIDATION

### Fix Verification
- [ ] **Original Issue**: Bug no longer occurs with original reproduction steps
- [ ] **Similar Cases**: Related scenarios also work correctly
- [ ] **Error Messages**: Error handling is clear and helpful
- [ ] **Documentation**: Changes documented if needed

### Success Criteria
- [ ] Issue completely resolved for reported scenario
- [ ] No new bugs introduced by the fix
- [ ] Test coverage prevents regression
- [ ] User experience improved with better error handling
- [ ] Performance impact is acceptable

---

## 🔗 RELATED WORK
- **Related Issues**: #
- **Duplicate Issues**: #
- **Similar Bugs**: #
- **Affected Features**: [list features that might be impacted]

---

## 📅 PRIORITY ASSESSMENT
**Business Impact**:
- [ ] **Critical**: Blocks core functionality
- [ ] **High**: Affects many users or important workflows  
- [ ] **Medium**: Affects some users or edge cases
- [ ] **Low**: Minor issue with workarounds available

**Technical Complexity**: [Simple/Medium/Complex]
**Fix Timeline**: [estimate]

---

## 💡 ADDITIONAL CONTEXT
<!-- Any other context, workarounds, or relevant information -->

**Workarounds**: [If any workarounds are available]
**User Impact**: [How many users affected, severity of impact]
**Business Context**: [Why this matters for the project]

---

**For Maintainers - Bug Resolution Workflow:**
- [ ] Bug confirmed and severity assessed
- [ ] Investigation task list created
- [ ] Root cause identified and documented
- [ ] Fix implementation approach approved
- [ ] Testing strategy validated
- [ ] Resolution completed and verified