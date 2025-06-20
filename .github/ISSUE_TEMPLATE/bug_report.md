---
name: 🐛 Bug Report
about: Report a bug in PyForge CLI for investigation and fixing
title: '[BUG] '
labels: 'bug, claude-ready, needs-investigation'
assignees: ''
---

## 🐛 Problem Description
<!-- Provide a clear and concise description of the bug -->

## 🎯 Expected Behavior
<!-- Describe what you expected to happen -->

## 📋 Current Behavior
<!-- Describe what actually happened -->

## 🔄 Steps to Reproduce
<!-- Provide detailed steps to reproduce the issue -->
1. 
2. 
3. 
4. 

## 💻 Environment Information
<!-- Complete this information to help with debugging -->
- **OS**: [e.g., Windows 11, macOS 14.5, Ubuntu 22.04]
- **Python Version**: [e.g., 3.10.12]
- **PyForge CLI Version**: [e.g., 0.2.0 or commit hash]
- **Installation Method**: [e.g., pip, source, conda]

## 📁 Sample Files
<!-- If applicable, provide information about the files causing issues -->
- **File Type**: [e.g., .xlsx, .mdb, .dbf, .pdf]
- **File Size**: [e.g., 2.5MB]
- **File Source**: [e.g., Excel 2019, Access 2016, dBASE IV]
- **Sample Available**: [Yes/No - attach if possible and not sensitive]

## 🚨 Error Output
<!-- Include the complete error message and stack trace -->
```
Paste the complete error output here
```

## 🔍 Claude Investigation Commands
<!-- Commands to help Claude investigate the issue -->
```bash
# Basic file information
pyforge info [your_file_here]

# Verbose conversion attempt
pyforge convert [your_file_here] --verbose

# Validation check
pyforge validate [your_file_here]

# List supported formats
pyforge formats
```

## 📊 Additional Context
<!-- Add any other context about the problem here -->
- [ ] Issue occurs with multiple files
- [ ] Issue is reproducible consistently
- [ ] Issue affects specific file types only
- [ ] Issue started after recent update
- [ ] Workaround available (describe below)

## 🎯 Acceptance Criteria
<!-- What needs to be done to consider this issue resolved -->
- [ ] Bug is fixed and no longer occurs
- [ ] Fix includes appropriate error handling
- [ ] Test case added to prevent regression
- [ ] Documentation updated if needed
- [ ] Validation against similar files confirms fix

## 🔗 Related Issues
<!-- Link any related issues or PRs -->
- Related to #
- Duplicate of #
- Blocks #

---
**For PyForge CLI Maintainers:**
- [ ] Issue confirmed and reproduced
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Tests added
- [ ] Documentation updated