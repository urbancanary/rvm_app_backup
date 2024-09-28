import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from bond_pricing.calculations import perform_regressions, create_rvm_grids
from bond_pricing.utils import create_spread_duration_plot, get_rating_from_string
from bond_pricing.auth import login, signup, change_password, delete_config, is_admin, load_config
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Set page to wide mode
st.set_page_config(layout="wide")

# Define the correct rating_num_map with proper rating strings
rating_num_map = {
    'Aaa': 1, 'Aa1': 2, 'Aa2': 3, 'Aa3': 4, 'A1': 5, 'A2': 6, 'A3': 7,
    'Baa1': 8, 'Baa2': 9, 'Baa3': 10, 'Ba1': 11, 'Ba2': 12, 'Ba3': 13,
    'B1': 14, 'B2': 15, 'B3': 16, 'Caa1': 17, 'Caa2': 18, 'Caa3': 19,
    'Ca': 20, 'C': 21
}

# Sort ratings by their numerical value
sorted_ratings = sorted(rating_num_map.items(), key=lambda x: x[1])

def load_data(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def process_data(df):
    if 'Rating' not in df.columns and 'Index Rating (String)' in df.columns:
        df['Rating'] = df['Index Rating (String)'].apply(get_rating_from_string)

    df['Rating'] = df['Rating'].apply(lambda x: x.capitalize() if isinstance(x, str) else x)
    df['rating_num'] = df['Rating'].map(rating_num_map)
    df['ln(duration)'] = np.log(df['OAD'])
    df['ln(spread)'] = np.log(df['OAS'])

    return df

def generate_rvm_grids(df):
    df_num = df[df['rating_num'].notnull()].copy()
    
    warf_map = dict(zip(df['Rating'], df['warf']))
    warf_map_sorted = pd.DataFrame({
        'rating': list(warf_map.keys()),
        'warf': list(warf_map.values()),
        'rating_num': [rating_num_map.get(rating, np.nan) for rating in warf_map.keys()]
    })
    warf_map_sorted = warf_map_sorted.dropna().sort_values('warf').reset_index(drop=True)

    df_num, coeffs_num, r2_num, df_warf, coeffs_warf, r2_warf = perform_regressions(df_num, warf_map_sorted)

    ratings_order = [rating for rating, _ in sorted_ratings]
    durations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]

    rvm_num, rvm_warf = create_rvm_grids(
        ratings_order, durations, coeffs_num, coeffs_warf, warf_map, rating_num_map
    )

    # Sort the RVM grids by the rating_num
    rvm_num = rvm_num.loc[[rating for rating, _ in sorted_ratings if rating in rvm_num.index]]
    rvm_warf = rvm_warf.loc[[rating for rating, _ in sorted_ratings if rating in rvm_warf.index]]

    return rvm_num, rvm_warf, r2_num, r2_warf, df_num

def login_page():
    st.title('Login')
    
    config_file = 'user_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        username = config.get('username', '')
        
        username = st.text_input('Username (email)', value=username)
        password = st.text_input('Password', type='password')
        
        if st.button('Login'):
            if login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error('Invalid username or password')
    else:
        username = st.text_input('Username (email)')
        password = st.text_input('Password', type='password')
        
        if st.button('Sign Up'):
            signup(username, password)
            st.success('Account created successfully. Please log in.')
        
        if st.button('Login'):
            if login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error('Invalid username or password')

def settings_page():
    st.title('Settings')
    old_password = st.text_input('Old Password', type='password')
    new_password = st.text_input('New Password', type='password')
    if st.button('Change Password'):
        if change_password(st.session_state['username'], old_password, new_password):
            st.success('Password changed successfully')
        else:
            st.error('Failed to change password')
    
    if st.button('Delete Account'):
        delete_config()
        st.session_state['logged_in'] = False
        st.rerun()

