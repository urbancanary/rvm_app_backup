import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def warf_to_rating_num(warf_value, warf_map_sorted):
    if warf_value <= warf_map_sorted['warf'].min():
        return warf_map_sorted.iloc[0]['rating_num']
    elif warf_value >= warf_map_sorted['warf'].max():
        return warf_map_sorted.iloc[-1]['rating_num']
    else:
        lower = warf_map_sorted[warf_map_sorted['warf'] <= warf_value].iloc[-1]
        upper = warf_map_sorted[warf_map_sorted['warf'] > warf_value].iloc[0]
        fraction = (warf_value - lower['warf']) / (upper['warf'] - lower['warf'])
        return lower['rating_num'] + fraction * (upper['rating_num'] - lower['rating_num'])

def perform_regression(df, model_type, warf_map_sorted=None):
    if model_type == 'Numerical':
        X = df[['ln(duration)', 'rating_num']]
        y = df['ln(spread)']
    elif model_type == 'WARF':
        X = df[['ln(duration)', 'warf']]
        y = df['ln(spread)']
    else:
        raise ValueError("Invalid model_type. Choose 'Numerical' or 'WARF'.")
    
    model = LinearRegression()
    model.fit(X, y)
    
    intercept = model.intercept_
    coeff_ln_duration, coeff_rating = model.coef_
    
    if model_type == 'Numerical':
        df['ln(spread)_predicted'] = intercept + coeff_ln_duration * df['ln(duration)'] + coeff_rating * df['rating_num']
    else:
        df['ln(spread)_predicted'] = intercept + coeff_ln_duration * df['ln(duration)'] + coeff_rating * df['warf']
    
    df['spread_predicted'] = np.exp(df['ln(spread)_predicted'])
    df['Return'] = (df['OAS'] - df['spread_predicted']) * df['OAD']
    df['Return_YTW'] = df['Return'] + df['YTW']
    
    if model_type == 'Numerical':
        df['Rating Num Implied'] = (df['ln(spread)'] - intercept - coeff_ln_duration * df['ln(duration)']) / coeff_rating
        df['Notches'] = df['rating_num'] - df['Rating Num Implied']
    else:
        df['WARF Implied'] = (df['ln(spread)'] - intercept - coeff_ln_duration * df['ln(duration)']) / coeff_rating
        df['Rating Num Implied'] = df['WARF Implied'].apply(lambda x: warf_to_rating_num(x, warf_map_sorted))
        df['Notches'] = df['rating_num'] - df['Rating Num Implied']
    
    coeffs = {
        'intercept': intercept,
        'coeff_ln_duration': coeff_ln_duration,
        'coeff_rating': coeff_rating
    }
    
    r2 = model.score(X, y)
    
    return df, coeffs, r2

def perform_regressions(df_num, warf_map_sorted):
    df_num, coeffs_num, r2_num = perform_regression(df_num, 'Numerical')
    df_warf, coeffs_warf, r2_warf = perform_regression(df_num, 'WARF', warf_map_sorted)
    return df_num, coeffs_num, r2_num, df_warf, coeffs_warf, r2_warf

def create_rvm_grid(ratings, durations, model_type, coeffs, warf_map, rating_num_map=None):
    grid_data = []
    for rating in ratings:
        if model_type == 'Numerical':
            if rating_num_map:
                rating_num = rating_num_map.get(rating, np.nan)
            else:
                rating_num = warf_to_rating_num(warf_map[rating], pd.DataFrame(warf_map.items(), columns=['rating', 'warf']))
            if pd.isna(rating_num):
                continue
            for duration in durations:
                ln_duration = np.log(duration)
                predicted_ln_spread = coeffs['intercept'] + coeffs['coeff_ln_duration'] * ln_duration + coeffs['coeff_rating'] * rating_num
                spread_predicted = np.exp(predicted_ln_spread)
                grid_data.append({'Rating': rating, 'Duration': duration, 'Predicted Spread': spread_predicted})
        elif model_type == 'WARF':
            warf = warf_map.get(rating, np.nan)
            if pd.isna(warf):
                continue
            for duration in durations:
                ln_duration = np.log(duration)
                predicted_ln_spread = coeffs['intercept'] + coeffs['coeff_ln_duration'] * ln_duration + coeffs['coeff_rating'] * warf
                spread_predicted = np.exp(predicted_ln_spread)
                grid_data.append({'Rating': rating, 'Duration': duration, 'Predicted Spread': spread_predicted})
    
    rvm_df = pd.DataFrame(grid_data)
    rvm_pivot = rvm_df.pivot(index='Rating', columns='Duration', values='Predicted Spread')
    return rvm_pivot

def create_rvm_grids(ratings_order, durations, coeffs_num, coeffs_warf, warf_map, rating_num_map=None):
    rvm_num = create_rvm_grid(ratings_order, durations, 'Numerical', coeffs_num, warf_map, rating_num_map)
    rvm_warf = create_rvm_grid(ratings_order, durations, 'WARF', coeffs_warf, warf_map, rating_num_map)
    return rvm_num, rvm_warf
