# SME and Quality Approval Check Workflow

## What does this do?

This repository enforces a **multi-team approval process** for Pull Requests (PRs):

- **At least 2 approvals from SME team members**
- **At least 1 approval from Quality team members**

Merges into `main` are only allowed if both conditions are met, in addition to your branch protection rule that requires a total of 3 approvals and CODEOWNERS review.

## How it works

- A GitHub Actions workflow runs automatically on every PR review event.
- The workflow uses a Python script (`scripts/check_approvals.py`) to check the latest review state for each reviewer.
- The script counts approvals from each team (using team slugs).
- If there are at least 2 SME and 1 Quality approvals, the check passes. Otherwise, it fails, blocking the merge.

## Setup

### 1. **Team Slugs**

Edit `.github/workflows/approval-check.yml` and update these lines with your correct GitHub team slugs:

```yaml
SME_TEAM: 'sme-team'           # Change to your SME team slug
QUALITY_TEAM: 'quality-team'   # Change to your Quality team slug
