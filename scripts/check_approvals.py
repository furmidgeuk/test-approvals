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

    # Keep only latest review state per user
    latest_reviews = {}
    for review in reviews:
        user = review['user']['login']
        latest_reviews[user] = review['state']

    sme_approvals = set()
    quality_approvals = set()
    for user, state in latest_reviews.items():
        if state == "APPROVED":
            if user in sme_members:
                sme_approvals.add(user)
            if user in quality_members:
                quality_approvals.add(user)

    if len(sme_approvals) >= MIN_SME_APPROVALS and len(quality_approvals) >= MIN_QUALITY_APPROVALS:
        print(f"✅ {len(sme_approvals)} SME approval(s) and {len(quality_approvals)} Quality approval(s). All requirements met.")
        sys.exit(0)
    else:
        print(f"❌ Not enough approvals: {len(sme_approvals)} SME (need {MIN_SME_APPROVALS}), {len(quality_approvals)} Quality (need {MIN_QUALITY_APPROVALS}).")
        sys.exit(1)

if __name__ == "__main__":
    main()
