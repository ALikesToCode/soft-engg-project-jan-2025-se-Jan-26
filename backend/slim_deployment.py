"""
Package Optimizer Script for Vercel Deployment

This script reduces the size of installed Python packages by removing
unnecessary files like tests, documentation, examples, and other
non-essential components. It's designed to be run after package
installation but before deployment to bring the deployment size
under Vercel's limits.
"""

import os
import shutil
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reduce_package_size():
    """
    Reduce the size of installed packages by removing unnecessary files.
    This function targets common large packages and removes non-essential
    components like tests, documentation, and development files.
    """
    try:
        # Find site-packages directory
        site_packages = None
        for path in sys.path:
            if path.endswith('site-packages'):
                site_packages = path
                break

        if not site_packages:
            logger.error("Could not find site-packages directory")
            return

        logger.info(f"Found site-packages at: {site_packages}")
        site_packages_path = Path(site_packages)

        # Patterns to remove from all packages
        patterns_to_remove = [
            # Tests and development files
            "**/tests/**",
            "**/test/**",
            "**/*_test.py",
            "**/*_tests.py",
            "**/.pytest_cache/**",
            "**/testing/**",
            
            # Documentation
            "**/docs/**",
            "**/doc/**",
            "**/README*",
            "**/CHANGELOG*",
            "**/LICENSE*",
            "**/CONTRIBUTING*",
            
            # Development files
            "**/.git/**",
            "**/.github/**",
            "**/examples/**",
            "**/sample/**",
            "**/.gitignore",
            "**/.travis.yml",
            "**/requirements-dev.txt",
            "**/setup.py",
            
            # Compiled extensions that might not be used
            "**/*.so",
            "**/*.dll",
            "**/*.dylib",
            "**/*.a",
            
            # Type stubs (can be removed if not using type checking)
            "**/*.pyi",
            "**/py.typed",
            
            # Jupyter notebooks and data files
            "**/*.ipynb",
            "**/*.ipynb_checkpoints/**",
        ]
        
        # Packages that we should be more aggressive with
        packages_to_optimize = [
            # LLM and LangChain related
            "langchain",
            "langchain_core",
            "langchain_google_genai",
            "langchain_postgres",
            "langchain_community",
            "google_generativeai", 
            
            # Data processing packages
            "sqlalchemy",
            "pydantic",
            
            # Unused components of larger packages
            "alembic",
            "aiohttp",
            "fastapi/openapi",
            "uvicorn/lifespan",
            
            # Other large packages
            "psutil",
            "psycopg2_binary",
            "passlib",
            "email_validator",
        ]
        
        removal_count = 0
        total_size_saved = 0
        
        # Process packages that should be more aggressively optimized
        for package in packages_to_optimize:
            package_path = site_packages_path / package.replace("/", os.sep)
            if package_path.exists():
                logger.info(f"Optimizing package: {package}")
                
                # First measure the size
                package_size_before = get_directory_size(package_path)
                
                # Apply optimizations to this package
                for pattern in patterns_to_remove:
                    for file_path in package_path.glob(pattern):
                        if file_path.exists():
                            size = get_file_or_dir_size(file_path)
                            if file_path.is_dir():
                                shutil.rmtree(file_path, ignore_errors=True)
                            else:
                                try:
                                    os.remove(file_path)
                                except PermissionError:
                                    logger.warning(f"Could not remove {file_path} due to permission error")
                            removal_count += 1
                            total_size_saved += size
                
                # Calculate and log size reduction
                package_size_after = get_directory_size(package_path)
                reduction = package_size_before - package_size_after
                if reduction > 0:
                    percentage = (reduction / package_size_before) * 100
                    logger.info(f"  Reduced {package} by {reduction / 1024 / 1024:.2f} MB ({percentage:.1f}%)")
        
        # Special package-specific optimizations
        if (site_packages_path / "langchain").exists():
            # Remove unused model providers
            providers_path = site_packages_path / "langchain" / "llms" / "providers"
            if providers_path.exists():
                keep_providers = ["google", "openai"]
                for provider in providers_path.iterdir():
                    if provider.is_dir() and provider.name not in keep_providers:
                        size = get_directory_size(provider)
                        shutil.rmtree(provider, ignore_errors=True)
                        total_size_saved += size
                        removal_count += 1
                        logger.info(f"Removed provider: {provider.name}")
        
        # Log results
        logger.info(f"Package optimization complete.")
        logger.info(f"Removed {removal_count} files/directories")
        logger.info(f"Total size saved: {total_size_saved / 1024 / 1024:.2f} MB")
    
    except Exception as e:
        logger.error(f"Error optimizing packages: {str(e)}")
        raise

def get_file_or_dir_size(path):
    """Get the size of a file or directory in bytes"""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        return get_directory_size(path)
    return 0

def get_directory_size(path):
    """Calculate the total size of a directory"""
    total = 0
    for entry in path.glob('**/*'):
        if entry.is_file():
            total += entry.stat().st_size
    return total

if __name__ == "__main__":
    logger.info("Starting package optimization...")
    reduce_package_size()
    logger.info("Package optimization completed successfully") 