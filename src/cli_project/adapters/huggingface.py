from cli_project.urls.base import HFModelURL  # , classify_url
from cli_project.core.entities import HFModel
import requests  # type: ignore
from typing import Any
from urllib.parse import urlparse
import re


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
        # Also capture README text for performance/dataset/code metrics
        # -------------------------------
        raw_license = data.get("license", "N/A")
        readme_text = ""   # 👈 NEW FIELD

        readme_url = f"https://huggingface.co/{model.repo_id}/raw/main/README.md"
        try:
            resp = requests.get(readme_url, timeout=10)
            if resp.status_code == 200:
                text = resp.text
                readme_text = text              # 👈 keep full README
                if raw_license == "N/A":
                    for line in text.lower().splitlines():
                        if line.startswith("license:"):
                            raw_license = line.split(":", 1)[1].strip()
                            break
        except Exception as e:
            print(f"Error fetching README: {e}")

        # -------------------------------
        # Datasets field (explicit or fallback to [])
        # -------------------------------
        try:
            dataset_list = data.get("datasets", [])
            if not isinstance(dataset_list, list):
                dataset_list = [dataset_list] if dataset_list else []
        except Exception as e:
            print(f"[WARN] Failed to extract dataset metadata: {e}")
            dataset_list = []

        # -------------------------------
        # Files field (from siblings)
        # -------------------------------
        file_list = []
        try:
            siblings = data.get("siblings", [])
            if isinstance(siblings, list):
                file_list = [s.get("rfilename") for s in siblings if isinstance(s, dict) and "rfilename" in s]
        except Exception as e:
            print(f"[WARN] Failed to extract file metadata: {e}")
            file_list = []

        metadata = {
            "repo_url": model.model_url.url,
            "repo_id": model.repo_id,
            "downloads": data.get("downloads", "N/A"),
            "likes": data.get("likes", "N/A"),
            "last_modified": data.get("lastModified", "N/A"),
            "num_files": len(data.get("siblings", [])),
            "license": raw_license,
            "size_mb": data.get("usedStorage", 0) / (1024 * 1024),
            "readme_text": readme_text,   # 👈 README needed for metrics
            "datasets": dataset_list,     # 👈 NEW
            "files": file_list,           # 👈 NEW
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

    # for manual testing
    from cli_project.core.entities import HFModel
    m = HFModel(model_url=HFModelURL(urls[0]), metrics=[])
    info = fetch_repo_metadata(m)
    print(info)
