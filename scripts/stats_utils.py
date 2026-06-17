"""Shared statistical utilities for STEAP post-processing."""

from typing import Union

import numpy as np


def bonferroni_correct(
    pvals: Union[np.ndarray, list, "pd.Series"], n_tests: int | None = None
) -> np.ndarray:
    """
    Apply Bonferroni correction to p-values.

    Parameters
    ----------
    pvals : array-like
        Raw p-values.
    n_tests : int, optional
        Number of tests. Defaults to len(pvals).
    """
    pvals = np.asarray(pvals, dtype=float)
    if n_tests is None:
        n_tests = len(pvals)
    corrected = pvals * n_tests
    return np.minimum(corrected, 1.0)


def bonferroni_threshold(alpha: float, n_tests: int) -> float:
    """Return the Bonferroni-corrected significance threshold."""
    return alpha / n_tests
