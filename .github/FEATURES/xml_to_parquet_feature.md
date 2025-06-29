---
name: ✨ Feature Request (PRD-Based)
about: Suggest a new feature using structured PRD → Tasks workflow
title: '[FEATURE] XML to Parquet Converter with Automated Structure Detection'
labels: 'enhancement, claude-ready, feature-request, prd-workflow'
assignees: ''
---

## 🚀 Feature Request Overview
<!-- Quick summary of what you want to build -->

**Feature Name**: XML to Parquet Converter with Automated Flattening
**Type**: [X] New Command [ ] Enhancement [ ] Integration [ ] Performance [ ] Other: ___

## 📋 Implementation Workflow
This feature request follows the **PRD → Tasks → Implementation** workflow:

1. **📝 PRD Creation**: Complete this issue to create a comprehensive PRD document
2. **🎯 Task Generation**: Generate structured task list from approved PRD  
3. **⚡ Implementation**: Execute tasks one-by-one with approval checkpoints

---

## 📋 PRD REQUIREMENTS GATHERING

### 🎯 Problem Statement
<!-- What problem does this solve? Who experiences this problem? -->

Many data engineers and analysts work with XML files containing hierarchical data that needs to be converted to columnar formats for analytics. Currently, pyforge supports various file formats but lacks XML processing capability. Users must manually write complex scripts to:
- Parse nested XML structures
- Flatten hierarchical data into tabular format
- Handle varying XML schemas
- Convert to Parquet for analytics workloads

This is time-consuming, error-prone, and requires deep XML/programming expertise.

### 💡 Proposed Solution Overview
<!-- High-level description of your proposed solution -->

Add a new `XmlConverter` to pyforge that:
1. Automatically detects and analyzes XML structure
2. Intelligently flattens nested hierarchies into tabular format
3. Handles arrays and nested objects with configurable strategies
4. Converts flattened data to Parquet format
5. Provides options for handling complex XML scenarios (namespaces, attributes, mixed content)

### 👥 Target Users
<!-- Who will use this feature? What are their skill levels? -->

- **Data Engineers**: Converting XML data sources for data pipelines
- **Data Analysts**: Needing to analyze XML data in BI tools
- **ETL Developers**: Building automated XML processing workflows
- **Business Users**: Converting XML reports/exports without coding

Skill levels range from command-line beginners to advanced users needing fine control.

### 🔄 User Journey
<!-- Step-by-step workflow of how users will interact with this feature -->
1. User starts with: XML file(s) containing structured/semi-structured data
2. User runs: `pyforge convert data.xml output.parquet`
3. Tool processes: 
   - Analyzes XML structure
   - Shows preview of detected schema
   - Flattens nested elements
   - Converts to Parquet
4. User receives: Parquet file with flattened data ready for analytics
5. User can then: Query with SQL, load into data warehouses, analyze in BI tools

### 📊 Requirements Breakdown
#### Functional Requirements
- [X] Parse XML files of any size (streaming for large files)
- [X] Auto-detect XML structure and namespaces
- [X] Flatten nested elements with configurable strategies
- [X] Handle XML attributes as columns
- [X] Support array/list elements with multiple flattening options
- [X] Convert to Parquet with appropriate data types (Phase 1: all strings)
- [X] Provide schema preview before conversion
- [X] Support batch conversion of multiple XML files
- [X] Handle malformed XML gracefully with error reporting

#### Non-Functional Requirements  
- [X] **Performance**: Stream processing for files > 100MB, < 5 sec for 10MB files
- [X] **Compatibility**: Python 3.8+, cross-platform (Windows/Mac/Linux)
- [X] **Usability**: Simple defaults with advanced options, clear error messages
- [X] **Reliability**: Graceful error handling, resume capability for large files

### 🖥️ Command Line Interface Design
```bash
# Primary command structure
pyforge convert input.xml output.parquet

# With options
pyforge convert data.xml output.parquet --flatten-strategy aggressive
pyforge convert data.xml output.parquet --array-handling expand
pyforge convert data.xml output.parquet --namespace-handling strip
pyforge convert data.xml output.parquet --preview-schema

# Batch processing
pyforge convert --batch "data/*.xml" --output-dir processed/
pyforge convert large.xml output.parquet --streaming --chunk-size 10000

# Schema preview
pyforge info data.xml --schema
pyforge validate data.xml --format xml
```

