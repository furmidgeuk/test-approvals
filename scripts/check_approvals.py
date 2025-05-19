import os
import requests
import sys

# === Configuration ===
MIN_SME_APPROVALS = 1   # <<< CHANGE THIS VALUE TO 1, 2, 3, ETC AS NEEDED

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

    # Track the latest approval for each user
    approvals = {}
    approval_events = []
    for review in reviews:
        if review['state'] == 'APPROVED':
            user = review['user']['login']
            approvals[user] = review['submitted_at']
            approval_events.append((review['submitted_at'], user))

    # Sort by approval time
    approval_events.sort()
    # SME approvals in order
    sme_approvals = []
    for _, user in approval_events:
        if user in sme_members and user not in sme_approvals:
            sme_approvals.append(user)
        if len(sme_approvals) == MIN_SME_APPROVALS:
            break

    if len(sme_approvals) < MIN_SME_APPROVALS:
        print(f"❌ Not enough SME approvals (need {MIN_SME_APPROVALS}).")
        sys.exit(1)
    else:
        # Find timestamp of last required SME approval
        last_sme_time = None
        approvals_counted = 0
        for time, user in approval_events:
            if user in sme_members and user in sme_approvals:
                approvals_counted += 1
                if approvals_counted == MIN_SME_APPROVALS:
                    last_sme_time = time
                    break

        # Any quality approval after this?
        for time, user in approval_events:
            if user in quality_members and time > last_sme_time:
                print(f"✅ Approval requirements met: {MIN_SME_APPROVALS} SME approval(s) and 1 Quality approval after SME(s).")
                sys.exit(0)
        print(f"❌ Need at least 1 Quality approval after {MIN_SME_APPROVALS} SME approval(s).")
        sys.exit(1)

if __name__ == "__main__":
    main()
