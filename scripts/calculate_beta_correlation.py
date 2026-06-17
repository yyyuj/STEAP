import itertools

import pandas as pd
from scipy.stats import pearsonr

import constants


def calculate_pearson(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Uses pearson correlation to calculate the cell type correlation.
    """
    corr_list = []
    for x, y in itertools.combinations(dataframe.columns, 2):
        corr, pval = pearsonr(dataframe.loc[:, x].values, dataframe.loc[:, y].values)
        corr_list.append([x, y, corr, pval])
    df = pd.DataFrame(corr_list, columns=["gwasx", "gwasy", "corr", "pval"])
    return df


def get_pthres(corr_df: pd.DataFrame) -> float:
    """
    Returns the lowest pvalue from the negative correlations in the
    input dataframe.
    """
    negative = corr_df[corr_df["corr"] < 0]["pval"]
    if negative.empty:
        return float("nan")
    return negative.min()


def calculate_celltype_corr(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the celltype correlation between all gwas phenotypes
    in the input dataframe.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The input pandas dataframe contains information about the phenotype,
        celltypes, method and enrichment (beta) values with corresponding
        p-values.

    Returns
    -------
    corr_df : pd.DataFrame
        Pandas dataframe containing the correlation and pvalue between the
        gwas phenotypes.
    """
    df_list = []
    for m in constants.METHODS:
        df_method = dataframe[(dataframe.method == m)]
        df_method_pivot = df_method.pivot_table(
            index="annotation", columns="gwas", values="beta"
        )
        # drop gwas if not complete
        df_method_pivot.dropna(axis="columns", inplace=True)
        corr_df = calculate_pearson(df_method_pivot)
        corr_df["method"] = m
        df_list.append(corr_df)
    return pd.concat(df_list)


if __name__ == "__main__":
    print("Calculating Cell Type Correlation...")
    df_all = pd.read_hdf(constants.ENRICHMENT_H5, "df_all")
    corr_df = calculate_celltype_corr(df_all)
    corr_df.to_hdf(constants.CORRELATION_H5, key="corr_df")
