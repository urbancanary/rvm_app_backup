# bond_pricing/data_processing.py
import pandas as pd
import os

def map_isin(uploaded_df, extended_data_path='bond_pricing/extended_bond_data.csv'):
    """
    Merge uploaded data with extended data based on ISIN if the extended data file exists.

    :param uploaded_df: DataFrame uploaded by the user.
    :param extended_data_path: Path to the extended bond data CSV.
    :return: Merged DataFrame with extended information if available, otherwise the original DataFrame.
    """
    if os.path.exists(extended_data_path):
        try:
            extended_data = pd.read_csv(extended_data_path)
            df_merged = uploaded_df.merge(extended_data, on='ISIN', how='left', indicator=True)
            
            # Identify and warn about ISINs that couldn't be mapped
            missing_isin = df_merged[df_merged['_merge'] == 'left_only']
            if not missing_isin.empty:
                print(f"Warning: {missing_isin.shape[0]} ISIN(s) could not be mapped to extended data.")
            
            # Drop the merge indicator column
            df_merged = df_merged.drop(columns=['_merge'])
            
            return df_merged
        except Exception as e:
            print(f"Error reading extended data file: {e}")
            print("Proceeding with original data.")
            return uploaded_df
    else:
        print(f"Extended data file not found at {extended_data_path}")
        print("Proceeding with original data.")
        return uploaded_df
