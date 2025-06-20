# Pull Request

## 📋 Description
<!-- Provide a clear and concise description of what this PR does -->

## 🔗 Related Issues
<!-- Link the issue(s) this PR addresses -->
- Fixes #
- Closes #
- Related to #

## 🔄 Type of Change
<!-- Mark the relevant option with an "x" -->
- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that causes existing functionality to not work as expected)
- [ ] 📚 Documentation update (changes to documentation only)
- [ ] 🔧 Refactoring (code changes that neither fix a bug nor add a feature)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test improvement/addition
- [ ] 🏗️ Build/CI changes

## 🧪 Testing
<!-- Describe the testing you performed -->
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] All existing tests pass

### Test Commands Run:
```bash
# Example test commands
python -m pytest tests/
pyforge convert test_files/sample.xlsx --verbose
pyforge validate test_files/
```

## 📝 Changes Made
<!-- List the specific changes made in this PR -->
- [ ] Added/modified files:
  - `src/pyforge_cli/...`
  - `tests/...`
  - `docs/...`
- [ ] Key changes:
  - Change 1
  - Change 2
  - Change 3

## 🔍 Code Quality Checklist
<!-- Ensure code quality standards are met -->
- [ ] Code follows project coding standards
- [ ] Self-review completed
- [ ] Code comments added where necessary
- [ ] No sensitive information (passwords, keys, etc.) included
- [ ] Error handling implemented appropriately
- [ ] Performance implications considered

## 📚 Documentation
<!-- Documentation changes made -->
- [ ] CLI help text updated
- [ ] Documentation website updated
- [ ] README updated (if applicable)
- [ ] Code comments added/updated
- [ ] Examples updated/added

## 🔄 Backwards Compatibility
<!-- Address compatibility concerns -->
- [ ] This change is backwards compatible
- [ ] Breaking changes are documented
- [ ] Migration guide provided (if needed)
- [ ] Deprecation warnings added (if applicable)

## 🖼️ Screenshots/Output
<!-- If applicable, add screenshots or command output -->
```
Example output from running the new/fixed functionality
```

## ⚡ Performance Impact
<!-- If applicable, describe performance implications -->
- [ ] No significant performance impact
- [ ] Performance improved
- [ ] Performance impact acceptable for the benefit
- [ ] Benchmarks included

## 🚀 Deployment Notes
<!-- Any special deployment considerations -->
- [ ] No special deployment requirements
- [ ] Requires environment variable changes
- [ ] Requires dependency updates
- [ ] Other: _______________

## 🔍 Claude Code Review Assistance
<!-- Information to help Claude review this PR -->
```bash
# Key files to review
git diff --name-only main...feature-branch

# Test the changes
pyforge convert examples/test.xlsx --verbose
python -m pytest tests/test_new_feature.py -v
```

## 📋 Reviewer Checklist
<!-- For reviewers to complete -->
- [ ] Code review completed
- [ ] Testing strategy adequate
- [ ] Documentation is sufficient
- [ ] No security concerns
- [ ] Performance is acceptable
- [ ] Ready to merge

---
**Merge Requirements:**
- [ ] All checks passing
- [ ] At least one approval
- [ ] No outstanding review comments
- [ ] Branch is up to date with main