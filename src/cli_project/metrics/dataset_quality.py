from typing import Any
import time
from cli_project.metrics.base import MetricResult


class DatasetQualityMetric:
    """
    Computes dataset quality heuristically based on Hugging Face model metadata.
    Factors include:
      - downloads
      - likes
      - number of files
      - model size (MB)
      - license presence
      - readme_text coverage
    """

    def name(self) -> str:
        return "dataset_quality"

    def compute(self, metadata: dict[str, Any]) -> MetricResult:
        t0 = time.time()

        downloads = metadata.get("downloads", 0) or 0
        likes = metadata.get("likes", 0) or 0
        num_files = metadata.get("num_files", 0)
        size_mb = metadata.get("size_mb", 0)
        license_str = metadata.get("license", "")
        readme_text = metadata.get("readme_text", "")

        # 1. Popularity Score (downloads scaled logarithmically)
        popularity = min(1.0, (downloads / 10000.0) ** 0.25) if downloads else 0.0

        # 2. Like Ratio Score
        like_ratio = likes / downloads if downloads else 0.0
        like_score = min(1.0, like_ratio * 5)  # 20% like rate → 1.0

        # 3. File Count Score (richness of repo)
        file_score = min(1.0, num_files / 10.0)  # 10+ files → full score

        # 4. Size Score (shouldn’t be empty or too large)
        if size_mb < 1:
            size_score = 0.0
        elif size_mb > 5000:
            size_score = 0.1
        else:
            size_score = min(1.0, size_mb / 100.0)  # 100MB → 1.0

        # 5. Readme Score
        readme_score = 1.0 if len(readme_text) > 300 else len(readme_text) / 300.0

        # 6. License Score
        license_score = 1.0 if license_str and license_str != "unknown" else 0.0

        # Weight each factor equally (or customize if needed)
        weights = {
            "popularity": 0.2,
            "like_score": 0.2,
            "file_score": 0.15,
            "size_score": 0.15,
            "readme_score": 0.2,
            "license_score": 0.1,
        }

        total = (
            weights["popularity"] * popularity +
            weights["like_score"] * like_score +
            weights["file_score"] * file_score +
            weights["size_score"] * size_score +
            weights["readme_score"] * readme_score +
            weights["license_score"] * license_score
        )

        details = {
            "popularity": round(popularity, 3),
            "like_score": round(like_score, 3),
            "file_score": round(file_score, 3),
            "size_score": round(size_score, 3),
            "readme_score": round(readme_score, 3),
            "license_score": round(license_score, 3),
        }

        latency = int((time.time() - t0) * 1000)

        return MetricResult(
            name=self.name(),
            value=round(total, 3),
            details=details,
            latency_ms=latency,
        )
