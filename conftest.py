"""Global pytest configuration."""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def samples_dir(project_root):
    """Get the samples directory path."""
    return project_root / "resources" / "mermaid_graphs"