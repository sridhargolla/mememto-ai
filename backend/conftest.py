import os
import tempfile

import pytest

# Create a session-wide temporary database file and set it in the environment
# before any test or application modules are imported.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_PATH"] = _db_path


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    try:
        if os.path.exists(_db_path):
            os.remove(_db_path)
    except Exception:
        pass
