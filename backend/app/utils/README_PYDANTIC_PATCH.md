# Pydantic v1 Patch for Python 3.13 Compatibility

## Issue

When running the application with Python 3.13, you may encounter the following deprecation warning:

```
/path/to/venv/lib/python3.13/site-packages/pydantic/v1/typing.py:68: DeprecationWarning: 
Failing to pass a value to the 'type_params' parameter of 'typing.ForwardRef._evaluate' is deprecated, 
as it leads to incorrect behaviour when calling typing.ForwardRef._evaluate on a stringified annotation 
that references a PEP 695 type parameter. It will be disallowed in Python 3.15.
```

This occurs because Pydantic v1 (which is still used by some dependencies even when Pydantic v2 is installed) 
doesn't pass the `type_params` parameter to `ForwardRef._evaluate`, which is now required in Python 3.13.

## Solution

We've implemented a monkey patch in `pydantic_patch.py` that:

1. Patches the `ForwardRef._evaluate` method in Pydantic v1 to handle the `type_params` parameter correctly
2. Filters out the specific deprecation warning

The patch is automatically applied when the application starts by adding these lines to `main.py`:

```python
# Apply Pydantic v1 patch for Python 3.13 compatibility
from app.utils.pydantic_patch import apply_patch
apply_patch()
```

And similarly in `tests/conftest.py` for test runs.

## Additional Configuration

We've also updated `pytest.ini` to filter out these deprecation warnings during test runs:

```ini
[pytest]
filterwarnings =
    ignore::DeprecationWarning:pydantic.v1.typing:
    ignore::DeprecationWarning:typing:
```

## Running Tests

To run tests with the patch applied, you can use the provided script:

```bash
./run_patched_tests.sh
```

## Long-term Solution

This patch is a temporary solution until all dependencies are updated to use Pydantic v2 exclusively or until Pydantic v1 is updated to be fully compatible with Python 3.13.

When upgrading dependencies, prioritize those that still rely on Pydantic v1. 