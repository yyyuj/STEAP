import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import constants
from scripts.es_loader import get_enrichr_organism, load_es_matrix


def test_load_es_matrix_from_config_path(tmp_path, monkeypatch):
    es_file = tmp_path / "custom.esmu.csv"
    es_file.write_text("gene,CellA\nENSG1,0.5\n")
    config_file = tmp_path / "config.yml"
    config_file.write_text(
        yaml.dump({"SPECIFICITY_INPUT": [{"id": "my_dataset", "path": str(es_file)}]})
    )
    monkeypatch.setattr(constants, "ESMU_DIR", str(tmp_path))

    df = load_es_matrix("my_dataset", config_path=str(config_file))

    assert list(df.columns) == ["CellA"]
    assert df.loc["ENSG1", "CellA"] == 0.5


def test_load_es_matrix_fallback_to_esmu_dir(tmp_path, monkeypatch):
    esmu_dir = tmp_path / "esmu"
    esmu_dir.mkdir()
    es_file = esmu_dir / "mousebrain.esmu.csv"
    es_file.write_text("gene,Neuron\nENSG1,0.9\n")
    monkeypatch.setattr(constants, "ESMU_DIR", str(esmu_dir))

    df = load_es_matrix("mousebrain", config_path=str(tmp_path / "missing.yml"))

    assert "Neuron" in df.columns


def test_load_es_matrix_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(constants, "ESMU_DIR", str(tmp_path))

    with pytest.raises(FileNotFoundError, match="ES matrix not found"):
        load_es_matrix("nonexistent_dataset", config_path=str(tmp_path / "missing.yml"))


def test_get_enrichr_organism():
    assert get_enrichr_organism("mousebrain") == "Mouse"
    assert get_enrichr_organism("Allen_human_LGN") == "Human"
