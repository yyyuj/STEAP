import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.stats_utils import bonferroni_correct, bonferroni_threshold


def test_bonferroni_correct_caps_at_one():
    result = bonferroni_correct([0.5, 0.6], n_tests=3)
    np.testing.assert_array_equal(result, [1.0, 1.0])


def test_bonferroni_threshold():
    assert bonferroni_threshold(0.05, 10) == pytest.approx(0.005)
