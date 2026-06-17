import itertools

import pandas as pd
from scipy.stats import spearmanr

import constants
from scripts.es_loader import load_es_matrix
from scripts.stats_utils import bonferroni_correct


def calculate_spearmanr(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Uses spearman correlation to calculate the ES gene correlation.
    """
    corr_list = []
    for x, y in itertools.combinations(dataframe.columns, 2):
        corr_frame = dataframe.loc[:, [x, y]].fillna(0).copy()
        # ES value should be > 0 in both celltypes
        corr_frame = corr_frame[(corr_frame > 0).all(1)]
        if corr_frame.empty:
            continue
        corr, pval = spearmanr(
            corr_frame.iloc[:, 0].values, corr_frame.iloc[:, 1].values
        )
        corr_list.append([x, y, corr, pval])
    df = pd.DataFrame(corr_list, columns=["celltypex", "celltypey", "corr", "pval"])
    return df


def correct_pval_correlation(corr_df: pd.DataFrame) -> pd.DataFrame:
    """
    Corrects the pvalues from the ES gene correlation using Bonferroni.
    """
    correct_df = corr_df.copy()
    n_test = correct_df.shape[0]
    correct_df["pval_bonferroni"] = bonferroni_correct(correct_df["pval"], n_test)
    return correct_df


def calculate_es_corr(datasets: list[str]) -> pd.DataFrame:
    """
    Calculates the expression specificity (ES) gene correlation between
    all celltypes in the input datasets.

    Parameters
    ----------
    datasets : list[str]
        List of the names of datasets. These names shouls correspong to
        the .csv file in the esmu directory.

    Returns
    -------
    es_corr_df : pd.DataFrame
        Pandas dataframe containing the ES gene correlation and pvalue
        between the gwas phenotypes.
    """
    df_list = []
    for dataset in datasets:
        df_esmu = load_es_matrix(dataset)
        df_esmu.columns = [f"{dataset}, {ct}" for ct in df_esmu.columns]
        df_list.append(df_esmu)

    merged_es_df = pd.concat(df_list, join="outer", axis=1)
    merged_es_df.sort_index(axis=1, inplace=True)
    es_corr_df = calculate_spearmanr(merged_es_df.fillna(0))
    es_corr_df = correct_pval_correlation(es_corr_df)
    return es_corr_df


if __name__ == "__main__":
    df_all = pd.read_hdf(constants.ENRICHMENT_H5, "df_all")
    datasets = df_all["specificity_id"].unique().tolist()
    es_corr_df = calculate_es_corr(datasets)
    es_corr_df.to_hdf(constants.CORRELATION_H5, key="es_corr_df")
