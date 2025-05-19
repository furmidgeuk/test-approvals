# SME and Quality Approval Workflow

This repository enforces that:

- At least **2 approvals from SME team members** are given before...
- At least **1 approval from Quality team member**, which must be after the SMEs.

Merges to `main` are only allowed when these rules are met.

## Setup

- Update the `SME_TEAM` and `QUALITY_TEAM` env vars in `.github/workflows/approval-check.yml` to your real team slugs.
- Make sure the workflow status check (`check-approvals`) is required in your branch protection rules.

## Team Slugs

You can find team slugs in your organization at  
`https://github.com/orgs/<org-name>/teams`


testing1
