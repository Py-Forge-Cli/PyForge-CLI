---
name: ✨ Feature Request (PRD-Based)
about: Suggest a new feature using structured PRD → Tasks workflow
title: '[FEATURE] Automated PyPI Deployment with setuptools-scm and Trusted Publishing'
labels: 'enhancement, claude-ready, feature-request, prd-workflow, ci-cd, deployment'
assignees: ''
---

## 🚀 Feature Request Overview

**Feature Name**: Automated PyPI Deployment System
**Type**: [X] Enhancement [ ] Integration [ ] Performance [ ] Other: CI/CD Pipeline

## 📋 Implementation Workflow

This feature request follows the **PRD → Tasks → Implementation** workflow:

1. **📝 PRD Creation**: Complete this issue to create a comprehensive PRD document
2. **🎯 Task Generation**: Generate structured task list from approved PRD  
3. **⚡ Implementation**: Execute tasks one-by-one with approval checkpoints

---

## 📋 PRD REQUIREMENTS GATHERING

### 🎯 Problem Statement

**Current Issues:**
- Manual version management requires updating version numbers in multiple files
- Hard-coded versions (0.5.5.dev13) create inconsistencies between pyproject.toml and __init__.py
- Using API tokens for PyPI authentication (security risk)
- No automated development version deployment to PyPI Test
- Manual release process prone to human error
- Developers cannot easily test latest development builds

**User Pain Points:**
- Maintainers must manually bump versions for every change
- Users cannot install and test latest development versions
- Release process requires manual coordination
- Version mismatches cause confusion and build failures

### 💡 Proposed Solution Overview

Implement a fully automated PyPI deployment system using modern best practices:

1. **Automated Version Management**: Use setuptools-scm to generate versions from Git commits and tags
2. **Dual Deployment Pipeline**: Auto-deploy development versions to PyPI Test, controlled releases to PyPI.org
3. **Trusted Publishing**: Replace API tokens with PyPI's trusted publishing for enhanced security
4. **Continuous Testing**: Every main branch commit creates a testable package on PyPI Test

### 👥 Target Users

**Primary Users:**
- **Maintainers**: Need streamlined release process without manual version management
- **Contributors**: Need to test their changes in real deployment scenarios
- **End Users**: Need access to stable releases and ability to test development versions

**Skill Levels:**
- Maintainers: Advanced (Git workflow, PyPI publishing)
- Contributors: Intermediate (basic Git knowledge)
- End Users: Basic (pip install commands)

### 🔄 User Journey

#### Development Workflow
1. **Developer commits** to main branch: `git push origin main`
2. **GitHub Actions triggers**: Automated build and version generation
3. **Auto-deploy to PyPI Test**: Package available as `0.6.0.dev23`
4. **Developer tests**: `pip install -i https://test.pypi.org/simple/ pyforge-cli`
5. **Validation**: Developer confirms changes work in real environment

#### Release Workflow
1. **Maintainer creates tag**: `git tag v0.6.0 && git push origin v0.6.0`
2. **GitHub release created**: Manual or automated release notes
3. **Auto-deploy to PyPI**: Package available as `0.6.0`
4. **Users install**: `pip install pyforge-cli` gets latest stable version
5. **Distribution**: Package automatically distributed worldwide

### 📊 Requirements Breakdown

#### Functional Requirements
- [X] **Automated Version Generation**: setuptools-scm generates versions from Git history
- [X] **Development Deployment**: Every main branch commit deploys to PyPI Test
- [X] **Production Deployment**: Git tags trigger deployment to PyPI.org
- [X] **Version Consistency**: Single source of truth for version numbers
- [X] **Security**: Use PyPI trusted publishing instead of API tokens
- [X] **Build Validation**: All deployments pass tests before publishing

