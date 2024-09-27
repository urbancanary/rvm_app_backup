# bond_pricing/utils.py
import pandas as pd
import plotly.express as px

def filter_bonds(df, filters):
    """
    Apply filters to the bond DataFrame.

    :param df: DataFrame containing bond data.
    :param filters: Dict containing filter criteria.
    :return: Filtered DataFrame.
    """
    for key, value in filters.items():
        if key in ['Yield', 'Spread']:
            lower, upper = value
            df = df[(df[key] >= lower) & (df[key] <= upper)]
        elif key in ['NFA', 'ESG']:
            if value:
                df = df[df[key] == True]
        else:
            if value:
                df = df[df[key].isin(value)]
    return df

def create_yield_plot(df):
    """
    Create an interactive yield vs spread scatter plot using Plotly.

    :param df: DataFrame containing bond data.
    :return: Plotly Figure object.
    """
    fig = px.scatter(
        df,
        x='Yield',
        y='Spread',
        color='Country',
        hover_data=['ISIN', 'Rating', 'CreditNotch'],
        title='Yield vs Spread by Country'
    )
    fig.update_layout(legend_title_text='Country')
    return fig
