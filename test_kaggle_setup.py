#!/usr/bin/env python3
"""
Test script to validate Kaggle API credentials setup
"""

import os
import json
from pathlib import Path

def check_kaggle_credentials():
    """Check if Kaggle credentials are properly configured"""
    print("🔍 Checking Kaggle API credentials...")
    print()
    
    # Check for kaggle.json file
    kaggle_dir = Path.home() / ".kaggle"
    credentials_file = kaggle_dir / "kaggle.json"
    
    if credentials_file.exists():
        print("✅ Found ~/.kaggle/kaggle.json")
        
        # Check file permissions
        file_stat = credentials_file.stat()
        file_mode = oct(file_stat.st_mode)[-3:]
        
        if file_mode == "600":
            print("✅ File permissions are correct (600)")
        else:
            print(f"⚠️  File permissions are {file_mode}, should be 600")
            print("   Run: chmod 600 ~/.kaggle/kaggle.json")
        
        # Check file contents
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
                
            if 'username' in creds and 'key' in creds:
                print(f"✅ Credentials file contains username: {creds['username']}")
                print("✅ Credentials file contains API key")
                return True, creds['username'], creds['key']
            else:
                print("❌ Credentials file missing username or key")
                return False, None, None
                
        except json.JSONDecodeError:
            print("❌ Credentials file is not valid JSON")
            return False, None, None
        except Exception as e:
            print(f"❌ Error reading credentials file: {e}")
            return False, None, None
    
    # Check environment variables
    elif 'KAGGLE_USERNAME' in os.environ and 'KAGGLE_KEY' in os.environ:
        username = os.environ['KAGGLE_USERNAME']
        key = os.environ['KAGGLE_KEY']
        print("✅ Found KAGGLE_USERNAME environment variable")
        print("✅ Found KAGGLE_KEY environment variable")
        print(f"✅ Username: {username}")
        return True, username, key
    
    else:
        print("❌ No Kaggle credentials found")
        print()
        print("📋 Setup options:")
        print("1. File-based (recommended):")
        print("   - Download kaggle.json from https://www.kaggle.com/account")
        print("   - Copy to ~/.kaggle/kaggle.json")
        print("   - Run: chmod 600 ~/.kaggle/kaggle.json")
        print()
        print("2. Environment variables:")
        print("   - export KAGGLE_USERNAME='your_username'")
        print("   - export KAGGLE_KEY='your_api_key'")
        return False, None, None

def test_kaggle_api():
    """Test actual Kaggle API functionality"""
    print("\n🧪 Testing Kaggle API access...")
    
    try:
        import kagglehub
        print("✅ kagglehub module imported successfully")
        
        # Test with a small, public dataset
        print("📥 Testing download with a small dataset...")
        path = kagglehub.dataset_download("yasserh/titanic-dataset")
        print(f"✅ Download successful! Path: {path}")
        
        # Check downloaded files
        if os.path.exists(path):
            files = list(os.listdir(path))
            print(f"✅ Downloaded {len(files)} files: {files}")
            return True
        else:
            print("⚠️  Download path doesn't exist")
            return False
            
    except ImportError:
        print("❌ kagglehub not installed. Run: pip install kagglehub")
        return False
    except Exception as e:
        print(f"❌ Kaggle API test failed: {e}")
        print()
        print("💡 Common issues:")
        print("- Check your internet connection")
        print("- Verify your Kaggle account has API access enabled")
        print("- Make sure you've accepted Kaggle's terms of service")
        print("- Try accessing https://www.kaggle.com in your browser first")
        return False

if __name__ == "__main__":
    print("🚀 Kaggle API Setup Validator")
    print("=" * 40)
    
    # Check credentials
    has_creds, username, key = check_kaggle_credentials()
    
    if has_creds:
        # Test API access
        api_works = test_kaggle_api()
        
        if api_works:
            print("\n🎉 Kaggle API is fully configured and working!")
            print("You can now run the Kaggle dataset download script.")
        else:
            print("\n❌ Kaggle API credentials found but API test failed")
    else:
        print("\n❌ Kaggle API setup incomplete")
        print("Please follow the setup instructions above.")