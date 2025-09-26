from cli_project.adapters import huggingface
from cli_project.metrics.license import LicenseMetric
from cli_project.urls.base import HFModelURL
from cli_project.core.entities import HFModel

url = "https://huggingface.co/ds4sd/SmolDocling-256M-preview-mlx-bf16"

# Instead of classify_url, directly wrap into HFModel
hf_model_url = HFModelURL(url=url)
model = HFModel(model_url=hf_model_url, metrics={})

# Fetch metadata dict
metadata = huggingface.fetch_repo_metadata(model)
print("Metadata:", metadata)

# Run license metric
metric = LicenseMetric()
result = metric.compute(metadata)

print(result)
