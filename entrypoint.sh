#!/bin/bash
set -e

# Get inputs from environment variables
TERRAFORM_DIR="${INPUT_TERRAFORM_DIRECTORY:-.}"
REQUIRED_TAGS="${INPUT_REQUIRED_TAGS}"
CONFIG_FILE="${INPUT_CONFIG_FILE}"

echo "======================================"
echo "🔍 Terraform Tag Validation"
echo "======================================"
echo "📁 Directory: $TERRAFORM_DIR"
echo "📋 Required tags:"
echo "$REQUIRED_TAGS" | sed 's/^/  - /'
if [ -n "$CONFIG_FILE" ]; then
    echo "⚙️  Config file: $CONFIG_FILE"
fi
echo "======================================"

# Navigate to Terraform directory
cd "$TERRAFORM_DIR"

# Check if Terraform files exist
if ! ls *.tf 1> /dev/null 2>&1; then
    echo "⚠️  No Terraform files found in $TERRAFORM_DIR"
    echo "Skipping validation..."
    exit 0
fi

# Initialize Terraform (without backend)
echo ""
echo "⚙️  Initializing Terraform..."
terraform init -backend=false > /dev/null 2>&1 || {
    echo "❌ Terraform init failed"
    exit 1
}

# Generate plan
echo "📝 Generating Terraform plan..."
terraform plan -out=plan.tfplan > /dev/null 2>&1 || {
    echo "❌ Terraform plan failed"
    echo "This could be due to missing provider credentials or configuration issues."
    exit 1
}

# Convert plan to JSON
echo "🔄 Converting plan to JSON..."
terraform show -json plan.tfplan > plan.json || {
    echo "❌ Failed to convert plan to JSON"
    exit 1
}

# Validate tags
echo "✅ Validating tags..."
if [ -n "$CONFIG_FILE" ]; then
    python3 /scripts/validate_tags.py plan.json "$REQUIRED_TAGS" "$CONFIG_FILE"
else
    python3 /scripts/validate_tags.py plan.json "$REQUIRED_TAGS"
fi

exit_code=$?

echo "======================================"
if [ $exit_code -eq 0 ]; then
    echo "✅ All resources have required tags!"
else
    echo "❌ Tag validation failed!"
    echo "Please add missing tags to your Terraform resources."
fi
echo "======================================"

exit $exit_code
