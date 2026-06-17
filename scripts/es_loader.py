"""Load expression specificity (ES) matrices from config or default paths."""

from pathlib import Path

import pandas as pd
import yaml

import constants


def _load_specificity_paths(config_path: str = constants.CONFIG_PATH) -> dict[str, str]:
    path = Path(config_path)
    if not path.is_file():
        return {}
    with open(path) as f:
        config = yaml.safe_load(f)
    return {
        entry["id"]: entry["path"]
        for entry in config.get("SPECIFICITY_INPUT", [])
    }


def get_enrichr_organism(dataset_id: str) -> str:
    """Return Enrichr organism for a dataset id."""
    return "Mouse" if dataset_id in constants.MOUSE_DATASETS else "Human"


def load_es_matrix(
    dataset_id: str, config_path: str = constants.CONFIG_PATH
) -> pd.DataFrame:
    """
    Load an ES matrix for a dataset id.

    Resolves the file path from config SPECIFICITY_INPUT when available,
    otherwise falls back to esmu/{dataset_id}.mu.csv or .esmu.csv.
    """
    specificity_paths = _load_specificity_paths(config_path)
    candidates = []
    if dataset_id in specificity_paths:
        candidates.append(specificity_paths[dataset_id])
    candidates.extend(
        [
            f"{constants.ESMU_DIR}/{dataset_id}.mu.csv",
            f"{constants.ESMU_DIR}/{dataset_id}.esmu.csv",
        ]
    )
    seen: set[str] = set()
    for filepath in candidates:
        if filepath in seen:
            continue
        seen.add(filepath)
        if Path(filepath).is_file():
            return pd.read_csv(filepath, index_col=0)
    raise FileNotFoundError(
        f"ES matrix not found for dataset '{dataset_id}' "
        f"(tried: {', '.join(candidates)})"
    )