### 📁 Input/Output Specifications
- **Input Types**: 
  - XML files (.xml)
  - Compressed XML (.xml.gz, .xml.bz2)
  - XML with various encodings (UTF-8, UTF-16, ISO-8859-1)
  
- **Output Types**: 
  - Parquet files with configurable compression
  - Schema report (JSON/text)
  - Conversion statistics
  
- **Processing Options**:
  - Flattening strategies: conservative, moderate, aggressive
  - Array handling: expand, concatenate, json_string
  - Namespace handling: preserve, strip, prefix
  - Attribute handling: include, exclude, prefix
  
- **Configuration**:
  - Max nesting depth
  - Column naming conventions
  - Null value handling
  - Data type inference (Phase 2)

### 🔍 Technical Architecture
- **Core Components**:
  - `XmlConverter` class extending `BaseConverter`
  - `XmlStructureAnalyzer` for schema detection
  - `XmlFlattener` for hierarchy flattening
  - `StreamingXmlParser` for large file handling
  
- **Dependencies**:
  - `lxml` or `xml.etree` for XML parsing
  - `pandas` for data manipulation (existing)
  - `pyarrow` for Parquet writing (existing)
  
- **Integration Points**:
  - Registers with `ConverterRegistry`
  - Uses existing `StringDatabaseConverter` pattern
  - Integrates with CLI command structure
  - Leverages existing progress tracking
  
- **Data Flow**:
  1. XML parsing → Structure analysis
  2. Schema detection → User preview (optional)
  3. Streaming parse → Flattening transformation
  4. DataFrame creation → Parquet writing

### 🧪 Testing Strategy

- **Test Data Generation**:
  - **Basic XML Structures**:
    - `simple.xml`: Flat structure with 5-10 elements
    - `attributes.xml`: Elements with various attributes
    - `namespaces.xml`: Multiple namespace declarations
    - `mixed_content.xml`: Text and element children mixed
    
  - **Nested Structures**:
    - `nested_shallow.xml`: 2-3 levels deep
    - `nested_moderate.xml`: 5-7 levels deep
    - `nested_deep.xml`: 10-15 levels deep
    - `nested_extreme.xml`: 20+ levels for stress testing
    
  - **Array Structures**:
    - `array_simple.xml`: Single repeated element
    - `array_nested.xml`: Arrays within arrays
    - `array_mixed.xml`: Arrays with different data types
    - `array_empty.xml`: Arrays with no elements
    - `array_single.xml`: Arrays with one element
    
  - **Large Files**:
    - `data_1mb.xml`: ~1MB with 1000 records
    - `data_10mb.xml`: ~10MB with 10,000 records
    - `data_100mb.xml`: ~100MB with 100,000 records
    - `data_1gb.xml`: ~1GB with 1,000,000 records
    
  - **Special Cases**:
    - `cdata_sections.xml`: CDATA wrapped content
    - `processing_instructions.xml`: XML with PIs
    - `dtd_entities.xml`: XML with DTD and entities
    - `unicode_content.xml`: Various Unicode characters
    - `special_chars.xml`: XML special characters in content
    
  - **Namespace Variations**:
    - `ns_default.xml`: Default namespace only
    - `ns_multiple.xml`: Multiple namespace prefixes
    - `ns_attributes.xml`: Namespaced attributes
    - `ns_mixed.xml`: Mix of default and prefixed
    
  - **Malformed XML**:
    - `malformed_unclosed.xml`: Missing closing tags
    - `malformed_invalid_chars.xml`: Invalid characters
    - `malformed_encoding.xml`: Wrong encoding declaration
    - `malformed_structure.xml`: Invalid nesting
    
  - **Compression Test Files**:
    - `compressed.xml.gz`: Gzip compressed XML
    - `compressed.xml.bz2`: Bzip2 compressed XML
    - `compressed_large.xml.gz`: Large compressed file
    
  - **Batch Processing Files**:
    - `batch/file1.xml`: Different structure
    - `batch/file2.xml`: Different structure
    - `batch/file3.xml`: Different structure
    - `batch/consistent/*.xml`: Same structure files
    
  - **Test Data Generator Script**:
    ```python
    # test_data_generator.py
    - Generate all test XML files programmatically
    - Ensure consistent, reproducible test data
    - Create files with specific characteristics
    - Generate large files efficiently
    - Create malformed files for error testing
    ```
    
  - **Example Test Data Structures**:
    ```xml
    <!-- simple.xml -->
    <root>
      <id>1</id>
      <name>Test User</name>
      <email>test@example.com</email>
      <age>25</age>
      <active>true</active>
    </root>
    
    <!-- array_simple.xml -->
    <root>
      <items>
        <item>Value1</item>
        <item>Value2</item>
        <item>Value3</item>
      </items>
    </root>
    
    <!-- nested_moderate.xml -->
    <company>
      <info>
        <name>TechCorp</name>
        <employees>
          <employee>
            <personal>
              <name>John Doe</name>
              <contact>
                <email>john@tech.com</email>
                <phone>555-0123</phone>
              </contact>
            </personal>
          </employee>
        </employees>
      </info>
    </company>
    
    <!-- attributes.xml -->
    <products>
      <product id="1" category="electronics" inStock="true">
        <name lang="en">Laptop</name>
        <price currency="USD">999.99</price>
      </product>
    </products>
    
    <!-- namespaces.xml -->
    <ns1:root xmlns:ns1="http://example.com/ns1" 
              xmlns:ns2="http://example.com/ns2">
      <ns1:data>Value1</ns1:data>
      <ns2:info type="test">Value2</ns2:info>
    </ns1:root>
    ```

