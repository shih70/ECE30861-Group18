"""
DOCTYPE: Code quality metric using pylint.
This module defines CodeQualityMetric, which evaluates the maintainability and style
of a model repository using pylint. The pylint score (0–10) is normalized to [0,1].
"""

import subprocess
import time
from typing import Any
from cli_project.core.entities import HFModel
from cli_project.adapters.huggingface_inspect import clone_model_repo, clean_up_cache


class CodeQualityMetric:
    def __init__(self):
        self._cached_score = None
        self._cached_latency = None

    def name(self) -> str:
        return "code_quality"

    def evaluate(self, model: HFModel) -> float:
        repo_path = clone_model_repo(model.repo_id)
        if repo_path is None:
            print("[ERROR] Repo clone failed — skipping code quality score.")
            return 0.0

        try:
            result = subprocess.run(
                ["pylint", repo_path, "-rn", "--score", "y", "--exit-zero"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            print(f"RETURN CODE: {result.returncode}")

            # Parse final score from output (look for line with "Your code has been rated at X.XX/10")
            for line in output.splitlines():
                if "Your code has been rated at" in line:
                    try:
                        score_str = line.split("rated at")[1].split("/")[0].strip()
                        score = float(score_str)
                        return max(0.0, min(score / 10.0, 1.0))
                    except ValueError:
                        continue

        except Exception as e:
            print(f"[ERROR] Pylint execution failed: {e}")

        finally:
            clean_up_cache(repo_path)

        return 0.0
    
    def score(self, model: HFModel) -> float:
        if self._cached_score is None:
            self._cached_score = self.evaluate(model)
        return self._cached_score

    def score_latency(self, model: HFModel) -> dict[str, Any]:
        if self._cached_latency is not None:
            return {"latency_ms": self._cached_latency}
        
        start = time.perf_counter()
        self.score(model)
        end = time.perf_counter()
        return {"latency_ms": (end - start) * 1000}
