from cli_project.urls.base import HFModelURL, classify_url
import requests


def fetch_repo_metadata(model: HFModelURL):
    """
    Fetch metadata for an HFModelURL instance via the Hugging Face API.
    Stores result in model.metadata and also returns it.
    """
    try:
        repo_id = model.repo_id   # uses HFModelURL property
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

        metadata = {
            "repo_id": repo_id,
            "downloads": data.get("downloads", "N/A"),
            "likes": data.get("likes", "N/A"),
            "last_modified": data.get("lastModified", "N/A"),
            "num_files": len(data.get("siblings", []))
        }

        model.metadata = metadata
        return metadata

    except Exception as e:
        print(f"Error fetching repo metadata: {e}")
        return None


# -------------------
# Example usage
# -------------------

if __name__ == "__main__":
    urls = [
        "https://huggingface.co/google-bert/bert-base-uncased",
        "https://huggingface.co/openai/whisper-tiny/tree/main"
    ]

    # classify URLs into UrlItem objects
    items = [classify_url(u) for u in urls]

    # filter models only
    models = [m for m in items if isinstance(m, HFModelURL)]

    for model in models:
        info = fetch_repo_metadata(model)
        if info:
            print(f"Metadata for {info['repo_id']}:")
            print(f"  Downloads: {info['downloads']}")
            print(f"  Likes: {info['likes']}")
            print(f"  Last Modified: {info['last_modified']}")
            print(f"  Number of files: {info['num_files']}")
            print("-" * 40)
        else:
            print(f"Could not fetch metadata for {model.url}")