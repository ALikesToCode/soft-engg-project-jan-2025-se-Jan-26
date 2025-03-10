#!/usr/bin/env python3
"""
Fix dependencies for Python 3.13 compatibility.

This script downgrades bcrypt to 4.0.1 and upgrades pydantic to 2.7.4 or newer
to fix compatibility issues with Python 3.13.
"""
import subprocess
import sys
import importlib.metadata
import os

def check_version(package):
    """Check the installed version of a package."""
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None

def main():
    """Main function to fix dependencies."""
    print("Checking Python version...")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major == 3 and python_version.minor >= 13:
        print("Python 3.13+ detected. Checking dependencies...")
        
        # Check bcrypt version
        bcrypt_version = check_version("bcrypt")
        if bcrypt_version:
            print(f"bcrypt version: {bcrypt_version}")
            if bcrypt_version.startswith("4.1") or bcrypt_version.startswith("4.2"):
                print("bcrypt 4.1+ or 4.2+ detected. This version is incompatible with passlib.")
                print("Downgrading bcrypt to 4.0.1...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt==4.0.1", "--force-reinstall"])
                print("bcrypt downgraded to 4.0.1")
            else:
                print("bcrypt version is compatible. No action needed.")
        else:
            print("bcrypt not installed. Installing bcrypt 4.0.1...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt==4.0.1"])
            print("bcrypt 4.0.1 installed")
        
        # Check pydantic version
        pydantic_version = check_version("pydantic")
        if pydantic_version:
            print(f"pydantic version: {pydantic_version}")
            major, minor, patch = map(int, pydantic_version.split(".")[:3])
            if major < 2 or (major == 2 and minor < 7) or (major == 2 and minor == 7 and patch < 4):
                print("pydantic version is older than 2.7.4. This version is incompatible with Python 3.13.")
                print("Upgrading pydantic to 2.7.4...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic>=2.7.4", "--force-reinstall"])
                print("pydantic upgraded to 2.7.4 or newer")
            else:
                print("pydantic version is compatible. No action needed.")
        else:
            print("pydantic not installed. Installing pydantic 2.7.4...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic>=2.7.4"])
            print("pydantic 2.7.4 or newer installed")
        
        # Check pydantic-settings version
        pydantic_settings_version = check_version("pydantic-settings")
        if pydantic_settings_version:
            print(f"pydantic-settings version: {pydantic_settings_version}")
            # Make sure pydantic-settings is compatible with the installed pydantic version
            print("Ensuring pydantic-settings is compatible with pydantic...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings>=2.0.0", "--force-reinstall"])
            print("pydantic-settings upgraded to a compatible version")
        else:
            print("pydantic-settings not installed. Installing compatible version...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic-settings>=2.0.0"])
            print("pydantic-settings installed")
        
        print("\nDependencies fixed. You should now be able to run the tests.")
        print("If you still encounter issues, consider downgrading to Python 3.12.3.")
    else:
        print("Python version is less than 3.13. No action needed.")

if __name__ == "__main__":
    main() 