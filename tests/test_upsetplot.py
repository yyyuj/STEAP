import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.upsetplot import create_group


def test_create_group_matches_keyword():
    gwas_group_dict = {
        "Structural MRI": ["volume", "thickness"],
        "DTI Tracts": ["DTI"],
    }
    assert create_group("subcortical_volume_gwas", gwas_group_dict) == "Structural MRI"


def test_create_group_returns_other_when_no_match():
    gwas_group_dict = {"DTI Tracts": ["DTI"]}
    assert create_group("unrelated_phenotype", gwas_group_dict) == "Other"
