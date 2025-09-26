import requests
from collections import Counter
from datetime import datetime, timedelta

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

# Example usage:
repo_url = "https://github.com/shih70/ECE30861-Group18/"
result = fetch_bus_factor_metrics(repo_url)
print(f"Unique Committers Count: {result['unique_committers_count']}")
print(f"Bus Factor Score: {result['bus_factor_score']}")
print(f"Commit Count by Committer: {result['commit_count_by_committer']}")