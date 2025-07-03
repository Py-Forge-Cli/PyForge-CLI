# Product Requirements Document: Automated PyPI Deployment System

## 1. Executive Summary

### 1.1 Project Overview
Implement a fully automated PyPI deployment system for PyForge CLI that replaces manual version management with setuptools-scm, enables continuous deployment to PyPI Test, and uses trusted publishing for enhanced security.

### 1.2 Business Case
- **Current Pain**: Manual version management, security risks with API tokens, no development version testing
- **Solution**: Automated version generation, dual deployment pipeline, trusted publishing
- **Impact**: Streamlined development, faster user feedback, reduced maintenance overhead

### 1.3 Success Metrics
- Development versions auto-deployed to PyPI Test within 5 minutes of commit
- Production versions auto-deployed to PyPI.org on Git tags
- Zero manual version management required
- 100% deployment success rate

## 2. Problem Statement

### 2.1 Current Issues
1. **Manual Version Management**: Developers must manually update version numbers in `pyproject.toml` and `__init__.py`
2. **Security Risk**: Using API tokens for PyPI authentication stored as GitHub secrets
3. **No Development Testing**: Users cannot test latest development versions
4. **Human Error**: Manual release process prone to version mismatches and deployment failures
5. **Slow Feedback**: Contributors cannot easily validate their changes in production-like environment

### 2.2 Impact Assessment
- **Maintainers**: Significant time spent on version management and release coordination
- **Contributors**: Cannot test changes in real deployment scenarios
- **End Users**: Limited access to latest fixes and features
- **Project Health**: Inconsistent versions create confusion and build failures

## 3. Solution Overview

### 3.1 Core Components
1. **Build System Migration**: Transition from Hatchling to setuptools + setuptools-scm
2. **Automated Version Generation**: Use Git history to generate version numbers
3. **Dual Deployment Pipeline**: Separate workflows for development and production
4. **Trusted Publishing**: Replace API tokens with PyPI's trusted publishing
5. **Environment Isolation**: Separate PyPI Test and Production environments

### 3.2 Technical Architecture
```
Git Commit → GitHub Actions → Version Generation → Build → Deploy to PyPI Test
Git Tag → GitHub Actions → Version Generation → Build → Deploy to PyPI.org
```

## 4. User Requirements

### 4.1 Primary Users
- **Maintainers**: Need streamlined release process without manual version management
- **Contributors**: Need to test their changes in real deployment scenarios  
- **End Users**: Need access to stable releases and development versions

### 4.2 User Stories
1. **As a maintainer**, I want releases to be automated so I can focus on development
2. **As a contributor**, I want to test my changes in a real environment before merge
3. **As an end user**, I want access to the latest fixes without waiting for formal releases

## 5. Functional Requirements

### 5.1 Automated Version Management (REQ-001)
- **Description**: Use setuptools-scm to generate versions from Git commits and tags
- **Acceptance Criteria**:
  - Version numbers generated automatically from Git history
  - Development versions follow pattern: `0.6.0.dev23+g1a2b3c4`
  - Release versions follow pattern: `0.6.0`
  - Single source of truth for version information

### 5.2 Development Deployment (REQ-002)
- **Description**: Auto-deploy development versions to PyPI Test on main branch commits
- **Acceptance Criteria**:
  - Every commit to main branch triggers deployment
  - Package available on PyPI Test within 5 minutes
  - Users can install with: `pip install -i https://test.pypi.org/simple/ pyforge-cli`
  - Deployment skipped if tests fail

### 5.3 Production Deployment (REQ-003)
- **Description**: Auto-deploy stable versions to PyPI.org on Git tags
- **Acceptance Criteria**:
  - Git tags matching `v*` pattern trigger deployment
  - Clean version numbers (no dev suffix)
  - Users can install with: `pip install pyforge-cli`
  - GitHub release artifacts automatically attached

### 5.4 Security Enhancement (REQ-004)
- **Description**: Use PyPI trusted publishing instead of API tokens
- **Acceptance Criteria**:
  - No API tokens stored in GitHub secrets
  - Trusted publishing configured for both PyPI Test and Production
  - Deployment permissions scoped to specific repositories
  - Audit trail maintained through GitHub Actions

### 5.5 Build Validation (REQ-005)
- **Description**: All deployments must pass comprehensive validation
- **Acceptance Criteria**:
  - Tests must pass before deployment
  - Package metadata validated
  - Distribution files checked for completeness
  - Installation testing performed

## 6. Non-Functional Requirements

### 6.1 Performance (NFR-001)
- **Requirement**: Deployment completes within 5 minutes of trigger
- **Measurement**: GitHub Actions workflow completion time
- **Rationale**: Fast feedback for development iterations

### 6.2 Reliability (NFR-002)
- **Requirement**: 99.5% deployment success rate
- **Measurement**: Successful deployments / Total deployment attempts
- **Rationale**: Consistent, dependable deployment process

