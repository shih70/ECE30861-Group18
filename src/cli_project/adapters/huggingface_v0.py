import requests
from urllib.parse import urlparse

def extract_repo_id(url):
    """
    Extract the repo ID (like 'google-bert/bert-base-uncased') from the HF URL.
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) >= 2:
        # The first two parts form the repo id: user_or_org/model_name
        repo_id = f"{path_parts[0]}/{path_parts[1]}"
        return repo_id
    else:
        raise ValueError("URL does not contain a valid repo identifier")

def fetch_repo_metadata(repo_url):
    try:
        repo_id = extract_repo_id(repo_url)
    except ValueError as e:
        print(e)
        return None

    api_url = f"https://huggingface.co/api/models/{repo_id}"

    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            return None
        
        data = response.json()

        downloads = data.get('downloads', 'N/A')
        likes = data.get('likes', 'N/A')
        last_modified = data.get('lastModified', 'N/A')
        siblings = data.get('siblings', [])
        num_files = len(siblings)

        return {
            "repo_id": repo_id,
            "downloads": downloads,
            "likes": likes,
            "last_modified": last_modified,
            "num_files": num_files
        }
    except Exception as e:
        print(f"Error fetching repo metadata: {e}")
        return None

# Example usage:

urls = [
    "https://huggingface.co/google-bert/bert-base-uncased",
    "https://huggingface.co/openai/whisper-tiny/tree/main"
]

for url in urls:
    info = fetch_repo_metadata(url)
    if info:
        print(f"Metadata for {info['repo_id']}:")
        print(f"  Downloads: {info['downloads']}")
        print(f"  Likes: {info['likes']}")
        print(f"  Last Modified: {info['last_modified']}")
        print(f"  Number of files: {info['num_files']}")
        print("-" * 40)
    else:
        print(f"Could not fetch metadata for {url}")