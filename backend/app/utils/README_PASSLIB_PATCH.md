# Passlib Bcrypt Patch for Newer Bcrypt Versions

## Issue

When using passlib with newer versions of bcrypt (4.x), you may encounter the following warning:

```
passlib.handlers.bcrypt - WARNING - (trapped) error reading bcrypt version
Traceback (most recent call last):
  File "/path/to/venv/lib/python3.13/site-packages/passlib/handlers/bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
              ^^^^^^^^^^^^^^^^^
AttributeError: module 'bcrypt' has no attribute '__about__'
```

This occurs because passlib is trying to access `bcrypt.__about__.__version__`, but in newer versions of bcrypt (4.x), the version information is stored differently.

## Solution

We've implemented a monkey patch in `passlib_patch.py` that:

1. Checks if bcrypt has the `__about__` attribute
2. If not, creates a fake `__about__` module with the `__version__` attribute
3. Monkey patches the `_load_backend_mixin` function in passlib to use this fake module
4. Filters out the specific warning

The patch is automatically applied when the application starts by adding these lines to `main.py`:

```python
# Apply passlib bcrypt patch for newer bcrypt versions
from app.utils.passlib_patch import apply_patch as apply_passlib_patch
apply_passlib_patch()
```

And similarly in `tests/conftest.py` for test runs.

## Additional Configuration

We've also updated `pytest.ini` to filter out these warnings during test runs:

```ini
[pytest]
filterwarnings =
    ignore::UserWarning:passlib.handlers.bcrypt:
```

## Long-term Solution

This patch is a temporary solution until passlib is updated to be fully compatible with newer versions of bcrypt.

When upgrading dependencies, consider:
1. Downgrading bcrypt to a version compatible with passlib (3.x)
2. Waiting for passlib to be updated to support bcrypt 4.x
3. Using this patch as a workaround 