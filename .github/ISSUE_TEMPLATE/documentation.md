---
name: 📚 Documentation Improvement
about: Suggest improvements to documentation, examples, or help text
title: '[DOCS] '
labels: 'documentation, claude-ready, improvement'
assignees: ''
---

## 📚 Documentation Issue
<!-- Describe what documentation needs to be improved -->

## 📍 Location
<!-- Where is the documentation that needs improvement? -->
- [ ] CLI Help Text (`pyforge --help`, `pyforge convert --help`)
- [ ] README.md
- [ ] Documentation Website ([https://py-forge-cli.github.io/PyForge-CLI/](https://py-forge-cli.github.io/PyForge-CLI/))
- [ ] API Documentation
- [ ] Code Comments
- [ ] Examples/Tutorials
- [ ] Error Messages
- [ ] Other: _______________

## 🎯 Specific Pages/Sections
<!-- List the specific files or pages that need updates -->
- File/Page: `docs/path/to/file.md`
- Section: "Specific Section Name"
- URL: https://py-forge-cli.github.io/PyForge-CLI/section/

## ❌ Current State
<!-- What is currently wrong, missing, or unclear? -->

## ✅ Proposed Improvement
<!-- What should be changed, added, or clarified? -->

## 👥 User Perspective
<!-- How does this improvement help users? -->
- **User Type**: [Beginner/Intermediate/Advanced/All]
- **Use Case**: [What are they trying to accomplish?]
- **Pain Point**: [What confusion or difficulty does this address?]

## 📋 Specific Changes Needed
<!-- Break down the specific changes required -->
- [ ] Add missing information about [topic]
- [ ] Clarify confusing explanation of [concept]
- [ ] Add code examples for [use case]
- [ ] Fix incorrect information about [detail]
- [ ] Update outdated screenshots/examples
- [ ] Improve organization/structure
- [ ] Add troubleshooting section
- [ ] Other: _______________

## 📝 Content Suggestions
<!-- If you have specific content suggestions, include them here -->
```markdown
<!-- Proposed content goes here -->
```

## 🔍 Examples to Include
<!-- Suggest specific examples that would be helpful -->
```bash
# Example commands to document
pyforge convert example.xlsx --verbose
pyforge info database.mdb
```

## 🔍 Claude Content Development
<!-- Guidance for Claude when updating documentation -->
```bash
# Files to examine for current content
ls docs/
grep -r "topic" docs/
cat docs/current-file.md

# Related documentation to check for consistency
docs/converters/
docs/reference/
```

## 🌟 Additional Context
<!-- Any other context about this documentation improvement -->
- **Frequency**: How often do users encounter this issue?
- **Impact**: How much does this confusion affect user experience?
- **Related Issues**: Are there GitHub issues or discussions about this?

## 📋 Success Criteria
<!-- What does good documentation look like for this topic? -->
- [ ] Information is accurate and up-to-date
- [ ] Examples are clear and working
- [ ] Common use cases are covered
- [ ] Troubleshooting guidance is provided
- [ ] Content is well-organized and easy to find
- [ ] Language is clear and accessible
- [ ] Code examples are tested and functional

## 🔗 Related Issues/PRs
<!-- Link related issues or PRs -->
- Related to #
- Documentation for #
- Addresses confusion in #

## 📊 Priority Level
<!-- Help prioritize this documentation improvement -->
- [ ] **Critical**: Blocking user adoption or causing significant confusion
- [ ] **High**: Important for user experience, affects many users
- [ ] **Medium**: Helpful improvement, affects some users
- [ ] **Low**: Nice to have, minor improvement

---
**For PyForge CLI Maintainers:**
- [ ] Documentation improvement approved
- [ ] Content reviewed for accuracy
- [ ] Examples tested and verified
- [ ] Changes implemented
- [ ] Documentation site regenerated
- [ ] Links and navigation verified