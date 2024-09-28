import plotly.express as px

def create_spread_duration_plot(df):
    """
    Create an interactive spread vs duration scatter plot using Plotly.

    :param df: DataFrame containing bond data.
    :return: Plotly Figure object.
    """
    # Filter spreads to 1000 or less
    df_filtered = df[df['OAS'] <= 1000]

    fig = px.scatter(
        df_filtered,
        x='OAD',  # Option-Adjusted Duration
        y='OAS',  # Option-Adjusted Spread
        color='Index Rating (String)' if 'Index Rating (String)' in df_filtered.columns else None,
        hover_data=['ISIN'],
        title='Option-Adjusted Spread vs Option-Adjusted Duration (Spread <= 1000)'
    )
    fig.update_layout(
        xaxis_title='Option-Adjusted Duration (OAD)',
        yaxis_title='Option-Adjusted Spread (OAS)',
        legend_title='Rating'
    )
    return fig

def get_rating_from_string(rating_string):
    """
    Extract the rating from the 'Index Rating (String)' column.
    
    :param rating_string: String containing the rating.
    :return: Extracted rating.
    """
    # Split the string and take the first part (assumed to be the rating)
    return rating_string.split()[0] if rating_string else None

def create_rating_num_map(ratings):
    """
    Create a mapping from rating to rating_num.
    
    :param ratings: List of unique ratings.
    :return: Dictionary mapping ratings to numbers.
    """
    sorted_ratings = sorted(ratings, key=lambda x: (x[0], len(x), x))  # Sort by first letter, then length, then full string
    return {rating: i+1 for i, rating in enumerate(sorted_ratings)}