# bond_pricing/data_processing.py
import pandas as pd

def map_isin(uploaded_df, extended_data_path='bond_pricing/extended_bond_data.csv'):
    """
    Merge uploaded data with extended data based on ISIN.

    :param uploaded_df: DataFrame uploaded by the user.
    :param extended_data_path: Path to the extended bond data CSV.
    :return: Merged DataFrame with extended information.
    """
    try:
        extended_data = pd.read_csv(extended_data_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Extended data file not found at {extended_data_path}")
    
    df_merged = uploaded_df.merge(extended_data, on='ISIN', how='left', indicator=True)
    
    # Identify and warn about ISINs that couldn't be mapped
    missing_isin = df_merged[df_merged['_merge'] == 'left_only']
    if not missing_isin.empty:
        print(f"Warning: {missing_isin.shape[0]} ISIN(s) could not be mapped to extended data.")
    
    # Drop the merge indicator column
    df_merged = df_merged.drop(columns=['_merge'])
    
    return df_merged
