# app.py

import streamlit as st
import pandas as pd
from bond_pricing.calculations import perform_regressions, create_rvm_grids
from bond_pricing.data_processing import load_data, filter_data
from bond_pricing.utils import create_scatter_plot, create_bar_chart, create_rvm_heatmap
from andy_rvm import warf_to_rating_num
import io

def main():
    st.title('Bond Analysis Dashboard')

    # File uploader
    st.sidebar.header('Upload Bond Data')
    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Load data
        df = load_data(uploaded_file)

        # Sidebar for filters
        st.sidebar.header('Filters')
        excluded_columns = st.sidebar.multiselect(
            'Select columns to exclude',
            options=df.columns,
            default=['ln(duration)', 'ln(spread)', 'ln(spread)_predicted_num', 'warf']
        )

        country_list = st.sidebar.multiselect(
            'Select countries',
            options=df['Country'].unique(),
            default=df['Country'].unique()
        )

        min_notches = st.sidebar.slider('Minimum absolute notches', 0.0, 10.0, 0.0, 0.1)
        min_return = st.sidebar.slider('Minimum expected return (%)', 0.0, 30.0, 0.0, 0.1)

        # Filter data
        filtered_df = filter_data(df, excluded_columns, country_list, min_notches, min_return)

        # Display filtered data
        st.subheader('Filtered Bond Data')
        st.dataframe(filtered_df)

        # Create and display scatter plot
        st.subheader('Bond Scatter Plot: OAS vs OAD')
        scatter_fig = create_scatter_plot(filtered_df)
        st.plotly_chart(scatter_fig)

        # Create and display bar chart
        st.subheader('Expected Return by Bond')
        bar_fig = create_bar_chart(filtered_df)
        st.plotly_chart(bar_fig)

        # RVM Grid Creation
        st.subheader('Risk-Value Matrix (RVM) Grids')

        # Prepare data for RVM grid creation
        filtered_df['rating_num'] = filtered_df['Index Rating (String)'].apply(warf_to_rating_num)
        df_num = filtered_df[filtered_df['rating_num'].notnull()].copy()
        df_num['rating_num'] = df_num['rating_num'].astype(int)

        df_warf = filtered_df[filtered_df['warf'].notnull()].copy()
        df_warf['warf'] = df_warf['warf'].astype(int)

        # Create WARF map sorted DataFrame
        warf_map = dict(zip(df['Index Rating (String)'], df['warf']))
        warf_map_sorted = pd.DataFrame({
            'rating': list(warf_map.keys()),
            'warf': list(warf_map.values())
        })
        warf_map_sorted['rating_num'] = warf_map_sorted['rating'].apply(warf_to_rating_num)
        warf_map_sorted = warf_map_sorted[warf_map_sorted['rating_num'].notnull()].sort_values('warf').reset_index(drop=True)
        warf_map_sorted['rating_num'] = warf_map_sorted['rating_num'].astype(int)

        # Perform regressions
        df_num, coeffs_num, r2_num, df_warf, coeffs_warf, r2_warf = perform_regressions(df_num, warf_map_sorted)

        # Define ratings and durations for RVM grids
        ratings_order = [
            'aaa', 'aa1', 'aa2', 'aa3', 'a1', 'a2', 'a3',
            'baa1', 'baa2', 'baa3', 'ba1', 'ba2', 'ba3',
            'b1', 'b2', 'b3', 'caa1', 'caa2', 'caa3',
            'ca1', 'ca2', 'ca3', 'ca', 'c', 'd', 'sd', 'wr', 'wd'
        ]
        durations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]

        # Create RVM Grids
        rvm_num, rvm_warf = create_rvm_grids(
            ratings_order, durations, coeffs_num, coeffs_warf, warf_map=warf_map
        )

        # Display RVM Grids
        st.subheader('Numerical Rating RVM Grid')
        st.plotly_chart(create_rvm_heatmap(rvm_num, 'RVM Grid - Numerical Rating Model'))

        st.subheader('WARF-based RVM Grid')
        st.plotly_chart(create_rvm_heatmap(rvm_warf, 'RVM Grid - WARF-based Model'))

        # Display R-squared values
        st.subheader('Model Performance')
        st.write(f"Numerical Rating-based Model R-squared: {r2_num:.4f}")
        st.write(f"WARF-based Model R-squared: {r2_warf:.4f}")

        # Download button for filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name="filtered_bond_data.csv",
            mime="text/csv",
        )
    else:
        st.info("Please upload an Excel file to begin.")

if __name__ == "__main__":
    main()
