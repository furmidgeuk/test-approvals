import os
import requests
import sys

MIN_SME_APPROVALS = 2
MIN_QUALITY_APPROVALS = 1

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")
SME_TEAM = os.getenv("SME_TEAM")
QUALITY_TEAM = os.getenv("QUALITY_TEAM")
ORG = REPO.split('/')[0]

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_team_members(team):
    url = f"https://api.github.com/orgs/{ORG}/teams/{team}/members"
    members = []
    page = 1
    while True:
        resp = requests.get(url + f"?page={page}", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        members.extend([m['login'] for m in data])
        page += 1
    return set(members)

def get_reviews():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/reviews"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def main():
    sme_members = get_team_members(SME_TEAM)
    quality_members = get_team_members(QUALITY_TEAM)
    reviews = get_reviews()

    # Track latest review state per user
    latest_reviews = {}
    sme_approvals = set()
    quality_approval_after_sme = None

    for review in reviews:
        user = review['user']['login']
        state = review['state']

        if state == "APPROVED":
            latest_reviews[user] = "APPROVED"
        elif state in ("CHANGES_REQUESTED", "DISMISSED"):
            # Reset approval if user changes mind or is dismissed
            latest_reviews[user] = state

        # Count only if still considered approved later
        temp_sme_approvals = {u for u, s in latest_reviews.items() if s == "APPROVED" and u in sme_members}
        if user in quality_members and state == "APPROVED":
            if len(temp_sme_approvals) >= MIN_SME_APPROVALS and latest_reviews[user] == "APPROVED":
                quality_approval_after_sme = user

        sme_approvals = temp_sme_approvals

    if len(sme_approvals) >= MIN_SME_APPROVALS and quality_approval_after_sme:
        print(f"✅ {len(sme_approvals)} SME approval(s) and 1 Quality approval from '{quality_approval_after_sme}' after SME approvals. All requirements met.")
        sys.exit(0)
    else:
        print(f"❌ Not enough approvals: {len(sme_approvals)} SME (need {MIN_SME_APPROVALS}), Quality approval after SME: {'yes' if quality_approval_after_sme else 'no'}.")
        sys.exit(1)


if __name__ == "__main__":
    main()
