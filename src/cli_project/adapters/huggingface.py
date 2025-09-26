from cli_project.urls.base import HFModelURL, classify_url
from cli_project.core.entities import HFModel
import requests # type: ignore
from typing import Any
from urllib.parse import urlparse
import re


# def fetch_repo_metadata(model: HFModelURL) -> dict[str, Any]:
#     """
#     Fetch metadata for an HFModelURL instance via the Hugging Face API.
#     Stores result in model.metadata and also returns it.
#     """
#     try:
#         repo_id = model.repo_id   # uses HFModelURL property
#     except ValueError as e:
#         print(e)
#         return None

#     api_url = f"https://huggingface.co/api/models/{repo_id}"

#     try:
#         response = requests.get(api_url)
#         if response.status_code != 200:
#             print(f"Failed to fetch data: HTTP {response.status_code}")
#             return None

#         data = response.json()

#         metadata = {
#             "repo_id": repo_id,
#             "downloads": data.get("downloads", "N/A"),
#             "likes": data.get("likes", "N/A"),
#             "last_modified": data.get("lastModified", "N/A"),
#             "num_files": len(data.get("siblings", []))
#         }

#         model.metadata = metadata
#         return metadata

#     except Exception as e:
#         print(f"Error fetching repo metadata: {e}")
#         return None
def extract_repo_id(url: str) -> str:
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


def fetch_repo_metadata(model: HFModel) -> dict[str, Any]:
    """
    Fetch metadata for an HFModelURL instance via the Hugging Face API.
    Stores result in model.metadata and also returns it.
    """
    try:
        model.repo_id = extract_repo_id(model.model_url.url)
    except ValueError as e:
        print(e)
        return {"": None}

    api_url = f"https://huggingface.co/api/models/{model.repo_id}"

    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            return {"": None}

        data = response.json()

        # -------------------------------
        # License: API first, README fallback
        # -------------------------------
        raw_license = data.get("license", "N/A")
        if raw_license == "N/A":
            readme_url = f"https://huggingface.co/{model.repo_id}/raw/main/README.md"
            try:
                resp = requests.get(readme_url, timeout=10)
                if resp.status_code == 200:
                    text = resp.text.lower()
                    for line in text.splitlines():
                        if line.lower().startswith("license:"):
                            raw_license = line.split(":", 1)[1].strip()
                            break
            except Exception as e:
                print(f"Error fetching README for license: {e}")

        metadata = {
            "repo_id": model.repo_id,
            "downloads": data.get("downloads", "N/A"),
            "likes": data.get("likes", "N/A"),
            "last_modified": data.get("lastModified", "N/A"),
            "num_files": len(data.get("siblings", [])),
            "license": raw_license,
        }

        model.metadata = metadata
        return metadata
    
    except Exception as e:
        print(f"Error fetching repo metadata: {e}")
        return {"": None}


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
    models = [m for m in items if isinstance(m, HFModel)]

    for model in models:
        info = fetch_repo_metadata(model)
        if info:
            print(f"Metadata for {info['repo_id']}:")
            print(f"  Downloads: {info['downloads']}")
            print(f"  Likes: {info['likes']}")
            print(f"  Last Modified: {info['last_modified']}")
            print(f"  Number of files: {info['num_files']}")
            print(f"  License: {info['license']}")
            print("-" * 40)
        else:
            print(f"Could not fetch metadata for {model.url}")
