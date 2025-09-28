import requests
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


def fetch_bus_factor_metrics(repo_url, days=365):
    # Extract the owner and repository name from the GitHub URL
    repo_url = repo_url.rstrip('/')
    owner, repo = repo_url.split('/')[-2], repo_url.split('/')[-1]

    # GitHub API URL for commits
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    
    # Calculate the start date for the 'recent' commits
    since_date = (datetime.now() - timedelta(days=days)).isoformat()

    # Fetch commit data from the GitHub API (using pagination for large repos)
    committers = set()
    commit_count_by_committer = Counter()
    page = 1

    while True:
        params = {
            'since': since_date,  # Only fetch commits from the last 'days' days
            'page': page,         # Pagination for large repos
            'per_page': 100       # Max commits per page
        }
        response = requests.get(api_url, params=params)

        if response.status_code != 200:
            raise Exception(f"Error fetching commit data: {response.status_code}, {response.text}")

        commits = response.json()
        
        if not commits:
            break  # No more commits, end the loop
        
        # Parse each commit to gather committer information
        for commit in commits:
            committer = commit.get('commit', {}).get('author', {}).get('name')
            if committer:
                committers.add(committer)
                commit_count_by_committer[committer] += 1
        
        page += 1  # Move to the next page if there are more commits

    # Number of unique committers
    unique_committers_count = len(committers)

    # Calculate the bus factor score (normalize between 0 and 1)
    bus_factor_score = min(unique_committers_count / 10.0, 1.0)

    # Return the relevant variables
    return {
        'unique_committers_count': unique_committers_count,
        'bus_factor_score': bus_factor_score,
        'commit_count_by_committer': commit_count_by_committer,
    }


# NEW: raw-data-only method using the faster /contributors endpoint.
# No scoring here — metrics do the math.
def fetch_bus_factor_raw_contributors(repo_url: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch raw bus-factor-related data using GitHub's /contributors and /repos endpoints.

    Returns (no scoring!):
        {
            'unique_committers_count': int,
            'commit_count_by_committer': {login: contributions, ...},
            'last_commit_date': ISO8601 string or None,
            'method': 'contributors'
        }
    """
    repo_url = repo_url.rstrip('/')
    owner, repo = repo_url.split('/')[-2], repo_url.split('/')[-1]

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    # 1) Unique contributors + contributions count
    contributors_api = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    commit_count_by_committer: Dict[str, int] = {}
    page = 1
    while True:
        params = {"per_page": 100, "page": page}
        r = requests.get(contributors_api, params=params, headers=headers)
        if r.status_code != 200:
            raise Exception(f"Error fetching contributors: {r.status_code}, {r.text}")

        data = r.json()
        if not data:
            break

        for c in data:
            login = c.get("login")
            if login:
                # 'contributions' is total commits by this login on default branch
                commit_count_by_committer[login] = int(c.get("contributions", 0))

        page += 1

    unique_committers_count = len(commit_count_by_committer)

    # 2) Last commit/push date (for future recency adjustments, if needed)
    repo_api = f"https://api.github.com/repos/{owner}/{repo}"
    last_commit_date = None
    r2 = requests.get(repo_api, headers=headers)
    if r2.status_code == 200:
        last_commit_date = r2.json().get("pushed_at")

    return {
        "unique_committers_count": unique_committers_count,
        "commit_count_by_committer": commit_count_by_committer,
        "last_commit_date": last_commit_date,
        "recent_committers": unique_committers_count,
        "method": "contributors",
    }


# Example usage:
if __name__ == "__main__":
    repo_url = "https://github.com/shih70/ECE30861-Group18/"

    # Old method (still works; includes a score, but metrics should ignore it)
    result_old = fetch_bus_factor_metrics(repo_url)
    print("OLD (commits crawl):", result_old)

    # New method (raw only; metrics should use this)
    result_new = fetch_bus_factor_raw_contributors(repo_url)
    print("NEW (contributors raw):", result_new)
