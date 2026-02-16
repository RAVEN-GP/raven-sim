import os
import pytest

def test_src_exists():
    """Verify src directory exists."""
    assert os.path.exists("src")

def test_readme_exists():
    """Verify README exists."""
    assert os.path.exists("README.md")
