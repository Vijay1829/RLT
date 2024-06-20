import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu

st.set_page_config(page_title="RLT", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

@st.cache_data

def load_data(file_path):
    df = pd.read_csv(file_path, sep='\t')

    df['Key'] = df['Country'] + '_' + df['Type'] + '_' + df['Order_Category'] + '_' + df['Product']
    
    return df
    
    
def save_data(df, file_path):
    if 'Key' in df.columns:
        df.drop(columns=['Key'], inplace=True)
    df.to_csv(file_path, index=False)
    
    
def transform_data(df, type_filter, current_week, max_weeks=12):
    df_filtered = df[df['Key'] == type_filter]
    df_filtered['Week'] = pd.to_datetime(df_filtered['Date']).dt.isocalendar().week
    df_filtered['Day'] = pd.to_datetime(df_filtered['Date']).dt.day_name()
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date']).dt.date
    df_filtered['Adjusted_Week'] = df_filtered['Week'] - current_week + 1
    df_filtered = df_filtered[df_filtered['Adjusted_Week'] <= max_weeks]  # Filter for up to 12 weeks
    df_filtered = df_filtered.sort_values(by=['Date'])
    return df_filtered


# File path (adjust to your actual file path)
country = "USA"  # This can be parameterized based on user selection if needed
forecast_file_path = f"./{country}_forecasts.csv"
model_file_path = f"./{country}_model.csv"

# Load the data
df_forecast = load_data(forecast_file_path)
df_model = load_data(model_file_path)


title = f"""
RLT Country Tool
## {country} : Commercial
"""



st.title(title)



# Get the current week number
current_week = pd.Timestamp.today().isocalendar().week

# Define tabs for different categories
#tabs = st.tabs(["PL.Base", "PL.Best", "Lutathera.Base"])   
#tabs = ["PL.Base", "PL.Best", "Lutathera.Base"]



# Function to render calendar view
def render_calendar_view(type_filter):
   # st.header(f"{type_filter} Demand")
    df_filtered = transform_data(df_forecast, type_filter, current_week, max_weeks=12)
    df_model_filtered = transform_data(df_model, type_filter, current_week, max_weeks=12)

    weeks = df_filtered['Adjusted_Week'].unique()

    # Define color mapping
    color_mapping = {}
    for week in weeks:
        if week < 1:
            color_mapping[week] = '#A0A0A0'
        elif 1 <= week <= 2:
            color_mapping[week] = '#FFEB3B'
        elif 3 <= week <= 7:
            color_mapping[week] = '#51AA55'
        elif 8 <=week :
            color_mapping[week] = '#ED8E16'
        elif 9 <= week <= 10:
            color_mapping[week] = '#67B46B'       
        else:
            color_mapping[week] = '#A0A0A0'

    for week in weeks:
        st.markdown(
            f"""
            <div style='
                padding: 5px;
                margin-bottom: 5px;
                background-color: {color_mapping[week]};
                border-radius: 5px;
                border: 2px solid #ccc;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
                color: #333;
                font-size: 20px;
            '>
            Week {week}
            </div>
            """,
            unsafe_allow_html=True
        )
        #st.subheader(f"Week {week}")
        week_data = df_filtered[df_filtered['Adjusted_Week'] == week]
        week_model_data = df_model_filtered[df_model_filtered['Adjusted_Week'] == week]
        week_data.set_index('Date', inplace=True)
        week_model_data.set_index('Date', inplace=True)

        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        cols = st.columns([6] + [10] * 7)
        with cols[0]:
            st.markdown("<div style='text-align: left; padding: 0px; margin-top: 90px; margin-bottom: 2px; '>", unsafe_allow_html=True)
            #st.subheader(f"**Week {week}**")
            
            st.write("**New**")

            st.write("**Total**")

            st.markdown("</div>", unsafe_allow_html=True)

        for idx, day in enumerate(days_of_week):
            with cols[idx + 1]:
                st.write(day)  # Display first 3 letters of the day to save space
                if day in week_data['Day'].values:
                    date = week_data[week_data['Day'] == day].index[0]
                    new_value = week_data.loc[date, 'New']
                    total_value = week_data.loc[date, 'Total']

                else:
                    date = None
                    new_value = 0
                    total_value = 0
                    
                
                if day in week_model_data['Day'].values:
                    model_value = week_model_data.loc[week_model_data[week_model_data['Day'] == day].index[0], 'Total']
                    model_new = week_model_data.loc[week_model_data[week_model_data['Day'] == day].index[0], 'New']
                else:
                    model_value = 0
                    model_new = 0

                st.date_input(f"Date", value=date, key=f"{type_filter}_{week}_{day}_date", disabled=True, label_visibility='collapsed') 
                
                Country, Model = st.columns(2)
                
                with Country:
                    new_value = st.number_input(
                        f"New ({day})", value=int(new_value), key=f"{type_filter}_{week}_{day}_New", label_visibility='collapsed' )
                    total_value = st.number_input(
                        f"Total ({day})", value=int(total_value), key=f"{type_filter}_{week}_{day}_Total", label_visibility='collapsed' )         
    
                with Model:
                    
                    model_new = st.number_input(
                        f"Model ({day})", value=int(model_new), key=f"{type_filter}_{week}_{day}_Model_New", disabled=True,
                        label_visibility='collapsed' )
                    
                    
                    model_value = st.number_input(
                        f"Model ({day})", value=int(model_value), key=f"{type_filter}_{week}_{day}_Model", disabled=True,
                        label_visibility='collapsed' )
                
 


    if st.button("Submit Demand"):
        for week in weeks:
            week_data = df_filtered[df_filtered['Adjusted_Week'] == week]
            for day in days_of_week:
                if day in week_data['Day'].values:
                    date = week_data[week_data['Day'] == day].index[0]
                else:
                    date = None
                
                new_value = st.session_state[f"{type_filter}_{week}_{day}_New"]
                total_value = st.session_state[f"{type_filter}_{week}_{day}_Total"]

                df_forecast.loc[(pd.to_datetime(df_forecast['Date']).dt.isocalendar().week - current_week + 1 == week) & 
                                (df_forecast['Key'] == type_filter) & 
                                (pd.to_datetime(df_forecast['Date']).dt.day_name() == day), 'New'] = new_value
                
                df_forecast.loc[(pd.to_datetime(df_forecast['Date']).dt.isocalendar().week - current_week + 1 == week) &
                                (df_forecast['Key'] == type_filter) & 
                                (pd.to_datetime(df_forecast['Date']).dt.day_name() == day), 'Total'] = total_value

        save_data(df_forecast, forecast_file_path)
        st.success("Data updated successfully!")


selected = option_menu(
menu_title= None , #["Pluvicto.base","Pluvicto.best", "Lutathera.base" ],  
options = ["Pluvicto.base","Pluvicto.best", "Lutathera.base" ],
icons=None, 
menu_icon="cast",  
default_index=0,  
orientation="horizontal",
styles={
        "container": {
            "padding": "10px",
            "background-color": "#f8f9fa",
            "border-radius": "8px",
            "box-shadow": "0 2px 4px rgba(0, 0, 0, 0.1)"
        },
        "icon": {
            "color": "#79E95D",  # Blue color for icons
            "font-size": "24px",  # Larger font size for icons
            "margin-right": "10px"  # Add space between icon and text
        },
        "nav-link": {
            "font-size": "18px",  # Font size for menu items
            "text-align": "center",  # Center align text
            "padding": "8px 20px",  # Padding around menu items
            "border-radius": "5px",  # Rounded corners
            "color": "#0E0F0D",  # Text color
            "transition": "background-color 0.5s",  # Smooth transition for hover effect
            "margin": "5px",  # Margin around menu items
            "background-color": "transparent",  # Transparent background initially
            "border": "2px solid transparent",  # Transparent border initially
        },
        "nav-link-selected": {
            "background-color": "#85D970",  # Background color when selected
            "color": "#fff",  # Text color when selected
            "font-weight": "bold",  # Bold text when selected
            "border": "1px solid #007bff",  # Border when selected
            "border-radius": "5px"  # Rounded corners when selected
        },
    }
)


if selected == "Pluvicto.base":
    render_calendar_view("USA_Base_Commercial_Pluvicto")

elif selected == "Pluvicto.best":
    render_calendar_view("USA_Best_Commercial_Pluvicto")

elif selected == "Lutathera.base":
    render_calendar_view("USA_Base_Commercial_Lutathera")


    

    
    


    
    
