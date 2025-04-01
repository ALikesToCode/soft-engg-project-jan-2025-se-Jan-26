# Python 3.13 Compatibility Issues

This document explains the compatibility issues with Python 3.13 and how to fix them.

## Issues

When running the tests with Python 3.13, you may encounter the following errors:

1. **Passlib bcrypt patch error**:
   ```
   Failed to apply passlib bcrypt patch: module 'passlib.handlers.bcrypt' has no attribute '_load_backend_mixin'
   ```

2. **Pydantic type evaluation error**:
   ```
   TypeError: apply_patch.<locals>.patched_evaluate() got multiple values for argument 'recursive_guard'
   ```

These errors occur because:
- Newer versions of bcrypt (4.1.x+) don't have the `__about__` attribute that passlib tries to access.
- Python 3.13 changed how the `ForwardRef._evaluate` method works, causing issues with Pydantic's type evaluation.

## Solutions

### Option 1: Fix Dependencies (Recommended)

Run the provided script to fix the dependencies:

```bash
python fix_dependencies.py
```

This script will:
- Downgrade bcrypt to 4.0.1 (which is compatible with passlib)
- Upgrade pydantic to 2.7.4 or newer (which is compatible with Python 3.13)
- Upgrade pydantic-settings to a compatible version

### Option 2: Downgrade Python

If the above solution doesn't work, you can downgrade to Python 3.12.3:

```bash
# For Arch-based systems (like Artix)
sudo pacman -S python312

# Create a new virtual environment with Python 3.12
python3.12 -m venv --clear venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 3: Use the Patches

We've added patches to fix these issues:

1. **Passlib Patch**: `app/utils/passlib_patch.py`
   - Adds a fake `__about__` attribute to bcrypt
   - Monkey patches `_load_backend_mixin` if it exists

2. **Pydantic Patch**: `app/utils/pydantic_patch.py`
   - Replaces the `ForwardRef` class with a custom implementation
   - Patches `evaluate_forwardref` to handle the recursive_guard parameter

3. **Python Typing Patch**: `app/utils/typing_patch.py`
   - Directly patches Python's `ForwardRef._evaluate` method
   - Handles the case where recursive_guard is passed both positionally and as a keyword

These patches are automatically applied in `conftest.py`.

## Troubleshooting

If you still encounter issues:

1. **Check your Python installation**:
   ```bash
   python --version
   which python
   ```

2. **Check your virtual environment**:
   ```bash
   echo $VIRTUAL_ENV
   ```

3. **Check installed package versions**:
   ```bash
   pip list | grep -E "bcrypt|passlib|pydantic"
   ```

4. **Recreate your virtual environment**:
   ```bash
   python -m venv --clear venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Try with Python 3.12**:
   ```bash
   python3.12 -m pytest tests/
   ```

6. **Try a clean install of dependencies**:
   ```bash
   pip uninstall -y bcrypt passlib pydantic pydantic-settings
   pip install bcrypt==4.0.1 pydantic>=2.7.4 pydantic-settings>=2.0.0 passlib
   ```

## References

- [Pydantic Issue #9609](https://github.com/pydantic/pydantic/issues/9609)
- [Bcrypt Issue #684](https://github.com/pyca/bcrypt/issues/684)
- [Passlib Issue #132](https://foss.heptapod.net/python-libs/passlib/-/issues/132) 