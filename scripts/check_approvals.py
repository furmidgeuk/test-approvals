import os
import requests
import sys

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")
SME_TEAM = os.getenv("SME_TEAM")            # e.g. 'sme-team'
QUALITY_TEAM = os.getenv("QUALITY_TEAM")    # e.g. 'quality-team'
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
    # Count SME approvals
    sme_approvals = [user for _, user in approval_events if user in sme_members]
    # Track first 2 SME approvals
    first_2_sme = []
    for user in sme_approvals:
        if user not in first_2_sme:
            first_2_sme.append(user)
        if len(first_2_sme) == 2:
            break

    # Quality approval(s) that come after the first 2 SME approvals
    if len(first_2_sme) < 2:
        print("❌ Not enough SME approvals (need 2).")
        sys.exit(1)
    else:
        # Find timestamp of second SME approval
        second_sme_time = None
        for time, user in approval_events:
            if user == first_2_sme[1]:
                second_sme_time = time
                break

        # Any quality approval after this?
        for time, user in approval_events:
            if user in quality_members and time > second_sme_time:
                print("✅ Approval requirements met: 2 SME approvals and 1 Quality approval after SME.")
                sys.exit(0)
        print("❌ Need at least 1 Quality approval after 2 SME approvals.")
        sys.exit(1)

if __name__ == "__main__":
    main()