#### Non-Functional Requirements  
- [X] **Performance**: Deployment completes within 5 minutes of commit/tag
- [X] **Compatibility**: Works with existing Hatchling-based build system migration
- [X] **Usability**: Zero configuration required for developers after initial setup
- [X] **Reliability**: Robust error handling and rollback capabilities
- [X] **Security**: No secrets stored in repository, trusted publishing only

### 🖥️ Command Line Interface Design

```bash
# No new CLI commands required - this is infrastructure

# Users benefit from improved installation experience:
# Development versions (auto-deployed)
pip install -i https://test.pypi.org/simple/ pyforge-cli
# Gets: pyforge-cli-0.6.0.dev23

# Production versions (manual releases)
pip install pyforge-cli
# Gets: pyforge-cli-0.6.0

# Version introspection
pyforge --version
# Output: 0.6.0.dev23 or 0.6.0
```

### 📁 Input/Output Specifications

**Inputs:**
- Git commits to main branch
- Git tags (v0.6.0, v1.0.0, etc.)
- GitHub release events
- pyproject.toml configuration

**Outputs:**
- Python wheel (.whl) and source distribution (.tar.gz)
- PyPI Test packages (development versions)
- PyPI.org packages (stable versions)
- Automated version files (_version.py)
- GitHub release artifacts

**Configuration Files:**
- pyproject.toml (setuptools-scm config)
- .github/workflows/deploy.yml (CI/CD pipeline)
- GitHub environment settings (PyPI trusted publishing)

### 🔍 Technical Architecture

**Core Components:**
1. **Build System Migration**: Hatchling → setuptools + setuptools-scm
2. **Version Management**: setuptools-scm automatic version generation
3. **CI/CD Pipeline**: Enhanced GitHub Actions workflow
4. **Authentication**: PyPI trusted publishing configuration
5. **Environment Management**: Separate PyPI Test and Production environments

**Dependencies:**
- setuptools>=64
- setuptools-scm>=8
- GitHub Actions: pypa/gh-action-pypi-publish@release/v1

**Integration Points:**
- Git history (tags, commits, branches)
- GitHub Actions (workflow triggers)
- PyPI trusted publishing (authentication)
- Existing package structure (minimal changes)

**Data Flow:**
```
Git Commit → GitHub Actions → Build Package → Version from Git → Deploy to PyPI Test
Git Tag → GitHub Actions → Build Package → Clean Version → Deploy to PyPI.org
```

### 🧪 Testing Strategy

**Unit Tests:**
- Version generation from different Git states
- Package metadata validation
- Build system compatibility

**Integration Tests:**
- End-to-end deployment to PyPI Test
- Version consistency across package files
- Installation testing from both repositories

**Performance Tests:**
- Deployment time benchmarks (<5 minutes)
- Build artifact size validation
- Network reliability testing

**Edge Cases:**
- Invalid Git tags (non-semver)
- Network failures during deployment
- PyPI service outages
- Version conflicts and rollbacks

---

## 🎯 PRD APPROVAL CHECKLIST

**Complete this section before generating tasks:**

- [X] Problem statement clearly defines user pain points
- [X] Solution approach is technically feasible  
- [X] Requirements are specific and measurable
- [X] CLI interface follows project conventions (no new commands needed)
- [X] Testing strategy covers all scenarios
- [X] Performance requirements are realistic (<5 min deployment)
- [X] Implementation approach is approved (setuptools-scm + trusted publishing)

---

## 📋 TASK GENERATION TRIGGER

**Once PRD is approved, use this section to generate implementation tasks:**

### Task List Creation
- [ ] **Ready to generate tasks**: PRD approved and complete
- [ ] **Task file created**: `/tasks/tasks-automated-pypi-deployment.md`
- [ ] **Implementation started**: First task marked in_progress

### Claude Implementation Commands
```bash
# Generate PRD document
"Create a PRD for automated PyPI deployment based on the requirements above"

# Generate task list from PRD  
"Generate tasks from /tasks/prd-automated-pypi-deployment.md"

# Start implementation
"Start working on /tasks/tasks-automated-pypi-deployment.md"
```

