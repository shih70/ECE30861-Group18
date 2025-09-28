"""
Metrics package initializer.

Each metric module exposes a top-level function:
    evaluate(repo: pathlib.Path) -> tuple[float | dict, int]
which returns (score, latency_ms).

Notes:
- Most metrics return a float score in [0,1].
- `size_score.evaluate` returns a float in [0,1] using cohort min–max
  (neutral 0.5 if bounds aren’t provided).
"""

#from .size_score import evaluate as eval_size
# from .license import evaluate as eval_license
# from .ramp_up_time import evaluate as eval_ramp_up_time
# from .dataset_and_code import evaluate as eval_dataset_and_code
#from .dataset_quality import evaluate as eval_dataset_quality
#from .code_quality import evaluate as eval_code_quality
#from .performance_claims import evaluate as eval_performance_claims
# from .bus_factor import evaluate as eval_bus_factor

__all__ = [
    #"eval_size",
    "eval_license",
    "eval_ramp_up_time",
    "eval_dataset_and_code",
    #"eval_dataset_quality",
    "eval_code_quality",
    "eval_performance_claims",
    "eval_bus_factor",
]
