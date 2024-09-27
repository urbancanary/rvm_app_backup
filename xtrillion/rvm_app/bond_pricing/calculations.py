# bond_pricing/calculations.py
import pandas as pd

def calculate_bond_grid(input_data):
    """
    Perform RVM/Bond pricing calculations.

    :param input_data: Dict or DataFrame containing input parameters.
    :return: DataFrame with calculated bond grid.
    """
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = pd.DataFrame(input_data)
    
    # TODO: Replace the placeholder logic with your actual RVM/Bond pricing calculations
    # Example Placeholder Calculation:
    df['Calculated Yield'] = df['Yield'] + df['Spread']
    
    return df