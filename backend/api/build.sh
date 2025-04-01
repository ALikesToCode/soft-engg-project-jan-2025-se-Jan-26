#!/bin/bash

echo "Starting build process for Vercel deployment..."

# Move to the parent directory to run the main build script
cd ..

# Run the main build script
./build.sh

# Return to the api directory
cd api

echo "API directory build completed successfully!" 