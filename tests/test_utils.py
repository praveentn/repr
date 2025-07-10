# tests/test_utils.py
"""
Test cases for utility functions
"""

import pytest
import tempfile
from pathlib import Path
from core.utils import FileUtils, ValidationUtils, HashUtils

def test_file_utils_ensure_directory():
    """Test directory creation utility."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_path = Path(temp_dir) / "test" / "nested" / "directory"
        
        result = FileUtils.ensure_directory(test_path)
        assert result is True
        assert test_path.exists()
        assert test_path.is_dir()

def test_file_utils_safe_write_read():
    """Test safe file write and read operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        test_content = "This is test content\nWith multiple lines"
        
        # Test write
        write_result = FileUtils.safe_write_file(test_file, test_content)
        assert write_result is True
        assert test_file.exists()
        
        # Test read
        read_content = FileUtils.safe_read_file(test_file)
        assert read_content == test_content

def test_validation_utils_email():
    """Test email validation."""
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "test+tag@example.org"
    ]
    
    invalid_emails = [
        "invalid-email",
        "@example.com",
        "test@",
        "test..test@example.com"
    ]
    
    for email in valid_emails:
        assert ValidationUtils.validate_email(email), f"Should be valid: {email}"
    
    for email in invalid_emails:
        assert not ValidationUtils.validate_email(email), f"Should be invalid: {email}"

def test_validation_utils_json():
    """Test JSON validation."""
    valid_json = '{"key": "value", "number": 123}'
    invalid_json = '{"key": "value", "incomplete":'
    
    assert ValidationUtils.validate_json(valid_json)
    assert not ValidationUtils.validate_json(invalid_json)

def test_validation_utils_limit_string():
    """Test string length limiting."""
    long_string = "This is a very long string that should be truncated"
    max_length = 20
    
    result = ValidationUtils.limit_string_length(long_string, max_length)
    
    assert len(result) <= max_length
    assert result.endswith("...")

def test_hash_utils_content_hash():
    """Test content hashing."""
    content1 = "Test content"
    content2 = "Test content"
    content3 = "Different content"
    
    hash1 = HashUtils.generate_content_hash(content1)
    hash2 = HashUtils.generate_content_hash(content2)
    hash3 = HashUtils.generate_content_hash(content3)
    
    assert hash1 == hash2  # Same content should have same hash
    assert hash1 != hash3  # Different content should have different hash
    assert len(hash1) == 64  # SHA256 hash length


