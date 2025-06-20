# Troubleshooting Guide

Solutions to common issues and optimization tips for PyForge CLI.

## Common Issues

### Installation Problems

**Issue**: `command not found: pyforge`
**Solution**: 
```bash
# Check if installed
pip show pyforge-cli

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### File Not Found Errors

**Issue**: `FileNotFoundError: No such file or directory`
**Solutions**:
- Check file path and spelling
- Use absolute paths
- Verify file permissions

### Permission Errors

**Issue**: Permission denied when writing output
**Solutions**:
```bash
# Check directory permissions
ls -la output_directory/

# Create output directory
mkdir -p output_directory

# Change permissions
chmod 755 output_directory/
```

## Performance Tips

### Large File Processing

For files over 100MB:
- Use verbose mode to monitor progress
- Ensure sufficient disk space (3x file size)
- Close other applications
- Consider processing in chunks

### Memory Optimization

```bash
# Monitor memory usage
top -p $(pgrep pyforge)

# Process with limited memory
ulimit -v 2048000  # Limit to 2GB
pyforge convert large_file.xlsx
```

## Getting Help

- Check [CLI Reference](../reference/cli-reference.md)
- Visit [GitHub Issues](https://github.com/Py-Forge-Cli/PyForge-CLI/issues)
- Ask in [Discussions](https://github.com/Py-Forge-Cli/PyForge-CLI/discussions)