- **Unit Tests**:
  - **Basic Conversion**:
    - Simple XML to Parquet conversion
    - XML with attributes to Parquet
    - XML with namespaces to Parquet
  
  - **Flattening Strategies**:
    - `--flatten-strategy conservative`: Minimal flattening, preserve structure
    - `--flatten-strategy moderate`: Balance between structure and usability
    - `--flatten-strategy aggressive`: Maximum flattening for analytics
  
  - **Array Handling Options**:
    - `--array-handling expand`: Create multiple rows for array elements
    - `--array-handling concatenate`: Join array values with delimiter
    - `--array-handling json_string`: Store arrays as JSON strings
  
  - **Namespace Handling**:
    - `--namespace-handling preserve`: Keep namespace prefixes
    - `--namespace-handling strip`: Remove all namespace information
    - `--namespace-handling prefix`: Convert namespaces to column prefixes
  
  - **Schema Preview**:
    - `--preview-schema`: Display detected schema before conversion
    - Schema detection for deeply nested XML
    - Schema inference for mixed content
  
  - **Batch Processing**:
    - `--batch "*.xml"`: Process multiple files
    - `--output-dir`: Specify output directory for batch
    - Batch with mixed XML structures
  
  - **Streaming Options**:
    - `--streaming`: Enable streaming for large files
    - `--chunk-size`: Custom chunk sizes (1000, 10000, 100000)
    - Memory usage with different chunk sizes
  
  - **Compression Formats**:
    - Input: `.xml`, `.xml.gz`, `.xml.bz2`
    - Output: Various Parquet compression options
  
  - **Command Variations**:
    - `pyforge info data.xml --schema`: Schema inspection
    - `pyforge validate data.xml --format xml`: XML validation
    - `pyforge formats`: Verify XML appears in supported formats
  
- **Integration Tests**:
  - **End-to-end Scenarios**:
    - Simple XML → Parquet with verification
    - Complex nested XML → Flattened Parquet
    - Multiple XML files → Batch Parquet output
  
  - **CLI Integration**:
    - Help text displays XML options correctly
    - Error messages for invalid options
    - Progress bars for large file processing
  
  - **Option Combinations**:
    - Aggressive flattening + array expansion
    - Namespace stripping + attribute inclusion
    - Streaming + batch processing
    - Schema preview + custom output paths
  
- **Performance Tests**:
  - **File Size Benchmarks**:
    - 1MB XML: < 1 second
    - 10MB XML: < 5 seconds
    - 100MB XML: < 30 seconds (streaming)
    - 1GB XML: < 5 minutes (streaming)
  
  - **Memory Profiling**:
    - Peak memory for different file sizes
    - Memory usage with/without streaming
    - Impact of chunk size on memory
  
  - **Optimization Tests**:
    - Streaming vs. full file loading
    - Different parser backends (lxml vs. etree)
    - Parallel batch processing performance
  
