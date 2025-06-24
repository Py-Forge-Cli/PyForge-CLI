# PRD: Test Datasets Collection Feature

## Product Requirements Document

**Feature Name**: Test Datasets Collection  
**Issue**: #15  
**Version**: 1.0  
**Date**: 2025-01-23  
**Status**: Draft

## Executive Summary

Create a comprehensive test dataset collection system for PyForge CLI that provides users with easy access to sample files across all supported formats. This feature will enable developers and users to quickly test converters with real-world data of various sizes and complexities.

## Problem Statement

### Current Challenges
1. Users need to find or create test files to try PyForge CLI features
2. No standardized test data for validating converter functionality
3. Difficult to test edge cases without appropriate sample files
4. Manual downloading and organizing of test files is time-consuming
5. No consistent structure for test data across different formats

### User Pain Points
- "I want to test the XML converter but don't have any XML files"
- "I need large files to test performance but can't find suitable samples"
- "I want to test edge cases but don't know what files would trigger them"
- "Setting up test data manually for each format is tedious"

## Goals and Objectives

### Primary Goals
1. Provide instant access to curated test datasets for all supported formats
2. Enable easy installation via CLI command: `pyforge install sample-datasets`
3. Organize datasets by format and size categories
4. Include edge case files for thorough testing

### Success Metrics
- 100% format coverage (all supported formats have test files)
- Download completion rate > 95%
- User satisfaction with dataset variety and quality
- Reduced time to first successful conversion test

## User Stories

### As a Developer
- I want to quickly access test files for any format so I can test my code changes
- I want datasets of different sizes to test performance optimizations
- I want edge case files to ensure robust error handling

### As a New User
- I want sample files to try PyForge CLI without finding my own data
- I want examples that demonstrate all features of each converter
- I want a simple command to get all test data at once

### As a QA Tester
- I want comprehensive test datasets to validate all converter features
- I want reproducible test cases with known expected outputs
- I want files that test boundary conditions and error scenarios

## Functional Requirements

### 1. Dataset Collection
- **Formats Coverage**:
  - PDF: Various layouts, encrypted, corrupted, multi-page
  - Excel (.xlsx): Single/multi-sheet, formulas, large datasets
  - XML: Simple/complex hierarchies, namespaces, large files
  - MDB/ACCDB: Sample databases with multiple tables
  - DBF: Different versions, encodings, field types
  - CSV: Various delimiters, encodings, large files
  - MDF: SQL Server database files (when available)

- **Size Categories**:
  - Small: < 100MB (quick tests, typical use cases)
  - Medium: 100MB-1GB (moderate performance testing)
  - Large: > 1GB (heavy performance testing)

- **File Characteristics**:
  - Normal: Standard files that should convert successfully
  - Edge Cases: Files with special characteristics
  - Error Cases: Files that should trigger specific errors

### 2. Installation Command
```bash
# Install to current directory
pyforge install sample-datasets

# Install to specified directory
pyforge install sample-datasets /path/to/destination
```

### 3. Dataset Organization
The following structure will be created in the current directory (or specified path):
```
sample-datasets/
├── pdf/
│   ├── small/
│   │   ├── simple.pdf
│   │   ├── multi-page.pdf
│   │   └── README.md
│   ├── medium/
│   │   ├── report-50pages.pdf
│   │   └── encrypted.pdf
│   └── large/
│       └── manual-500pages.pdf
├── excel/
│   ├── small/
│   │   ├── simple.xlsx
│   │   └── multi-sheet.xlsx
│   └── medium/
│       └── sales-data.xlsx
├── xml/
│   ├── small/
│   │   ├── simple.xml
│   │   └── namespaces.xml
│   └── large/
│       └── catalog.xml
└── metadata.json
```

### 4. Dataset Sources
- **Public Domain Sources**:
  - Government open data portals
  - Academic datasets
  - Open source projects
  - Generated synthetic data

- **Hosting Infrastructure**:
  - **GitHub Releases** (Primary hosting method)
    - Maximum 2GB per file (sufficient for our use case)
    - Free hosting with no bandwidth limits
    - Reliable CDN with global distribution
    - Version-controlled releases
    - Direct download URLs with HTTPS
    - Integrated with project repository

- **Download Methods**:
  - Direct HTTPS downloads from GitHub Releases
  - Progress tracking for large files
  - Checksum verification
  - Resume capability for interrupted downloads


## Technical Requirements

### 1. Implementation Details
- Use existing Rich console for progress display
- Implement parallel downloads for efficiency
- Cache downloaded files with checksum verification
- Provide offline mode using cached datasets

### 2. Storage Requirements
- Target location: Current directory or user-specified path
- Creates `sample-datasets/` folder in target location
- Estimated total size: 5-10GB for complete collection
- Compress where appropriate to save bandwidth

### 3. Download Infrastructure
- **Primary Hosting**: GitHub Releases for PyForge CLI repository
- **File Organization**: Compressed archives per format (e.g., `pdf-samples.zip`, `excel-samples.zip`)
- **Version Management**: Tagged releases for dataset versions
- **Download URLs**: Direct HTTPS links to release assets
- Implement retry logic for failed downloads
- Show download progress with ETA
- Support resumable downloads