### 6.3 Security (NFR-003)
- **Requirement**: No secrets stored in repository
- **Measurement**: Zero API tokens in GitHub secrets after migration
- **Rationale**: Enhanced security posture

### 6.4 Compatibility (NFR-004)
- **Requirement**: Zero breaking changes to existing functionality
- **Measurement**: All existing tests continue to pass
- **Rationale**: Smooth transition for existing users

## 7. Technical Specifications

### 7.1 Build System Configuration
```toml
[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"

[project]
dynamic = ["version"]

[tool.setuptools_scm]
version_file = "src/pyforge_cli/_version.py"
```

### 7.2 Version Import Pattern
```python
# src/pyforge_cli/__init__.py
from ._version import __version__
```

### 7.3 CI/CD Pipeline Structure
```yaml
name: Deploy to PyPI
on:
  push:
    branches: [main]
  push:
    tags: ['v*']

jobs:
  test:
    # Run comprehensive test suite
  build:
    # Build distribution packages
  deploy-test:
    # Deploy to PyPI Test (main branch)
  deploy-prod:
    # Deploy to PyPI.org (tags only)
```

## 8. Testing Strategy

### 8.1 Unit Testing
- Version generation from different Git states
- Package metadata validation
- Build configuration correctness

### 8.2 Integration Testing
- End-to-end deployment to PyPI Test
- Version consistency across files
- Installation testing from both repositories

### 8.3 Performance Testing
- Deployment time measurement
- Build artifact validation
- Network reliability testing

### 8.4 Security Testing
- Trusted publishing validation
- Permission scope verification
- Audit trail completeness

## 9. Implementation Plan

### 9.1 Phase 1: Build System Migration
- Update pyproject.toml with setuptools-scm
- Create version file structure
- Update imports for dynamic versioning
- Validate local builds

### 9.2 Phase 2: Version Generation
- Configure setuptools-scm
- Test version generation locally
- Validate version patterns
- Update package metadata

### 9.3 Phase 3: CI/CD Pipeline
- Update GitHub Actions workflow
- Configure trusted publishing
- Setup environment protection
- Test deployment pipeline

### 9.4 Phase 4: Validation & Testing
- Comprehensive testing across scenarios
- Performance validation
- Security audit
- Documentation updates

## 10. Risk Analysis

### 10.1 Technical Risks
- **Risk**: setuptools-scm incompatibility
- **Mitigation**: Thorough testing on feature branch
- **Impact**: Medium
- **Probability**: Low

### 10.2 Security Risks
- **Risk**: Trusted publishing misconfiguration
- **Mitigation**: Staged rollout with validation
- **Impact**: High
- **Probability**: Low

### 10.3 Operational Risks
- **Risk**: Deployment failures during transition
- **Mitigation**: Parallel setup with rollback plan
- **Impact**: Medium
- **Probability**: Medium

## 11. Success Criteria

### 11.1 Primary Success Metrics
- [ ] All commits to main auto-deploy to PyPI Test
- [ ] All Git tags auto-deploy to PyPI.org
- [ ] Version numbers generated automatically
- [ ] Trusted publishing replaces API tokens
- [ ] Deployment time < 5 minutes

### 11.2 Quality Metrics
- [ ] Zero breaking changes to existing functionality
- [ ] 100% test coverage for new components
- [ ] Documentation updated and comprehensive
- [ ] Security audit passed

## 12. Dependencies

### 12.1 External Dependencies
- PyPI trusted publishing account setup
- GitHub repository environment configuration
- setuptools-scm package availability

### 12.2 Internal Dependencies
- Current Hatchling build system (to be migrated)
- Existing GitHub Actions workflow
- Package structure and imports

## 13. Acceptance Criteria

### 13.1 Deployment Criteria
- [ ] Every main branch commit creates PyPI Test package
- [ ] Git tags create PyPI.org production packages
- [ ] Version numbers match Git history
- [ ] No manual version management required
- [ ] Trusted publishing authentication works

### 13.2 Quality Criteria
- [ ] All existing tests pass
- [ ] New functionality is tested
- [ ] Documentation is complete
- [ ] Security audit completed
- [ ] Performance requirements met

## 14. Appendices

### 14.1 Reference Architecture
Based on PyPI Trusted Publishing best practices and setuptools-scm documentation.

### 14.2 Version Examples
- Development: `0.6.0.dev23+g1a2b3c4`
- Release Candidate: `0.6.0rc1`
- Production: `0.6.0`
- Post-release: `0.6.0.post1`

### 14.3 Installation Examples
```bash
# Development version
pip install -i https://test.pypi.org/simple/ pyforge-cli

# Production version
pip install pyforge-cli

# Specific version
pip install pyforge-cli==0.6.0
```

---

**Document Status**: Draft  
**Version**: 1.0  
**Created**: 2025-06-29  
**Author**: System Implementation  
**Reviewers**: Project Maintainers  
**Approval**: Pending