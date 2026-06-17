import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.convert_output_to_dataframe import find_csv_file, pvalue_correction


def test_find_csv_file_parses_cellect_directory(tmp_path):
    prioritization = tmp_path / "CELLECT-PGC_test" / "CELLECT-MAGMA" / "out" / "prioritization.csv"
    prioritization.parent.mkdir(parents=True)
    prioritization.write_text("gwas,specificity_id,annotation,beta,beta_se,pvalue\n")

    result = find_csv_file(str(tmp_path))

    assert "PGC_test" in result
    assert "MAGMA" in result["PGC_test"]
    assert result["PGC_test"]["MAGMA"] == str(prioritization)


def test_pvalue_correction_aligns_annotations():
    dataframe = pd.DataFrame(
        {
            "gwas": ["g1", "g1", "g1", "g1"],
            "specificity_id": ["ds1", "ds1", "ds1", "ds1"],
            "annotation": ["A", "B", "A", "B"],
            "method": ["MAGMA", "MAGMA", "LDSC", "LDSC"],
            "pvalue": [0.01, 0.02, 0.03, 0.04],
            "beta": [1.0, 1.0, 1.0, 1.0],
        }
    )
    corrected = pvalue_correction(dataframe, method="bonferroni")

    assert "pvalue_bonferroni" in corrected.columns
    assert len(corrected) == len(dataframe)
    merged = corrected.merge(
        dataframe,
        on=["gwas", "specificity_id", "annotation", "method", "pvalue"],
    )
    assert len(merged) == len(dataframe)
