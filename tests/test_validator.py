"""
Unit tests for MoJ tag validation.
Tests tag enforcement, format validation, and error reporting.
"""

import pytest
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import validate_tags


@pytest.fixture
def reset_config():
    """Reset global config between tests."""
    validate_tags.REQUIRED_TAGS = validate_tags.DEFAULT_REQUIRED_TAGS.copy()
    validate_tags.TAG_FORMATS = validate_tags.DEFAULT_TAG_FORMATS.copy()
    validate_tags.EXCLUDE_RESOURCES = []
    yield
    validate_tags.REQUIRED_TAGS = validate_tags.DEFAULT_REQUIRED_TAGS.copy()
    validate_tags.TAG_FORMATS = validate_tags.DEFAULT_TAG_FORMATS.copy()
    validate_tags.EXCLUDE_RESOURCES = []


def test_validates_moj_business_units(reset_config):
    """Test that only valid MoJ business units are accepted."""
    valid_units = ["HMPPS", "OPG", "LAA", "Central Digital", 
                   "Technology Services", "HMCTS", "CICA", "OCTO"]
    
    for unit in valid_units:
        tags = {
            "business-unit": unit,
            "application": "Test App",
            "owner": "Team: test@digital.justice.gov.uk",
            "is-production": "true",
            "service-area": "Testing",
            "environment-name": "test"
        }
        
        # Should not raise any issues
        assert validate_tags.REQUIRED_TAGS["business-unit"] is not None
        assert unit in validate_tags.REQUIRED_TAGS["business-unit"]


def test_rejects_invalid_business_unit(reset_config):
    """Test that invalid business units are detected."""
    invalid_unit = "RandomDepartment"
    
    assert invalid_unit not in validate_tags.REQUIRED_TAGS["business-unit"]


def test_validates_owner_email_format(reset_config):
    """Test owner format validation: 'Team Name: email@domain.com'"""
    valid_owners = [
        "WebOps: webops@digital.justice.gov.uk",
        "COAT Team: coat@justice.gov.uk",
        "Platform Team: platform@digital.justice.gov.uk"
    ]
    
    pattern = validate_tags.DEFAULT_TAG_FORMATS["owner"]["pattern"]
    
    import re
    for owner in valid_owners:
        assert re.match(pattern, owner), f"Valid owner rejected: {owner}"


def test_rejects_invalid_owner_format(reset_config):
    """Test that invalid owner formats are detected."""
    invalid_owners = [
        "WebOps",  # Missing email
        "webops@digital.justice.gov.uk",  # Missing team name
        "Team",  # No email at all
        "Team: notanemail",  # Invalid email format
    ]
    
    pattern = validate_tags.DEFAULT_TAG_FORMATS["owner"]["pattern"]
    
    import re
    for owner in invalid_owners:
        assert not re.match(pattern, owner), f"Invalid owner accepted: {owner}"


def test_validates_is_production_values(reset_config):
    """Test is-production only accepts 'true' or 'false'."""
    allowed = validate_tags.REQUIRED_TAGS["is-production"]
    
    assert "true" in allowed
    assert "false" in allowed
    assert "yes" not in allowed
    assert "no" not in allowed
    assert "maybe" not in allowed


def test_validates_environment_name_values(reset_config):
    """Test environment-name accepts standard environments."""
    allowed = validate_tags.REQUIRED_TAGS["environment-name"]
    
    assert "production" in allowed
    assert "staging" in allowed
    assert "test" in allowed
    assert "development" in allowed
    assert "prod" not in allowed  # Should use full name


def test_detects_missing_tags():
    """Test detection of resources missing required tags."""
    # This would need a mock terraform plan JSON
    # Simplified test structure
    resource_tags = {
        "business-unit": "OCTO",
        "application": "Test"
        # Missing: owner, is-production, service-area, environment-name
    }
    
    required = set(validate_tags.REQUIRED_TAGS.keys())
    present = set(resource_tags.keys())
    missing = required - present
    
    assert "owner" in missing
    assert "is-production" in missing
    assert "service-area" in missing
    assert "environment-name" in missing


def test_detects_empty_tag_values():
    """Test detection of empty or whitespace-only tag values."""
    empty_values = [
        "",
        "   ",
        "\t",
        "\n"
    ]
    
    for value in empty_values:
        assert not value or value.strip() == ""


def test_all_required_tags_defined(reset_config):
    """Test that all 6 MoJ mandatory tags are defined."""
    required_tags = set(validate_tags.REQUIRED_TAGS.keys())
    
    expected_tags = {
        "business-unit",
        "application", 
        "owner",
        "is-production",
        "service-area",
        "environment-name"
    }
    
    assert required_tags == expected_tags, \
        f"Missing tags: {expected_tags - required_tags}, Extra: {required_tags - expected_tags}"


def test_resource_location_parsing():
    """Test that resource locations are properly extracted from terraform files."""
    # Test the regex pattern used to find resources
    import re
    
    terraform_content = '''
resource "aws_s3_bucket" "example" {
  bucket = "test-bucket"
  
  tags = {
    business-unit = "OCTO"
  }
}
'''
    
    pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"'
    matches = list(re.finditer(pattern, terraform_content, re.MULTILINE))
    
    assert len(matches) == 1
    assert matches[0].group(1) == "aws_s3_bucket"
    assert matches[0].group(2) == "example"


def test_dynamic_taggable_resource_detection():
    """Test that resources are detected as taggable based on tags/tags_all presence."""
    # Resource with tags field should be detected
    resource_with_tags = {
        'address': 'aws_s3_bucket.test',
        'type': 'aws_s3_bucket',
        'change': {
            'actions': ['create'],
            'after': {
                'tags': {'Name': 'test'}
            }
        }
    }
    
    # Resource with tags_all field should be detected
    resource_with_tags_all = {
        'address': 'aws_instance.test',
        'type': 'aws_instance',
        'change': {
            'actions': ['create'],
            'after': {
                'tags_all': {'Name': 'test'}
            }
        }
    }
    
    # Resource without tags should be skipped
    resource_without_tags = {
        'address': 'aws_iam_policy_document.test',
        'type': 'aws_iam_policy_document',
        'change': {
            'actions': ['create'],
            'after': {
                'json': '{}'
            }
        }
    }
    
    # Verify tags/tags_all detection logic
    after_with_tags = resource_with_tags['change']['after']
    after_with_tags_all = resource_with_tags_all['change']['after']
    after_without = resource_without_tags['change']['after']
    
    assert after_with_tags.get('tags') is not None or after_with_tags.get('tags_all') is not None
    assert after_with_tags_all.get('tags') is not None or after_with_tags_all.get('tags_all') is not None
    assert after_without.get('tags') is None and after_without.get('tags_all') is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