### 4. Integration Points
- Integrate with existing CLI command structure
- Use consistent error handling and logging
- Follow PyForge CLI coding standards
- Update documentation with examples using datasets

## Non-Functional Requirements

### 1. Performance
- Download speeds limited only by user's connection
- Parallel downloads when possible
- Efficient storage with no duplicates
- Quick access to dataset metadata

### 2. Reliability
- Checksum verification for all downloads
- Graceful handling of network failures
- Clear error messages for troubleshooting
- Automatic cleanup of partial downloads

### 3. Usability
- Single command installation
- Clear progress indication
- Informative success/error messages
- Easy discovery of available datasets

### 4. Maintainability
- Centralized dataset registry (metadata.json)
- Version tracking for dataset updates
- Easy addition of new datasets
- Community contribution guidelines

## User Interface

### Installation Flow
```
$ pyforge install sample-datasets

PyForge Test Datasets Installer
==============================

Analyzing available datasets...
✓ Found 7 formats with 45 sample files (2.3 GB total)

Downloading datasets to ./sample-datasets/...
[████████████████████] 100% PDF samples (15 files)
[████████████████████] 100% Excel samples (8 files)
[████████████▌       ] 67%  XML samples (downloading catalog.xml)

✅ Successfully installed 45 test files to ./sample-datasets/

Quick start:
  pyforge convert sample-datasets/pdf/small/simple.pdf
  pyforge convert sample-datasets/excel/small/simple.xlsx
```

### Custom Directory Installation
```
$ pyforge install sample-datasets /home/user/test-data

PyForge Test Datasets Installer
==============================

Installing to: /home/user/test-data/sample-datasets/

Downloading datasets...
[████████████████████] 100% Complete

✅ Successfully installed 45 test files to /home/user/test-data/sample-datasets/

Quick start:
  pyforge convert /home/user/test-data/sample-datasets/pdf/small/simple.pdf
```

## Implementation Phases

### Phase 1: Research and Dataset Collection (Week 1-2)
- Research and identify available datasets for each file type
- Document sources organized by Small (<100MB), Medium (100MB-1GB), Large (>1GB)
- Create comprehensive markdown documentation with dataset locations
- Verify licensing and copyright compliance for all sources
- Categorize datasets by characteristics (normal, edge cases, error cases)

### Phase 2: Data Collection Pipeline (Week 3)
- Create automated pipeline to gather datasets from documented sources
- Implement web scraping and download automation for identified sources
- Organize and validate collected datasets
- Package datasets by format into compressed archives
- Create GitHub release with all dataset archives
- Generate metadata and checksums for all files

### Phase 3: CLI Implementation (Week 4)
- Implement core framework with GitHub Releases integration
- Add `pyforge install sample-datasets` command
- Implement parallel processing for multiple archive downloads
- Add progress tracking and error handling
- Create comprehensive unit testing suite
- Documentation and final release preparation

## Success Criteria

1. **Completeness**: All supported formats have at least 3 test files
2. **Accessibility**: Single command installation to current/specified directory
3. **Hosting**: All datasets hosted on GitHub Releases with reliable download URLs
4. **Reliability**: 99% successful download rate from GitHub Releases
5. **Performance**: Complete dataset downloads in < 5 minutes on broadband
6. **Documentation**: Every dataset has description and expected behavior
7. **File Size Compliance**: All individual files under 2GB GitHub limit
8. **Version Control**: Dataset releases tagged and versioned on GitHub

## Risks and Mitigation

### Technical Risks
- **GitHub file size limits**: Ensure all files stay under 2GB limit (current plan fits well within this)
- **Download failures**: Implement robust retry and resume for GitHub Releases URLs
- **Storage space**: Check available space before download
- **Release asset management**: Maintain organized release structure

### Legal Risks
- **Copyright issues**: Use only public domain or generated data
- **Privacy concerns**: Ensure no PII in datasets
- **License compliance**: Document all data sources

## Future Enhancements

1. **Dataset Generation**: Tool to create synthetic test data
2. **Custom Datasets**: User-contributed dataset packages
3. **Cloud Integration**: Direct S3/Azure blob access
4. **Performance Benchmarks**: Standard performance tests

## Appendix

### A. Sample Dataset Sources
- PDF: arxiv.org, government reports
- Excel: data.gov, kaggle public datasets  
- XML: w3.org samples, open APIs
- MDB: Microsoft samples, generated data
- CSV: UCI ML repository, open data portals

### B. File Naming Convention
```
{description}-{characteristics}-{size}.{ext}
Examples:
- invoice-simple-small.pdf
- sales-multsheet-medium.xlsx
- catalog-namespaces-large.xml
```

### C. Metadata Structure
```json
{
  "version": "1.0.0",
  "generated": "2024-01-23T10:00:00Z",
  "formats": {
    "pdf": {
      "total_files": 9,
      "total_size": "297.1 MB",
      "categories": {
        "small": {
          "files": ["simple.pdf", "multi-page.pdf"],
          "descriptions": {
            "simple.pdf": "Single page PDF with text only",
            "multi-page.pdf": "10-page PDF with images"
          }
        }
      }
    }
  }
}
```