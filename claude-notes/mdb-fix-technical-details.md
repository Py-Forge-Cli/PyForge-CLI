# Technical Details: MDB Fix for Databricks Serverless

## Problem Statement
MDB/Access file conversion was failing in Databricks Serverless environment due to:
1. JPype native library limitations (can't load JNI libraries)
2. Missing JAR files in package distribution
3. TestPyPI v1.0.6 had a bug in `get_converter()` method

## Solution Architecture

### 1. Subprocess Backend Implementation
Created `ucanaccess_subprocess_backend.py` as an alternative to JPype:

#### Key Design Decisions:
- **Java Subprocess Execution**: Instead of using JPype to bridge Python-Java, we compile and run Java code directly
- **Dynamic Java Code Generation**: Creates Java source files on-the-fly for each operation
- **CSV Bridge**: Java exports data to CSV, Python reads it back via pandas
- **Temporary File Management**: Handles cleanup of Java source, class, and CSV files

#### Implementation Details:
```python
def _run_java_code(self, java_code: str) -> dict:
    """Compile and run Java code with UCanAccess classpath."""
    # 1. Extract class name from Java source
    class_match = re.search(r'public\s+class\s+(\w+)', java_code)
    class_name = class_match.group(1)
    
    # 2. Write Java file with correct name (fixes compilation error)
    java_file = os.path.join(temp_dir, f"{class_name}.java")
    
    # 3. Compile with full classpath
    compile_cmd = ['javac', '-cp', classpath, java_file]
    
    # 4. Run and capture output
    run_cmd = ['java', '-cp', f'.{os.pathsep}{classpath}', class_name, ...]
```

#### Unity Catalog Support:
```python
if db_path.startswith("/Volumes/"):
    # Copy to local storage for Java access
    local_path = os.path.join(temp_dir, f"pyforge_{os.getpid()}_{file_name}")
    subprocess.run(f"cp '{db_path}' '{local_path}'", shell=True)
```

### 2. Backend Selection Strategy
Modified `dual_backend_mdb_reader.py` to implement fallback chain:

```python
# Connection attempt order:
1. UCanAccess (JPype) - Primary, works in most environments
2. UCanAccess Subprocess - Fallback for Serverless/JPype issues  
3. PyODBC - Windows-only fallback
```

### 3. JAR Files Packaging Fix

#### MANIFEST.in Addition:
```
# Include JAR files for UCanAccess
recursive-include src/pyforge_cli/data/jars *.jar
```

#### pyproject.toml Configuration:
```toml
[tool.setuptools]
packages = {find = {where = ["src"]}}  # Fixed from manual list
package-dir = {"" = "src"}
include-package-data = true

[tool.setuptools.package-data]
pyforge_cli = [
    "data/jars/*.jar",
    "backends/jars/*.jar"
]
```

### 4. Environment Detection
Added Databricks Serverless detection in `ucanaccess_backend.py`:

```python
def _is_databricks_serverless(self) -> bool:
    """Detect Databricks Serverless environment."""
    return (
        os.environ.get('IS_SERVERLESS') == 'TRUE' or
        os.environ.get('SPARK_CONNECT_MODE_ENABLED') == '1'
    )
```

## Bug Fixes

### 1. Java Class Name Compilation Error
**Issue**: `class ListTables is public, should be declared in a file named ListTables.java`
**Fix**: Extract class name from Java source and use it as filename

### 2. Missing JAR Files
**Issue**: JAR files not included in wheel distribution
**Fix**: Proper setuptools configuration with package-data

### 3. get_converter() TypeError
**Issue**: `get_converter()` takes 2 positional arguments but 3 were given
**Fix**: This was fixed in dev versions but exists in TestPyPI v1.0.6

## Testing Strategy

### Test Notebook Structure:
1. Environment verification (Java, Python, Serverless detection)
2. JAR files availability check
3. MDB conversion tests (simple files without OLE objects)
4. Local file copy approach (fallback for Unity Catalog issues)
5. Direct Python API testing

### Test Files Selection:
- Avoided Northwind database (has OLE/image objects causing type conversion errors)
- Used simpler MDB files: `sample_dibi.mdb`, `access_sakila.mdb`

## Performance Considerations

### Subprocess Backend Trade-offs:
- **Pros**: Works in restricted environments, no native library dependencies
- **Cons**: Slower due to process creation, Java compilation overhead

### Optimization Strategies:
1. **Table List Caching**: Cache results to avoid repeated Java calls
2. **Batch Operations**: Could extend to support multiple table exports in one Java run
3. **Connection Pooling**: Not applicable due to stateless subprocess nature

## Future Improvements

1. **Compiled Java JAR**: Pre-compile common operations into a JAR
2. **Better Error Handling**: Parse Java exceptions more intelligently
3. **Streaming Support**: For large tables, stream CSV data instead of full export
4. **Password Support**: Currently not supported in subprocess mode
5. **Connection String Options**: Support more UCanAccess connection parameters

## Deployment Notes

- Current version: 1.0.9.dev6
- Wheel includes ~8MB of JAR files
- Compatible with Databricks Serverless V1 (Python 3.10.12)
- No additional dependencies required beyond standard PyForge CLI deps