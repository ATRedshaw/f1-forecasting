import pandas as pd

def check_all_ran_values(practice_statistics):
    """
    For all _ran values, update any NaNs to False
    
    Args:
        practice_statistics (pd.DataFrame): The practice statistics dataframe

    Returns:
        pd.DataFrame: The practice statistics dataframe with all _ran values updated to False
    """
    for col in practice_statistics.columns:
        if 'ran_' in col:
            practice_statistics[col] = practice_statistics[col].fillna(False)
    return practice_statistics

def remove_nan_target_col(practice_statistics, target_col='quali_position'):
    """
    For all values in the target_col, remove the rows where the value is NaN
    
    Args:
        practice_statistics (pd.DataFrame): The practice statistics dataframe
        target_col (str): The target column to remove NaNs from

    Returns:
        pd.DataFrame: The practice statistics dataframe with all rows where the target_col is NaN removed
    """
    practice_statistics = practice_statistics[practice_statistics[target_col].notna()]

    # Move the target_col to the last column
    practice_statistics = practice_statistics[[col for col in practice_statistics.columns if col != target_col] + [target_col]]

    return practice_statistics

def fill_nans_with_zero(practice_statistics):
    """
    Fill any remaining NaNs with 0, these are columns related to tyre compounds that were not run in that overall sessiom,
    but exist in some session in the dataset.
    
    Args:
        practice_statistics (pd.DataFrame): The practice statistics dataframe

    Returns:
        pd.DataFrame: The practice statistics dataframe with all NaNs filled with 0
    """
    practice_statistics = practice_statistics.fillna(0)
    practice_statistics = practice_statistics.reset_index(drop=True)
    return practice_statistics