---

## 🔍 CLAUDE GUIDANCE SECTION

### File Structure for Implementation
```
/tasks/
  ├── prd-automated-pypi-deployment.md      # Product Requirements Document
  ├── tasks-automated-pypi-deployment.md    # Implementation task list
  └── ...

Files to Modify:
├── pyproject.toml                          # Build system and setuptools-scm config
├── src/pyforge_cli/__init__.py            # Dynamic version import
├── .github/workflows/publish.yml          # Enhanced CI/CD pipeline
├── .gitignore                             # Ignore auto-generated _version.py
└── @docs/                                 # Documentation updates
```

### Key Investigation Areas
```bash
# Examine current build configuration
cat pyproject.toml | grep -A 10 "build-system"
cat pyproject.toml | grep version

# Check current GitHub Actions
cat .github/workflows/publish.yml

# Verify current version handling
grep -r "__version__" src/pyforge_cli/
grep -r "version" src/pyforge_cli/

# Test current build process
python -m build
```

### Implementation Checkpoints
- [ ] **Phase 1**: Migrate build system from Hatchling to setuptools-scm
- [ ] **Phase 2**: Configure automated version generation and validation
- [ ] **Phase 3**: Update GitHub Actions workflow with trusted publishing
- [ ] **Phase 4**: Setup PyPI environments and test deployment pipeline
- [ ] **Phase 5**: Comprehensive testing and documentation updates

---

## 📊 SUCCESS CRITERIA

- [ ] PRD document created and approved
- [ ] Task list generated with clear acceptance criteria  
- [ ] All tasks completed with user approval at each step
- [ ] Every main branch commit auto-deploys development version to PyPI Test
- [ ] Git tags auto-deploy stable versions to PyPI.org
- [ ] Version numbers generated automatically from Git history
- [ ] No manual version management required
- [ ] Trusted publishing replaces API token authentication
- [ ] Deployment completes within 5 minutes
- [ ] Zero breaking changes to existing functionality
- [ ] Documentation updated with new deployment process

---

## 🔗 RELATED WORK

- **Related Issues**: #XX (if any existing deployment issues)
- **Depends On**: Current Hatchling build system
- **Blocks**: Future automated release management features
- **Similar Features**: Existing publish.yml workflow (to be enhanced)

---

## 📅 PRIORITIZATION

- **Business Impact**: **High** - Streamlines development and release process
- **Technical Complexity**: **Medium** - Well-established tools and patterns
- **User Demand**: **High** - Enables faster iteration and testing
- **Implementation Timeline**: **3-5 days** (setup, testing, documentation)

**Dependencies:**
- PyPI trusted publishing setup (requires PyPI account access)
- GitHub repository environment configuration
- Migration testing on development branch

---

## 💡 IMPLEMENTATION NOTES

### Migration Strategy
1. **Parallel Setup**: Configure new system alongside existing
2. **Testing Branch**: Test thoroughly on feature branch before main
3. **Gradual Rollout**: Deploy to PyPI Test first, validate, then enable production
4. **Rollback Plan**: Keep existing system as backup during transition

### Security Considerations
- Remove API token secrets after trusted publishing is confirmed working
- Environment protection rules for production deployments
- Audit trail for all deployments through GitHub Actions logs

### Future Enhancements
- Automated changelog generation from conventional commits
- Pre-release deployment workflows (alpha, beta, rc)
- Integration with GitHub Releases for automated release notes
- Slack/Discord notifications for deployment events

---

**For Maintainers - PRD Workflow:**
- [X] Issue reviewed and PRD requirements complete
- [X] Technical feasibility confirmed (setuptools-scm is industry standard)
- [X] PRD document creation approved
- [ ] Task generation authorized
- [ ] Implementation approach validated

**Next Steps:**
1. Generate comprehensive PRD document
2. Create detailed implementation task list
3. Begin Phase 1: Build system migration
4. Test and validate each phase before proceeding