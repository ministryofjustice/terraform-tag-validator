#!/usr/bin/env python3
"""
Validates that all Terraform resources have required MoJ tags.
Supports both hardcoded defaults and YAML configuration files.
"""
import json
import sys
import re
import os
import glob
import fnmatch
from typing import Dict, List, Set, Optional, Tuple

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Default MoJ tagging standard (used if no config file provided)
DEFAULT_REQUIRED_TAGS = {
    "business-unit": [
        "HMPPS", "OPG", "LAA", "Central Digital",
        "Technology Services", "HMCTS", "CICA", "Platforms"
    ],
    "application": None,  # Any value OK
    "owner": None,  # Format validated by regex below
    "is-production": ["true", "false"],
    "service-area": None,  # Any value OK
    "environment-name": ["production", "staging", "test", "development"]
}

# Default tag format validation (regex patterns)
DEFAULT_TAG_FORMATS = {
    "owner": {
        "pattern": r'^.+:\s+\S+@\S+\.\S+$',
        "description": "Must be format: '<team-name>: <team-email>' (e.g., 'WebOps: webops@digital.justice.gov.uk')"
    }
}

# Global config (set by load_config or defaults)
REQUIRED_TAGS = DEFAULT_REQUIRED_TAGS.copy()
TAG_FORMATS = DEFAULT_TAG_FORMATS.copy()
EXCLUDE_RESOURCES: List[str] = []


def load_config(config_path: str) -> bool:
    """
    Load tag validation configuration from a YAML file.
    Returns True if config was loaded successfully, False otherwise.
    Falls back to default MoJ config if file not found or YAML not available.
    """
    global REQUIRED_TAGS, TAG_FORMATS, EXCLUDE_RESOURCES
    
    if not YAML_AVAILABLE:
        print("⚠️  PyYAML not installed. Using default MoJ configuration.")
        print("   Install with: pip install pyyaml")
        return False
    
    if not os.path.exists(config_path):
        print(f"⚠️  Config file not found: {config_path}")
        print("   Using default MoJ configuration.")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config:
            return False
        
        # Parse required_tags section
        if 'required_tags' in config:
            REQUIRED_TAGS = {}
            TAG_FORMATS = {}
            
            for tag_name, tag_config in config['required_tags'].items():
                if isinstance(tag_config, dict):
                    # Check for allowed_values
                    if 'allowed_values' in tag_config:
                        REQUIRED_TAGS[tag_name] = tag_config['allowed_values']
                    else:
                        REQUIRED_TAGS[tag_name] = None
                    
                    # Check for regex pattern
                    if 'pattern' in tag_config:
                        TAG_FORMATS[tag_name] = {
                            'pattern': tag_config['pattern'],
                            'description': tag_config.get('pattern_description', 
                                                         f'Must match pattern: {tag_config["pattern"]}')
                        }
                else:
                    # Simple tag without constraints
                    REQUIRED_TAGS[tag_name] = None
        
        # Parse exclude_resources section
        if 'exclude_resources' in config:
            EXCLUDE_RESOURCES = config['exclude_resources'] or []
        
        print(f"✅ Loaded configuration from {config_path}")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML config: {e}")
        print("   Using default MoJ configuration.")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        print("   Using default MoJ configuration.")
        return False


def should_exclude_resource(resource_address: str) -> bool:
    """
    Check if a resource should be excluded from validation.
    Supports exact matches and wildcard patterns.
    """
    for pattern in EXCLUDE_RESOURCES:
        if fnmatch.fnmatch(resource_address, pattern):
            return True
    return False


def parse_required_tags(tags_input: str) -> List[str]:
    """Parse required tags from input (comma-separated or newline-separated)."""
    tags = []
    
    # Handle both comma-separated and newline-separated
    if ',' in tags_input:
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]
    else:
        tags = [t.strip() for t in tags_input.split('\n') if t.strip()]
    
    return tags


def find_resource_location(resource_address: str, terraform_dir: str = '.') -> Optional[Tuple[str, int]]:
    """
    Find the file and line number where a resource is defined.
    Returns (filename, line_number) or None if not found.
    """
    # Extract resource type and name from address
    # e.g., "aws_s3_bucket.my_bucket" -> type="aws_s3_bucket", name="my_bucket"
    match = re.match(r'([^.]+)\.(.+)', resource_address)
    if not match:
        return None
    
    resource_type, resource_name = match.groups()
    
    # Pattern to match resource definitions
    # e.g., resource "aws_s3_bucket" "my_bucket" {
    pattern = re.compile(
        rf'resource\s+"({resource_type})"\s+"({resource_name})"\s*\{{',
        re.MULTILINE
    )
    
    # Search all .tf files
    for tf_file in glob.glob(os.path.join(terraform_dir, '*.tf')):
        try:
            with open(tf_file, 'r') as f:
                content = f.read()
                match = pattern.search(content)
                if match:
                    # Count line number
                    line_num = content[:match.start()].count('\n') + 1
                    return (os.path.basename(tf_file), line_num)
        except Exception:
            continue
    
    return None


