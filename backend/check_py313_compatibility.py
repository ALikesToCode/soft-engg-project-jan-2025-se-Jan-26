#!/usr/bin/env python3
"""
Check for Python 3.13 compatibility issues in installed packages.

This script checks for common compatibility issues with Python 3.13,
such as dependencies on removed modules like 'pipes'.
"""
import sys
import importlib
import pkg_resources
import subprocess
import re

def check_package_for_imports(package_name, problematic_modules):
    """Check if a package imports problematic modules."""
    try:
        # Get the package location
        package = pkg_resources.get_distribution(package_name)
        package_location = package.location
        package_path = f"{package_location}/{package.project_name.replace('-', '_')}"
        
        # Use grep to find imports of problematic modules
        for module in problematic_modules:
            try:
                result = subprocess.run(
                    ["grep", "-r", f"import {module}", package_path],
                    capture_output=True,
                    text=True
                )
                if result.stdout:
                    print(f"⚠️  {package_name} imports removed module '{module}':")
                    for line in result.stdout.splitlines():
                        print(f"   {line}")
                    return True
            except Exception as e:
                print(f"Error checking {package_name} for {module} imports: {e}")
        
        return False
    except Exception as e:
        print(f"Error checking package {package_name}: {e}")
        return False

def main():
    """Main function to check for Python 3.13 compatibility issues."""
    print("Checking for Python 3.13 compatibility issues...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major != 3 or python_version.minor < 13:
        print("This script is intended to check for Python 3.13 compatibility issues.")
        print("You are not using Python 3.13, but we'll check anyway.")
    
    # List of modules removed in Python 3.13
    removed_modules = [
        "pipes",
        "asyncore",
        "asynchat",
        "audioop",
        "cgi",
        "cgitb",
        "chunk",
        "crypt",
        "imghdr",
        "mailcap",
        "msilib",
        "nis",
        "nntplib",
        "ossaudiodev",
        "parser",
        "spwd",
        "sunau",
        "telnetlib",
        "uu",
        "xdrlib"
    ]
    
    # Get installed packages
    installed_packages = [pkg.key for pkg in pkg_resources.working_set]
    
    # Check each package for imports of removed modules
    problematic_packages = []
    for package in installed_packages:
        if check_package_for_imports(package, removed_modules):
            problematic_packages.append(package)
    
    # Print summary
    print("\nSummary:")
    if problematic_packages:
        print(f"Found {len(problematic_packages)} packages with potential Python 3.13 compatibility issues:")
        for package in problematic_packages:
            print(f"- {package}")
        print("\nRecommendations:")
        print("1. Consider downgrading to Python 3.12 if these packages are essential.")
        print("2. Look for updated versions of these packages that support Python 3.13.")
        print("3. Consider forking and fixing these packages if they are open source.")
    else:
        print("No obvious compatibility issues found with installed packages.")
        print("However, this doesn't guarantee that all packages will work correctly with Python 3.13.")
    
    print("\nFor more information on Python 3.13 changes, see:")
    print("https://docs.python.org/3.13/whatsnew/3.13.html")

if __name__ == "__main__":
    main() 