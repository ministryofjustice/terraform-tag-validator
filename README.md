# Terraform Tag Enforcement

**Author:** Folarin Oyenuga

Docker-based GitHub Action that validates Terraform resources have mandatory MoJ tags before deployment.

## Problem

Infrastructure resources deployed without proper tags cause:
- Untrackable cloud costs
- Security audit failures  
- Ownership ambiguity
- Compliance violations

Detecting missing tags post-deployment is costly to remediate.

## Solution

Pre-deployment validation via GitHub Actions that:
- Blocks PRs with improperly tagged resources
- Validates tag values against MoJ standards
- Detects missing tags and empty values
- Works on both GitHub-hosted and self-hosted runners

## How It Works

1. Docker container bundles Terraform + Python validation script
2. Runs `terraform plan` on PR changes
3. Parses plan JSON for taggable resources
4. Validates against [MoJ tagging standards](https://ministryofjustice.github.io/technical-guidance/documentation/standards/documenting-infrastructure-owners.html)
5. Returns exit code 1 if violations found (blocks PR merge)

## Usage

### 1. Add Workflow to Your Repository

Create `.github/workflows/validate-terraform-tags.yml`:

```yaml
name: Terraform Tag Validation

on:
  pull_request:
    paths: ['**.tf']

jobs:
  validate-tags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: FolarinOyenuga/tag-enforcement-test@v1
        with:
          terraform_directory: ./terraform
          required_tags: |
            business-unit
            application
            owner
            is-production
            service-area
            environment-name
```

### 2. Enforce in Branch Protection

To **block PRs** with invalid tags:

1. Go to **Settings** → **Rules** → **Rulesets**
2. Create new **Branch ruleset**
3. Target: `main` branch
4. Enable: **Require status checks to pass**
5. Add required check: `validate-tags` (or your job name)

**This ensures PRs cannot merge until all resources have proper tags.**

## Required Tags (MoJ Standard)

| Tag | Description | Example | Validation |
|-----|-------------|---------|------------|
| `business-unit` | Business unit | `Platforms` | Must be: HMPPS, OPG, LAA, Central Digital, Technology Services, HMCTS, CICA, or Platforms |
| `application` | Service name | `Cloud Platform` | Any non-empty value |
| `owner` | Team and email | `WebOps: webops@justice.gov.uk` | Format: `Team Name: email@domain.com` |
| `is-production` | Production status | `true` | Must be: `true` or `false` |
| `service-area` | Team's service area | `Cloud Optimisation` | Any non-empty value |
| `environment-name` | Environment type | `production` | Must be: production, staging, test, or development |

## Local Testing

```bash
docker build -t tag-enforcement:local .

docker run --rm \
  -v $(pwd)/terraform:/workspace \
  -w /workspace \
  -e INPUT_TERRAFORM_DIRECTORY=. \
  -e INPUT_REQUIRED_TAGS="business-unit,application,owner,is-production,service-area" \
  tag-enforcement:local
```

## Why Docker?

- **Consistency:** Works identically on all runner types
- **Self-contained:** No environment setup required
- **Secure:** Isolated execution environment
- **Self-hosted friendly:** No assumptions about pre-installed tools