def rvm_calc_page(is_admin):
    st.title('Relative Value Model (RVM) Calculator')

    if 'bond_pricing.xlsx' in os.listdir():
        df = load_data('bond_pricing.xlsx')
        if df is not None:
            df = process_data(df)

            st.subheader('Risk-Value Matrix (RVM) Grids')

            required_columns = ['OAD', 'OAS', 'YTW', 'ISIN', 'warf', 'Rating', 'rating_num']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.warning(f"Unable to create RVM Grids. Missing columns: {', '.join(missing_columns)}")
            else:
                with st.spinner('Calculating RVM grids...'):
                    rvm_num, rvm_warf, r2_num, r2_warf, df_calc = generate_rvm_grids(df)
                
                st.success('RVM calculations completed!')

                # Store the calculated data
                df_calc.to_csv('bond_pricing_calcs.csv', index=False)

                st.subheader('Numerical Rating RVM Grid')
                # Display RVM grid to 0 decimal places
                st.dataframe(rvm_num.round(0).style.format("{:.0f}").apply(lambda _: ['background-color: #2f2f2f' if i % 2 == 0 else '' for i in range(len(_))], axis=0))

                if is_admin:
                    st.subheader('WARF-based RVM Grid')
                    # Display RVM grid to 0 decimal places
                    st.dataframe(rvm_warf.round(0).style.format("{:.0f}").apply(lambda _: ['background-color: #2f2f2f' if i % 2 == 0 else '' for i in range(len(_))], axis=0))

                    st.subheader('Model Performance')
                    st.write(f"Numerical Rating-based Model R-squared: {r2_num:.4f}")
                    st.write(f"WARF-based Model R-squared: {r2_warf:.4f}")
    else:
        st.info("Bond pricing data not available. Please contact an administrator.")

