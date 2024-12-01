import streamlit as st
from indices.msavi_map import calculate_and_display_map as calculate_msavi
from indices.ndvi_map import calculate_and_display_map as calculate_ndvi
from indices.dwsi_map import calculate_and_display_map as calculate_dwsi
from indices.ndmi_map import calculate_and_display_map as calculate_ndmi
from indices.ndni_map import calculate_and_display_map as calculate_ndni
from indices.gndvi_map import calculate_and_display_map as calculate_gndvi




import datetime  # Import the datetime module

# Initialize Earth Engine (Place this at the beginning if shared across modules)
import ee

try:
    ee.Initialize(project='wrkfarm-415118')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='wrkfarm-415118')


# Page Title
st.title("Satellite Index Map Generator")

# Define your specific Point of Interest (POI) as an EE Geometry
# Replace with your POI coordinates
poi = ee.Geometry.Polygon([
    [77.77333199305133, 12.392392446684909],
    [77.77285377084087, 12.391034719901086],
    [77.77415744218291, 12.390603704636632],
    [77.77438732135664, 12.391302225016886],
    [77.77376792469431, 12.391501801924363],
    [77.77399141833513, 12.392187846379386],
    [77.77333199305133, 12.392392446684909]
])


# ... (Rest of your code: POI, Earth Engine initialization, etc.)

# Date Input Components - Updated for default values
year_choices = [str(year) for year in range(2015, 2025)]
month_choices = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]

# Calculate default dates
today = datetime.date.today()
default_start_date = today - datetime.timedelta(days=3)

# User Inputs (Sidebar)
st.sidebar.header("Select Date Range and Index")

# Start Date (With Default)
start_year = st.sidebar.selectbox(
    "Start Year", year_choices, index=year_choices.index(str(default_start_date.year)))
start_month = st.sidebar.selectbox(
    "Start Month", month_choices, index=default_start_date.month - 1)
start_day = st.sidebar.number_input(
    "Start Day", min_value=1, max_value=31, value=default_start_date.day)

# End Date (With Default)
end_year = st.sidebar.selectbox(
    "End Year", year_choices, index=year_choices.index(str(today.year)))
end_month = st.sidebar.selectbox(
    "End Month", month_choices, index=today.month - 1)
end_day = st.sidebar.number_input(
    "End Day", min_value=1, max_value=31, value=today.day)

index_choice = st.sidebar.radio("Select Index", ["MSAVI", "NDVI", "DWSI", "NDMI", "NDNI", "GNDVI"])

# Button and Display
if st.button('Calculate and Display Map'):
    try:
        if index_choice == "MSAVI":
            map_html = calculate_msavi(
                poi, start_year, start_month, start_day, end_year, end_month, end_day)
        elif index_choice == "NDVI":
            map_html = calculate_ndvi(
                poi, start_year, start_month, start_day, end_year, end_month, end_day)
        elif index_choice == "DWSI":
            map_html = calculate_dwsi(
                poi, start_year, start_month, start_day, end_year, end_month, end_day)
        elif index_choice == "NDMI":
            map_html = calculate_ndmi(
                poi, start_year, start_month, start_day, end_year, end_month, end_day)
        
        elif index_choice == "NDNI":
            map_html = calculate_ndni(
                poi, start_year, start_month, start_day, end_year, end_month, end_day)
        elif index_choice == "GNDVI":
            map_html = calculate_gndvi(
                poi, start_year, start_month, start_day, end_year, end_month, end_day)
        st.components.v1.html(map_html, height=500)
    except Exception as e:
        st.error(f"An error occurred: {e}")
