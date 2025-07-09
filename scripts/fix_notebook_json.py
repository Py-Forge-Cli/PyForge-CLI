#!/usr/bin/env python3
"""
Fix JSON parsing issues in Jupyter notebooks.
"""
import json
import sys
from pathlib import Path


def fix_notebook_json(notebook_path):
    """Fix common JSON issues in Jupyter notebooks."""
    print(f"Fixing {notebook_path}...")
    
    try:
        # Read the notebook content
        with open(notebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Common fixes for malformed JSON
        # 1. Fix escaped newlines in JSON strings
        content = content.replace('",\\n",', '",')
        content = content.replace('\\n",', '",')
        content = content.replace('",\\n', '",\n')
        
        # 2. Try to parse and validate
        try:
            notebook_data = json.loads(content)
            
            # Clean up metadata if needed
            if 'metadata' in notebook_data:
                metadata = notebook_data['metadata']
                
                # Fix kernelspec if malformed
                if 'kernelspec' in metadata:
                    kernelspec = metadata['kernelspec']
                    if isinstance(kernelspec, dict):
                        # Ensure proper structure
                        kernelspec['display_name'] = kernelspec.get('display_name', 'Python 3').replace('\\n', '')
                        kernelspec['language'] = kernelspec.get('language', 'python').replace('\\n', '')
                        kernelspec['name'] = kernelspec.get('name', 'python3').replace('\\n', '')
                
                # Fix language_info if malformed
                if 'language_info' in metadata:
                    lang_info = metadata['language_info']
                    if isinstance(lang_info, dict):
                        for key in lang_info:
                            if isinstance(lang_info[key], str):
                                lang_info[key] = lang_info[key].replace('\\n', '')
            
            # Write back the fixed JSON
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook_data, f, indent=1, ensure_ascii=False)
            
            print(f"✓ Fixed {notebook_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            
            # Try more aggressive fixes
            # Look for specific pattern issues around the error location
            lines = content.split('\n')
            
            # Fix specific pattern found in error
            fixed_lines = []
            for i, line in enumerate(lines):
                # Remove invalid escape sequences in JSON string values
                if '"display_name": "Python 3",\\n",' in line:
                    line = '   "display_name": "Python 3",'
                elif '"language": "python",\\n",' in line:
                    line = '   "language": "python",'
                elif '"name": "python3",\\n"' in line:
                    line = '   "name": "python3"'
                
                fixed_lines.append(line)
            
            # Rejoin and try again
            content = '\n'.join(fixed_lines)
            
            try:
                notebook_data = json.loads(content)
                with open(notebook_path, 'w', encoding='utf-8') as f:
                    json.dump(notebook_data, f, indent=1, ensure_ascii=False)
                print(f"✓ Fixed {notebook_path} (after aggressive fixes)")
                return True
            except Exception as e2:
                print(f"Failed to fix {notebook_path}: {e2}")
                return False
                
    except Exception as e:
        print(f"Error processing {notebook_path}: {e}")
        return False


def main():
    """Main entry point."""
    # Fix the known problematic notebooks
    notebooks_to_fix = [
        "notebooks/testing/functional/04-databricks-extension-functional.ipynb",
        "notebooks/testing/functional/05-databricks-extension-serverless.ipynb"
    ]
    
    success_count = 0
    for notebook_path in notebooks_to_fix:
        if Path(notebook_path).exists():
            if fix_notebook_json(notebook_path):
                success_count += 1
        else:
            print(f"File not found: {notebook_path}")
    
    print(f"\nFixed {success_count}/{len(notebooks_to_fix)} notebooks")
    return 0 if success_count == len(notebooks_to_fix) else 1


if __name__ == "__main__":
    sys.exit(main())