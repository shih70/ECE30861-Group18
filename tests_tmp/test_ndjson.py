import json
import pytest
from _pytest.capture import CaptureFixture
from cli_project.io.ndjson import NDJSONEncoder
from cli_project.core.entities import HFModel
from cli_project.metrics.base import MetricResult
from cli_project.urls.base import HFModelURL

def make_model_with_results(name: str="bert-base-uncased") -> HFModel:
    url = HFModelURL(f"https://huggingface.co/{name}")
    m = HFModel(model_url=url)
    m.add_results([
        MetricResult("license", 1.0, {}, 10),
        MetricResult("bus_factor", 0.9, {}, 20),
    ])
    return m

def test_encode_single_model_returns_json() -> None:
    model = make_model_with_results()
    line = NDJSONEncoder.encode(model)
    data = json.loads(line)
    assert data["name"] == "bert-base-uncased"
    assert data["license"] == 1.0
    assert data["license_latency"] == 10

def test_encode_computes_net_score() -> None:
    model = make_model_with_results()
    line = NDJSONEncoder.encode(model)
    data = json.loads(line)
    assert "net_score" in data
    assert 0 <= data["net_score"] <= 1

def test_encode_all_multiple_models() -> None:
    model1 = make_model_with_results("bert-base-uncased")
    model2 = make_model_with_results("whisper-tiny")
    ndjson_str = NDJSONEncoder.encode_all([model1, model2])
    lines = ndjson_str.splitlines()
    assert len(lines) == 2
    assert "bert-base-uncased" in lines[0]
    assert "whisper-tiny" in lines[1]

def test_print_records_prints(capsys: CaptureFixture[str]) -> None:
    model = make_model_with_results()
    NDJSONEncoder.print_records([model])
    captured = capsys.readouterr()
    assert "bert-base-uncased" in captured.out

def test_encode_with_no_results() -> None:
    url = HFModelURL("https://huggingface.co/empty-model")
    model = HFModel(model_url=url)
    line = NDJSONEncoder.encode(model)
    data = json.loads(line)
    assert data["name"] == "empty-model"
    # net_score should not exist since no results
    assert "net_score" not in data