def validate_terraform_plan(plan_file: str, required_tags_input: str) -> int:
    """
    Validate tags in Terraform plan JSON.
    Returns 0 if valid, 1 if violations found.
    """
    required_tags = parse_required_tags(required_tags_input)
    
    print(f"\n📋 Checking for tags: {', '.join(required_tags)}\n")
    
    with open(plan_file, 'r') as f:
        plan = json.load(f)
    
    # Get terraform directory (where .tf files are)
    terraform_dir = os.path.dirname(os.path.abspath(plan_file))
    
    violations = []
    resources_checked = 0
    
    for resource in plan.get('resource_changes', []):
        # Skip resources being deleted or not changing
        actions = resource.get('change', {}).get('actions', [])
        if actions == ['delete'] or actions == ['no-op']:
            continue
        
        resource_type = resource.get('type', '')
        resource_address = resource.get('address', '')
        
        # Check if resource should be excluded
        if should_exclude_resource(resource_address):
            continue
        
        # Get tags from the resource
        # Prefer tags_all (AWS provider v3.38.0+) as it includes provider default_tags
        after = resource.get('change', {}).get('after', {})
        tags_all = after.get('tags_all')
        tags = after.get('tags')
        
        # Skip resources that don't support tagging (no tags or tags_all field)
        if tags_all is None and tags is None:
            continue
        
        # Use tags_all if available, otherwise fall back to tags
        if isinstance(tags_all, dict):
            tags = tags_all
        elif not isinstance(tags, dict):
            tags = {}
        
        resources_checked += 1
        
        # Check each required tag
        missing_tags = []
        invalid_tags = []
        
        for tag in required_tags:
            if tag not in tags:
                missing_tags.append(tag)
            else:
                # Check if tag value is empty or None
                tag_value = tags[tag]
                if not tag_value or str(tag_value).strip() == '':
                    missing_tags.append(f"{tag} (empty value)")
                else:
                    # Validate against allowed values (if specified)
                    if tag in REQUIRED_TAGS and REQUIRED_TAGS[tag] is not None:
                        allowed_values = REQUIRED_TAGS[tag]
                        if tag_value not in allowed_values:
                            invalid_tags.append({
                                'tag': tag,
                                'value': tag_value,
                                'allowed': allowed_values
                            })
                    
                    # Validate tag format (if specified)
                    if tag in TAG_FORMATS:
                        format_spec = TAG_FORMATS[tag]
                        pattern = format_spec['pattern']
                        if not re.match(pattern, str(tag_value)):
                            invalid_tags.append({
                                'tag': tag,
                                'value': tag_value,
                                'format': format_spec['description']
                            })
        
        # Find source location
        location = find_resource_location(resource_address, terraform_dir)
        
        # Record violations
        if missing_tags:
            violations.append({
                'resource': resource_address,
                'location': location,
                'type': 'missing',
                'tags': missing_tags
            })
        
        if invalid_tags:
            for invalid in invalid_tags:
                violation = {
                    'resource': resource_address,
                    'location': location,
                    'type': 'invalid',
                    'tag': invalid['tag'],
                    'value': invalid['value']
                }
                if 'allowed' in invalid:
                    violation['allowed'] = invalid['allowed']
                if 'format' in invalid:
                    violation['format'] = invalid['format']
                violations.append(violation)
    
    # Print results
    print(f"📊 Resources checked: {resources_checked}\n")
    
    # Build summary for PR comments
    summary_lines = []
    
    if not violations:
        print("✅ All resources have required tags!\n")
        summary_lines.append("✅ All resources have required tags!")
        write_outputs([], summary_lines)
        return 0
    
    # Print violations
    print(f"❌ Found {len(violations)} violation(s):\n")
    summary_lines.append(f"❌ **Found {len(violations)} violation(s):**\n")
    
    for v in violations:
        resource = v['resource']
        location = v.get('location')
        
        # Format location
        location_str = ""
        if location:
            filename, line_num = location
            location_str = f" ({filename}:{line_num})"
        
        if v['type'] == 'missing':
            missing = ', '.join(v['tags'])
            print(f"  ❌ {resource}{location_str}")
            print(f"     Missing tags: {missing}\n")
            summary_lines.append(f"- **{resource}**{location_str}")
            summary_lines.append(f"  - Missing: `{missing}`")
        elif v['type'] == 'invalid':
            tag = v['tag']
            value = v['value']
            print(f"  ❌ {resource}{location_str}")
            print(f"     Invalid value for '{tag}': '{value}'")
            summary_lines.append(f"- **{resource}**{location_str}")
            summary_lines.append(f"  - Invalid `{tag}`: `{value}`")
            
            # Show either allowed values or format requirement
            if 'allowed' in v:
                allowed = ', '.join(v['allowed'])
                print(f"     Allowed values: {allowed}\n")
                summary_lines.append(f"  - Allowed: `{allowed}`")
            elif 'format' in v:
                print(f"     {v['format']}\n")
                summary_lines.append(f"  - {v['format']}")
    
    write_outputs(violations, summary_lines)
    return 1


def write_outputs(violations: List[Dict], summary_lines: List[str]) -> None:
    """Write outputs to GITHUB_OUTPUT file for action outputs."""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if not github_output:
        return
    
    try:
        with open(github_output, 'a') as f:
            # Write violations count
            f.write(f"violations_count={len(violations)}\n")
            
            # Write violations JSON (escape for multiline)
            violations_json = json.dumps(violations)
            f.write(f"violations={violations_json}\n")
            
            # Write summary (use heredoc for multiline)
            summary = '\n'.join(summary_lines)
            f.write(f"violations_summary<<EOF\n{summary}\nEOF\n")
    except Exception as e:
        print(f"Warning: Could not write outputs: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: validate_tags.py <plan.json> <required_tags> [config_file]")
        sys.exit(1)
    
    plan_file = sys.argv[1]
    required_tags = sys.argv[2]
    config_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Load config if provided
    if config_file:
        load_config(config_file)
    
    exit_code = validate_terraform_plan(plan_file, required_tags)
    sys.exit(exit_code)
