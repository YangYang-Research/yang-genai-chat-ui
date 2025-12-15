# Unit Tests

This directory contains unit tests for the yang-genai-chat-ui project.

## Test Structure

- `test_utils.py` - Tests for `helpers/utils.py` (file processing, formatting, etc.)
- `test_auth.py` - Tests for `helpers/auth.py` (JWT authentication, login functions)
- `test_http.py` - Tests for `helpers/http.py` (HTTP request methods)
- `conftest.py` - Shared pytest fixtures and configuration

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_utils.py
```

### Run with Coverage Report

```bash
pytest --cov=helpers --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test

```bash
pytest tests/test_utils.py::TestUtils::test_process_single_file_text
```

## Test Coverage

The tests aim to cover:
- File processing (text, image, document files)
- File size validation
- File type validation
- JWT token creation and verification
- Authentication flow
- HTTP request methods (GET, POST, PUT, DELETE)
- Error handling

## Notes

- Tests use mocking to avoid external dependencies (AWS, API calls, Streamlit)
- Some tests require proper mocking of Streamlit session state
- JWT tests use a test secret key for validation
