import streamlit as st
import pandas as pd
import numpy as np
import os

# Load data function
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

# Save data function
def save_data(df, file_path):
    df.to_excel(file_path, index=False)

# Function to transform data for calendar view
def transform_data(df, type_filter):
    df_filtered = df[df['Type'] == type_filter]
    df_filtered['Week'] = pd.to_datetime(df_filtered['Date']).dt.isocalendar().week
    df_filtered['Day'] = pd.to_datetime(df_filtered['Date']).dt.day_name()
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date']).dt.date
    df_filtered = df_filtered.sort_values(by=['Date'])
    return df_filtered

# Initialize the app
st.title("Forecast Data Management")

# Tabs for different categories
tabs = st.tabs(["PL.Base", "PL.Best", "Lutathera.Base"])

# File path (adjust to your actual file path)
country = "USA"  # This can be parameterized based on user selection if needed
file_path = f"./{country}_forecasts.xlsx"

# Load the data
df = load_data(file_path)

# Function to render calendar view
def render_calendar_view(type_filter):
    st.header(f"{type_filter} Values")
    df_filtered = transform_data(df, type_filter)

    weeks = df_filtered['Week'].unique()

    for week in weeks:
        st.subheader(f"Week {week}")
        week_data = df_filtered[df_filtered['Week'] == week]
        week_data.set_index('Date', inplace=True)

        cols = st.columns(7)
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for idx, day in enumerate(days_of_week):
            if day in week_data['Day'].values:
                date = week_data[week_data['Day'] == day].index[0]
                new_value = week_data.loc[date, 'New']
                total_value = week_data.loc[date, 'Total']
            else:
                date = None
                new_value = 0
                total_value = 0
            
            with cols[idx]:
                st.write(day)
               # st.date_input(f"Date ({day})", value=date, key=f"{type_filter}_{week}_{day}_date")
                new_value = st.number_input("New", value=int(new_value), key=f"{type_filter}_{week}_{day}_new")
                total_value = st.number_input("Total", value=int(total_value), key=f"{type_filter}_{week}_{day}_total")

    if st.button(f"Save {type_filter} Data"):
        for week in weeks:
            week_data = df_filtered[df_filtered['Week'] == week]
            for day in days_of_week:
                if day in week_data['Day'].values:
                    date = week_data[week_data['Day'] == day].index[0]
                else:
                    date = None
                
                new_value = st.session_state[f"{type_filter}_{week}_{day}_new"]
                total_value = st.session_state[f"{type_filter}_{week}_{day}_total"]

                df.loc[(pd.to_datetime(df['Date']).dt.isocalendar().week == week) & (df['Type'] == type_filter) & (pd.to_datetime(df['Date']).dt.day_name() == day), 'New'] = new_value
                df.loc[(pd.to_datetime(df['Date']).dt.isocalendar().week == week) & (df['Type'] == type_filter) & (pd.to_datetime(df['Date']).dt.day_name() == day), 'Total'] = total_value

        save_data(df, file_path)
        st.success("Data updated successfully!")

# Display calendar views in respective tabs
with tabs[0]:
    render_calendar_view("Base")
    
with tabs[1]:
    render_calendar_view("Best")
    
with tabs[2]:
    render_calendar_view("Lutathera.Base")
