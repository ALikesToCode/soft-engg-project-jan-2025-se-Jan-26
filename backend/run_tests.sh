#!/bin/bash

# Script to run tests with optimizations

# Set environment variables for testing
export TESTING=True
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export JWT_SECRET_KEY="test_secret_key_for_testing_purposes_only"
export JWT_ALGORITHM="HS256"
export JWT_EXPIRATION=3600
export UPLOAD_DIR="./tests/test_uploads"
export REDIS_URL="redis://localhost:6379/0"
export TEST_USE_SQLITE="true"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
PYTHON_3_13=false
if [[ $PYTHON_VERSION == *"3.13"* ]]; then
    PYTHON_3_13=true
    echo "Python 3.13 detected. Some features like pytest-profiling are not available."
fi

# Check if pytest-xdist is installed
if pip list | grep -q pytest-xdist; then
    PARALLEL="-n auto"
else
    PARALLEL=""
    echo "pytest-xdist not installed. Running tests sequentially."
    echo "Install with: pip install pytest-xdist"
fi

# Check if profiling is available
PROFILING_AVAILABLE=false
if [ "$PYTHON_3_13" = false ] && pip list | grep -q pytest-profiling; then
    PROFILING_AVAILABLE=true
else
    echo "Profiling with pytest-profiling is not available."
    if [ "$PYTHON_3_13" = true ]; then
        echo "pytest-profiling is not compatible with Python 3.13 (uses removed 'pipes' module)."
        echo "Using cProfile instead for basic profiling."
    else
        echo "Install with: pip install pytest-profiling"
    fi
fi

# Parse command line arguments
COVERAGE=false
PROFILING=false
FAILED_FIRST=false
MARKERS=""
SPECIFIC_TESTS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --profile)
            PROFILING=true
            shift
            ;;
        --failed-first)
            FAILED_FIRST=true
            shift
            ;;
        --unit)
            MARKERS="unit"
            shift
            ;;
        --integration)
            MARKERS="integration"
            shift
            ;;
        --api)
            MARKERS="api"
            shift
            ;;
        --model)
            MARKERS="model"
            shift
            ;;
        --service)
            MARKERS="service"
            shift
            ;;
        --auth)
            MARKERS="auth"
            shift
            ;;
        --llm)
            MARKERS="llm"
            shift
            ;;
        --chat)
            MARKERS="chat"
            shift
            ;;
        --academic-integrity)
            MARKERS="academic_integrity"
            shift
            ;;
        --assignment)
            MARKERS="assignment"
            shift
            ;;
        --analytics)
            MARKERS="analytics"
            shift
            ;;
        --not-slow)
            MARKERS="not slow"
            shift
            ;;
        *)
            SPECIFIC_TESTS="$SPECIFIC_TESTS $1"
            shift
            ;;
    esac
done

# Build the command
CMD="python3 -m pytest"

# Add specific tests if provided
if [ -n "$SPECIFIC_TESTS" ]; then
    CMD="$CMD $SPECIFIC_TESTS"
else
    CMD="$CMD tests/"
fi

# Add markers if provided
if [ -n "$MARKERS" ]; then
    CMD="$CMD -m \"$MARKERS\""
fi

# Add failed first if requested
if [ "$FAILED_FIRST" = true ]; then
    CMD="$CMD --ff"
fi

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    CMD="$CMD --cov=app --cov-report=term-missing"
fi

# Add profiling if requested
if [ "$PROFILING" = true ]; then
    if [ "$PROFILING_AVAILABLE" = true ]; then
        # Use pytest-profiling if available
        CMD="$CMD --profile"
    elif [ "$PYTHON_3_13" = true ]; then
        # Use Python's built-in cProfile for Python 3.13
        echo "Using Python's built-in cProfile for profiling..."
        CMD="python -m cProfile -o profile.stats $CMD"
    fi
fi

# Add parallel execution if available
if [ -n "$PARALLEL" ]; then
    CMD="$CMD $PARALLEL"
fi

# Print the command
echo "Running: $CMD"

# Execute the command
eval $CMD

# If profiling was used with cProfile, print stats
if [ "$PROFILING" = true ] && [ "$PROFILING_AVAILABLE" = false ] && [ "$PYTHON_3_13" = true ]; then
    echo "Generating profiling stats..."
    python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(30)"
    echo "Full profiling stats saved to profile.stats"
fi

# If profiling was used with pytest-profiling, generate SVG
if [ "$PROFILING" = true ] && [ "$PROFILING_AVAILABLE" = true ]; then
    echo "Generating profiling SVG..."
    python -m pytest_profiling.svg
fi

# Print help information
echo ""
echo "Test run complete."
echo ""
echo "Usage:"
echo "  ./run_tests.sh [options] [specific_tests]"
echo ""
echo "Options:"
echo "  --coverage           Run with coverage report"
echo "  --profile            Run with profiling"
echo "  --failed-first       Run failed tests first"
echo "  --unit               Run only unit tests"
echo "  --integration        Run only integration tests"
echo "  --api                Run only API tests"
echo "  --model              Run only model tests"
echo "  --service            Run only service tests"
echo "  --auth               Run only authentication tests"
echo "  --llm                Run only LLM-related tests"
echo "  --chat               Run only chat-related tests"
echo "  --academic-integrity Run only academic integrity tests"
echo "  --assignment         Run only assignment-related tests"
echo "  --analytics          Run only analytics-related tests"
echo "  --not-slow           Skip slow tests"
echo ""
echo "Examples:"
echo "  ./run_tests.sh                                  # Run all tests"
echo "  ./run_tests.sh --coverage                       # Run all tests with coverage"
echo "  ./run_tests.sh --unit                           # Run only unit tests"
echo "  ./run_tests.sh --failed-first                   # Run failed tests first"
echo "  ./run_tests.sh tests/test_auth.py               # Run specific test file"
echo "  ./run_tests.sh --coverage tests/test_auth.py    # Run specific test file with coverage" 