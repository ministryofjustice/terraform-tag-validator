#!/usr/bin/env python3
"""
Validates that all Terraform resources have required MoJ tags.
"""
import json
import sys
import re
import os
import glob
from typing import Dict, List, Set, Optional, Tuple

# MoJ tagging standard
REQUIRED_TAGS = {
    "business-unit": [
        "HMPPS", "OPG", "LAA", "Central Digital",
        "Technology Services", "HMCTS", "CICA", "Platforms"
    ],
    "application": None,  # Any value OK
    "owner": None,  # Format: "team-name: team-email"
    "is-production": ["true", "false"],
    "service-area": None  # Any value OK
}

# AWS resources that support tagging
TAGGABLE_RESOURCES = {
    "aws_s3_bucket",
    "aws_instance",
    "aws_db_instance",
    "aws_rds_cluster",
    "aws_lambda_function",
    "aws_dynamodb_table",
    "aws_ecs_cluster",
    "aws_ecs_service",
    "aws_eks_cluster",
    "aws_vpc",
    "aws_subnet",
    "aws_security_group",
    "aws_iam_role",
    "aws_kms_key",
    "aws_cloudwatch_log_group",
    "aws_ecr_repository",
    "aws_elasticache_cluster",
    "aws_elasticsearch_domain",
    "aws_opensearch_domain",
    "aws_route53_zone",
    "aws_acm_certificate",
    "aws_elb",
    "aws_lb",
    "aws_alb",
    "aws_api_gateway_rest_api",
    "aws_apigatewayv2_api",
}


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
        
        # Only check taggable resources
        if resource_type not in TAGGABLE_RESOURCES:
            continue
        
        resources_checked += 1
        
        # Get tags from the resource
        after = resource.get('change', {}).get('after', {})
        tags = after.get('tags')
        
        # Handle resources with no tags block at all (tags = None or other falsy values)
        if not isinstance(tags, dict):
            tags = {}
        
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
                elif tag in REQUIRED_TAGS and REQUIRED_TAGS[tag] is not None:
                    # Validate against allowed values
                    allowed_values = REQUIRED_TAGS[tag]
                    if tag_value not in allowed_values:
                        invalid_tags.append({
                            'tag': tag,
                            'value': tag_value,
                            'allowed': allowed_values
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
                violations.append({
                    'resource': resource_address,
                    'location': location,
                    'type': 'invalid',
                    'tag': invalid['tag'],
                    'value': invalid['value'],
                    'allowed': invalid['allowed']
                })
    
    # Print results
    print(f"📊 Resources checked: {resources_checked}\n")
    
    if not violations:
        print("✅ All resources have required tags!\n")
        return 0
    
    # Print violations
    print(f"❌ Found {len(violations)} violation(s):\n")
    
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
        elif v['type'] == 'invalid':
            tag = v['tag']
            value = v['value']
            allowed = ', '.join(v['allowed'])
            print(f"  ❌ {resource}{location_str}")
            print(f"     Invalid value for '{tag}': '{value}'")
            print(f"     Allowed values: {allowed}\n")
    
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: validate_tags.py <plan.json> <required_tags>")
        sys.exit(1)
    
    plan_file = sys.argv[1]
    required_tags = sys.argv[2]
    
    exit_code = validate_terraform_plan(plan_file, required_tags)
    sys.exit(exit_code)