- **Edge Cases**:
  - **Malformed XML**:
    - Missing closing tags
    - Invalid characters
    - Encoding errors
  
  - **Complex Structures**:
    - Deeply nested (>10 levels)
    - Mixed content (text + elements)
    - Self-referencing elements
    - CDATA sections
    - Processing instructions
  
  - **Attribute Edge Cases**:
    - Attributes with same name as elements
    - Namespace-prefixed attributes
    - Empty attributes
  
  - **Array Edge Cases**:
    - Empty arrays
    - Single-element arrays
    - Nested arrays
    - Arrays with mixed types
  
  - **Error Handling**:
    - File not found
    - Permission denied
    - Disk space issues
    - Invalid option combinations
    - Corrupted XML files

---

## 🎯 PRD APPROVAL CHECKLIST
**Complete this section before generating tasks:**

- [X] Problem statement clearly defines user pain points
- [X] Solution approach is technically feasible
- [X] Requirements are specific and measurable
- [X] CLI interface follows project conventions
- [X] Testing strategy covers all scenarios
- [X] Performance requirements are realistic
- [X] Implementation approach is approved

---

## 📋 TASK GENERATION TRIGGER
**Once PRD is approved, use this section to generate implementation tasks:**

### Task List Creation
- [ ] **Ready to generate tasks**: PRD approved and complete
- [ ] **Task file created**: `/tasks/tasks-xml-to-parquet.md`
- [ ] **Implementation started**: First task marked in_progress

### Claude Implementation Commands
```bash
# Generate PRD document
"Create a PRD for XML to Parquet conversion based on the requirements above"

# Generate task list from PRD  
"Generate tasks from /tasks/prd-xml-to-parquet.md"

# Start implementation
"Start working on /tasks/tasks-xml-to-parquet.md"
```

---

## 🔍 CLAUDE GUIDANCE SECTION

### File Structure for Implementation
```
/tasks/
  ├── prd-xml-to-parquet.md      # Product Requirements Document
  ├── tasks-xml-to-parquet.md    # Implementation task list
  └── ...

@docs/                           # Documentation under docs folder
```

### Key Investigation Areas
```bash
# Examine existing patterns
grep -r "BaseConverter" src/pyforge_cli/converters/
grep -r "StringDatabaseConverter" src/pyforge_cli/converters/
grep -r "register_converter" src/pyforge_cli/

# Core files to modify
# - src/pyforge_cli/converters/xml.py (new file)
# - src/pyforge_cli/converters/__init__.py (register)
# - src/pyforge_cli/core/loader.py (add to builtin)
# - tests/test_xml_converter.py (new tests)
```

### Implementation Checkpoints
- [ ] **Phase 1**: Core XML parsing and flattening logic
- [ ] **Phase 2**: CLI interface integration  
- [ ] **Phase 3**: Advanced options and streaming
- [ ] **Phase 4**: Testing and error handling
- [ ] **Phase 5**: Performance optimization and docs

---

## 📊 SUCCESS CRITERIA
- [ ] PRD document created and approved
- [ ] Task list generated with clear acceptance criteria
- [ ] All tasks completed with user approval at each step
- [ ] XML files convert successfully to Parquet
- [ ] Nested structures flatten correctly
- [ ] Large files process without memory issues
- [ ] Test coverage > 90%
- [ ] Documentation updated (CLI help, docs site)
- [ ] Performance benchmarks meet requirements

---

## 🔗 RELATED WORK
- **Related Issues**: #
- **Depends On**: Existing converter infrastructure
- **Blocks**: #
- **Similar Features**: Excel converter (multi-sheet), CSV converter (auto-detection)

---

## 📅 PRIORITIZATION
- **Business Impact**: High - Enables XML data analytics workflows
- **Technical Complexity**: Medium - Well-defined problem with existing patterns
- **User Demand**: High - Common enterprise data format
- **Implementation Timeline**: 2-3 days

---
**For Maintainers - PRD Workflow:**
- [ ] Issue reviewed and PRD requirements complete
- [ ] Technical feasibility confirmed
- [ ] PRD document creation approved
- [ ] Task generation authorized
- [ ] Implementation approach validated