def analysis_page():
    st.title('Analysis')
    
    # Load the stored calculations
    if os.path.exists('bond_pricing_calcs.csv'):
        df = pd.read_csv('bond_pricing_calcs.csv')
    else:
        st.error("Calculated data not found. Please run the RVM Calculator first.")
        return

    # Apply filters
    st.subheader("Filters")
    with st.form("filters_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_notches = st.slider("Minimum Credit Notches", min_value=-10, max_value=10, value=-10)
            min_return_yield = st.slider("Minimum Return+Yield", min_value=0.0, max_value=20.0, value=0.0)
        
        with col2:
            min_yield = st.slider("Minimum Yield", min_value=0.0, max_value=20.0, value=0.0)
            countries = df['Country'].unique()
            selected_countries = st.multiselect("Select Countries", countries)
        
        with col3:
            st.write("Select Ratings")
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                st.write("Investment Grade")
                ig_ratings = [rating for rating, num in rating_num_map.items() if num <= 10]
                selected_ig_ratings = []
                for rating in ig_ratings:
                    if st.checkbox(rating, value=True, key=f"ig_rating_{rating}"):
                        selected_ig_ratings.append(rating)
            
            with col3_2:
                st.write("Sub-Investment Grade")
                sub_ig_ratings = [rating for rating, num in rating_num_map.items() if num > 10]
                selected_sub_ig_ratings = []
                for rating in sub_ig_ratings:
                    if st.checkbox(rating, value=False, key=f"sub_ig_rating_{rating}"):
                        selected_sub_ig_ratings.append(rating)
        
        selected_ratings = selected_ig_ratings + selected_sub_ig_ratings
        
        apply_filters = st.form_submit_button("Apply Filters")

    if apply_filters:
        # Apply filters
        df = df[df['Notches'] >= min_notches]
        df = df[df['Return_YTW'] >= min_return_yield]
        df = df[df['YTW'] >= min_yield]
        if selected_countries:
            df = df[df['Country'].isin(selected_countries)]
        if selected_ratings:
            df = df[df['Rating'].isin(selected_ratings)]

    # Option to upload a file
    uploaded_file = st.file_uploader("Upload your Excel file (optional)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        uploaded_df = load_data(uploaded_file)
        if uploaded_df is not None:
            use_full_set = st.checkbox("Include full dataset with uploaded bonds", value=False)
            if use_full_set:
                df = pd.concat([df, uploaded_df]).drop_duplicates(subset=['ISIN'], keep='first')
            else:
                df = uploaded_df

    # Round the spread to the nearest integer
    df['OAS'] = df['OAS'].round().astype(int)
    df['spread_predicted'] = df['spread_predicted'].round().astype(int)
    df['spread_predicted_num'] = df['spread_predicted_num'].round().astype(int)

    # Display filtered data using AgGrid
    st.subheader("Filtered Data")
    
    columns_to_display = [
        'ISIN', 'Description', 'Ccy', 'Price', 'YTW', 'OAD', 'OAS', 'Index Rating (String)',
        'Country', 'Rating Num', 'warf', 'ln(spread)_predicted_num', 'spread_predicted_num',
        'Return_num', 'Return_YTW_num', 'Rating Num Implied_num', 'Notches_num', 'Rating',
        'ln(spread)_predicted', 'spread_predicted', 'Return', 'Return_YTW', 'Rating Num Implied',
        'Notches', 'WARF Implied'
    ]
    
    df_display = df[columns_to_display]

    gb = GridOptionsBuilder.from_dataframe(df_display)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)  # Set initial page size to 20
    gb.configure_side_bar()
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
    
    # Add banded rows
    gb.configure_grid_options(rowClassRules={
        'banded-row': 'node.rowIndex % 2 === 0'
    })
    
    gridOptions = gb.build()

    grid_response = AgGrid(
        df_display,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        theme='streamlit', 
        enable_enterprise_modules=True,
        height=400,  # Set initial height
        width='100%',
        reload_data=True,
        custom_css={
            ".ag-row-even": {"background-color": "#2f2f2f !important"},
        }
    )

    # Add pagination controls
    st.write("Rows per page:")
    rows_per_page = st.selectbox("", [20, 50, 100, 500, 1000], index=0)
    
    if rows_per_page != gridOptions['paginationPageSize']:
        gridOptions['paginationPageSize'] = rows_per_page
        st.rerun()

    # Download options
    st.subheader("Download Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Full Dataset"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full Dataset as CSV",
                data=csv,
                file_name="full_dataset.csv",
                mime="text/csv",
            )
    
    with col2:
        if st.button("Download Filtered Data"):
            csv = grid_response['data'].to_csv(index=False)
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv",
            )

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_page()
    else:
        st.sidebar.title('Navigation')
        admin_status = is_admin()
        pages = ['RVM Calculator', 'Analysis', 'Settings']
        page = st.sidebar.selectbox('Go to', pages)

        # Add explanatory notes to the sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("Page Descriptions")
        
        if page == 'RVM Calculator':
            st.sidebar.markdown("""
            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
            <strong>RVM Calculator:</strong><br>
            • Calculates Risk-Value Matrix (RVM) grids<br>
            • Displays Numerical Rating and WARF-based grids<br>
            • Shows model performance metrics
            </div>
            """, unsafe_allow_html=True)
        elif page == 'Analysis':
            st.sidebar.markdown("""
            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
            <strong>Analysis:</strong><br>
            • View and filter bond data<br>
            • Apply filters to analyze bond information<br>
            • Upload custom bond data (optional)<br>
            • View and download filtered data<br>
            • Note: If a new file is uploaded, only these bonds will be filtered by default<br>
            • Use the checkbox to include the full dataset along with uploaded bonds
            </div>
            """, unsafe_allow_html=True)
        elif page == 'Settings':
            st.sidebar.markdown("""
            <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
            <strong>Settings:</strong><br>
            • Change your account password<br>
            • Delete your account
            </div>
            """, unsafe_allow_html=True)

        if st.sidebar.button('Logout'):
            st.session_state['logged_in'] = False
            st.rerun()

        if page == 'RVM Calculator':
            rvm_calc_page(admin_status)
        elif page == 'Analysis':
            analysis_page()
        elif page == 'Settings':
            settings_page()

if __name__ == "__main__":
    main()