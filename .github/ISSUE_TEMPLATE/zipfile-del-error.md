---
name: ZipFile.__del__ Error Investigation
about: Track and resolve the persistent ZipFile deletion error in MDB conversion
title: 'bug: ZipFile.__del__ error persists during MDB conversion on Unity Catalog volumes'
labels: 'bug, investigation, mdb-converter, databricks-serverless'
assignees: ''
---

## Bug Description
A `ZipFile.__del__` error consistently occurs during MDB conversion in Databricks Serverless environments, even after disabling all Excel report generation.

## Error Details
```
--- Standard Error (includes warnings/logs) ---
EnhancedMDBConverter - WARNING - Failed to generate conversion report: [Errno 95] Operation not supported
Exception ignored in: <function ZipFile.__del__ at 0x7f0e6cc06cb0>
Traceback (most recent call last):
  File "/usr/lib/python3.10/zipfile.py", line 1834, in __del__
    self.close()
  File "/usr/lib/python3.10/zipfile.py", line 1851, in close
    self.fp.seek(self.start_dir)
OSError: [Errno 95] Operation not supported
```

## Environment
- **Platform**: Databricks Serverless V1
- **Python Version**: 3.10
- **PyForge CLI Version**: 1.0.9.dev8
- **File System**: Unity Catalog volumes (`/Volumes/...`)

## Current Status
✅ **Functionality Works**: MDB conversion completes successfully and creates Parquet files  
✅ **All 6 stages display**: Progress tracking works correctly  
❌ **Error persists**: ZipFile deletion error occurs but doesn't impact conversion  

## Investigation Completed
- [x] Disabled Excel report generation in `EnhancedMDBConverter`
- [x] Disabled Excel report generation in base `MDBConverter`
- [x] Verified no `pd.ExcelWriter` calls in conversion path
- [x] Confirmed `_generate_excel_report()` raises `NotImplementedError`
- [x] Searched codebase for all Excel-related operations

## Root Cause Theories
1. **Pandas Auto-Import**: Pandas may automatically import Excel modules (`openpyxl`) during initialization
2. **Hidden Dependency**: Some dependency might create temporary Excel/ZIP files
3. **Environment Issue**: Databricks Serverless may have filesystem restrictions affecting cleanup
4. **Memory Management**: ZipFile objects created elsewhere aren't being cleaned up properly

## Reproduction Steps
1. Deploy PyForge CLI to Databricks Serverless
2. Run MDB conversion to Unity Catalog volume:
   ```python
   pyforge convert /path/to/file.mdb /Volumes/catalog/schema/output/
   ```
3. Observe error in stderr (conversion still succeeds)

## Expected Behavior
No ZipFile deletion errors should occur during MDB conversion.

## Proposed Investigation
1. **Add debugging**: Inject logging to track ZipFile creation
2. **Dependency analysis**: Check if any imported modules create ZipFiles
3. **Environment testing**: Test in different Databricks environments
4. **Memory profiling**: Track object creation and cleanup

## Workaround
The error doesn't affect functionality - MDB conversion works correctly and produces expected Parquet files.

## Priority
**Low** - Error doesn't impact functionality, but should be resolved for clean logs.

## Related
- PR #37: Unity Catalog volume path fixes
- Fix applied in commit 079dd09