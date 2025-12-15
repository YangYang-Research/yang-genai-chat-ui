"""
Pytest configuration and shared fixtures.
"""
import pytest
from unittest.mock import Mock, MagicMock
import os
from pathlib import Path


@pytest.fixture
def mock_file():
    """Create a mock file object for testing."""
    file = Mock()
    file.name = "test_file.txt"
    file.type = "text/plain"
    file.read.return_value = b"test content"
    return file


@pytest.fixture
def mock_image_file():
    """Create a mock image file object for testing."""
    file = Mock()
    file.name = "test_image.png"
    file.type = "image/png"
    file.read.return_value = b"fake image content"
    return file


@pytest.fixture
def mock_document_file():
    """Create a mock document file object for testing."""
    file = Mock()
    file.name = "test_document.pdf"
    file.type = "application/pdf"
    file.read.return_value = b"fake pdf content"
    return file


@pytest.fixture
def mock_large_file():
    """Create a mock large file object for testing."""
    file = Mock()
    file.name = "large_file.pdf"
    file.type = "application/pdf"
    # Create content larger than max size (11 MB)
    file.read.return_value = b"x" * (11 * 1024 * 1024)
    return file


@pytest.fixture
def mock_file_config(monkeypatch):
    """Mock FileConfig with test values."""
    monkeypatch.setenv("ALLOWED_FILE_TYPES", "txt,html,md,pdf,docx,doc,png,jpg,jpeg,csv,xlsx,xls")
    monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "10")
    from helpers.config import FileConfig
    return FileConfig()


@pytest.fixture
def mock_cookie_manager():
    """Mock cookie manager for testing."""
    return MagicMock()


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QifQ.test"


@pytest.fixture
def mock_user_info():
    """Mock user info dictionary."""
    return {
        "username": "testuser",
        "user_id": "123",
        "role": "admin"
    }
