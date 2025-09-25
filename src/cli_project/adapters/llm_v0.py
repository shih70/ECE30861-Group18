import requests # type: ignore
from urllib.parse import urlparse
import re
from typing import Any

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

def fetch_repo_metadata(repo_url: str) -> dict[str, Any]:
    try:
        repo_id = extract_repo_id(repo_url)
    except ValueError as e:
        print(e)
        return {"": None}

    README_url = f"https://huggingface.co/{repo_id}/raw/main/README.md"

    try:
        response = requests.get(README_url)
        if response.status_code != 200:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            return {"": None}
        
        return response.text
    except Exception as e:
        print(f"Error fetching repo metadata: {e}")
        return {"": None}

def strip_hf_metadata(text: str) -> str:
    """
    Remove Hugging Face YAML metadata (--- ... ---) from README.md content.
    """
    return re.sub(r"^---[\s\S]*?---\n", "", text, count=1)

def query_readme(repo_url: str) -> None:
    api_key = ""
    readme_text = fetch_repo_metadata(repo_url)
    if not readme_text:
        raise ValueError("Failed to fetch README")
    
    print("Original README:\n")
    print(readme_text[:500])
    print(type(readme_text))

    clean_readme = strip_hf_metadata(readme_text)
    
    print("\n\nCleaned README:\n")
    print(clean_readme[:500])
    print(type(clean_readme))
    
    url = "https://genai.rcac.purdue.edu/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama4:latest",
        "messages": [
        {
            "role": "user",
            "content": clean_readme

        }
        ],
        # "stream": True
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        print(response.text)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    repo_url = "https://huggingface.co/openai/whisper-tiny/tree/main"
    print(repo_url)
    print(type(fetch_repo_metadata(repo_url)))
    query_readme(repo_url)