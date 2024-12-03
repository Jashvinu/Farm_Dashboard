import streamlit as st
from datetime import datetime, timedelta
from indices.msavi_map import calculate_and_display_map as calculate_msavi
from indices.ndvi_map import calculate_and_display_map as calculate_ndvi
from indices.dwsi_map import calculate_and_display_map as calculate_dwsi
from indices.ndmi_map import calculate_and_display_map as calculate_ndmi
from indices.ndni_map import calculate_and_display_map as calculate_ndni
from indices.gndvi_map import calculate_and_display_map as calculate_gndvi
from indices.ph_map import calculate_and_display_ph_map as calculate_ph
from weather import get_weather_data
import ee
import matplotlib.pyplot as plt
import pandas as pd
import os
import base64
from pathlib import Path
from database.data_management.indexes_tables import get_indices_data

st.set_page_config(layout="wide")

# Load CSS from the external file


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Load the CSS file
load_css('styles.css')

# Define default dates at the start
default_start_date = datetime.now() - timedelta(days=30)
default_end_date = datetime.now()

# Define your functions first


def display_weather(api_key, latitude, longitude):
    """Fetch and display weather data."""
    weather_data = get_weather_data(latitude, longitude, api_key)
    if weather_data:
        st.markdown('', unsafe_allow_html=True)  # Start of weather report box
        st.markdown(f"""
            <div class="weather-report">
                <div class="weather-item">
                    <div class="weather-label">Temperature</div>
                    <div class="weather-value">{weather_data['temperature']['current']}°C</div>
                </div>
                <div class="weather-item">
                    <div class="weather-label">Humidity</div>
                    <div class="weather-value">{weather_data['conditions']['humidity']}%</div>
                </div>
                <div class="weather-item">
                    <div class="weather-label">Wind Speed</div>
                    <div class="weather-value">{weather_data['wind']['speed']} m/s</div>
                </div>
                <div class="weather-item">
                    <div class="weather-label">Cloud Cover</div>
                    <div class="weather-value">{weather_data['clouds']['coverage']}%</div>
                </div>
                <div class="weather-item">
                    <div class="weather-label">Conditions</div>
                    <div class="weather-value">{weather_data['conditions']['description'].title()}</div>
                </div>
                <div class="weather-item">
                    <div class="weather-label">Rainfall (1h)</div>
                    <div class="weather-value">{weather_data['rain']['last_1h'] if 'rain' in weather_data else '0'} mm</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(
            '</div>', unsafe_allow_html=True)  # End of weather report box





poi = ee.Geometry.Polygon([
    [77.77333199305133, 12.392392446684909],
    [77.77285377084087, 12.391034719901086],
    [77.77415744218291, 12.390603704636632],
    [77.77438732135664, 12.391302225016886],
    [77.77376792469431, 12.391501801924363],
    [77.77399141833513, 12.392187846379386],
    [77.77333199305133, 12.392392446684909]
])
month_names = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

try:
    ee.Initialize(project='wrkfarm-415118')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='wrkfarm-415118')


# Navigation Bar
st.markdown("""
    <div class="nav-container">
        <div class="logo" style="display: flex; align-items: center;">
            <img src="assets/logo.png" alt="wrkFarm Logo" style="height: 40px; margin-right: 10px;">
            <span style="color: black;">wrkFarm</span>
        </div>
        <div style="display: flex; gap: 2rem;">
            <span>Dashboard</span>
            <span>Maps</span>
            <span>Reports</span>
            <span>Insights</span>
            <span>Events</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main Title Section
st.markdown('<h1 class="main-title">Farm Health Dashboard</h1>',
            unsafe_allow_html=True)
st.markdown('<p class="subtitle">Insights powered by wrkFarm\'s AI technology</p>',
            unsafe_allow_html=True)

# Add auto-refresh meta tag in the header
st.markdown("""
    <meta http-equiv="refresh" content="3600">  <!-- Refresh every 1 hour (3600 seconds) -->
""", unsafe_allow_html=True)


start_date = ee.Date(datetime.now().strftime('%Y-%m-%d')).advance(-30, 'day')
end_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))

# Get the indices data
indices_df = get_indices_data(poi, start_date, end_date)

# Display the line chart for NDVI, GNDVI, and NDMI



# Create a container for the form and weather report
form_col, weather_col = st.columns([.3, 1])

with form_col:
    # Farm Selection
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="form-title">Select Farm and Date Range</h2>',
                unsafe_allow_html=True)
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.markdown('<label class="form-label">Farm</label>',
                unsafe_allow_html=True)
    farm_name = st.selectbox(
        "", ["Select a farm...", "Farm 1", "Farm 2", "Farm 3"], label_visibility="collapsed")

    # Date Range Selection
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        st.markdown('<label class="form-label">Start Date</label>',
                    unsafe_allow_html=True)
        start_date = st.date_input(
            "", default_start_date, label_visibility="collapsed")
    with date_col2:
        st.markdown('<label class="form-label">End Date</label>',
                    unsafe_allow_html=True)
        end_date = st.date_input("", default_end_date,
                                 label_visibility="collapsed")

with weather_col:
    # Weather container with shading and shadow, and reduced width

    st.markdown('<div class="weather-header">🌤️ Current Weather</div>',
                unsafe_allow_html=True)
    api_key = "267e562c624e571ae21c81bd64a27e07"  # Ensure your API key is defined
    display_weather(api_key, 12.392392446684909, 77.77333199305133)

    st.markdown('</div>', unsafe_allow_html=True)

# Auto-refresh and map generation code

try:
    # Ensure that start_date and end_date are valid
    if start_date and end_date:
        try:
            # Ensure month index is valid
            start_month_index = start_date.month - 1
            end_month_index = end_date.month - 1

            if 0 <= start_month_index < len(month_names) and 0 <= end_month_index < len(month_names):
                # Calculate all indices using the defined dates
                msavi_map_html = calculate_msavi(poi, start_date.year, month_names[start_month_index], start_date.day,
                                                    end_date.year, month_names[end_month_index], end_date.day)
               
                ndvi_map_html = calculate_ndvi(poi, start_date.year, month_names[start_month_index], start_date.day,
                                                end_date.year, month_names[end_month_index], end_date.day)
                
                dwsi_map_html = calculate_dwsi(poi, start_date.year, month_names[start_month_index], start_date.day,
                                                end_date.year, month_names[end_month_index], end_date.day)
                ndmi_map_html = calculate_ndmi(poi, start_date.year, month_names[start_month_index], start_date.day,
                                                end_date.year, month_names[end_month_index], end_date.day)
                ndni_map_html = calculate_ndni(poi, start_date.year, month_names[start_month_index], start_date.day,
                                                end_date.year, month_names[end_month_index], end_date.day)
                gndvi_map_html = calculate_gndvi(poi, start_date.year, month_names[start_month_index], start_date.day,
                                                    end_date.year, month_names[end_month_index], end_date.day)
                #ph_map_html = calculate_ph(poi, start_date.year, month_names[start_month_index], start_date.day,
                                               # end_date.year, month_names[end_month_index], end_date.day)
            else:
                st.error("Invalid month index for the selected dates.")
        except Exception as e:
            st.error(f"An error occurred while generating maps: {e}")
    else:
        st.error("Please select a valid start and end date.")

    # Add JavaScript for periodic refresh

    msavi_map_html = calculate_msavi(poi, start_date.year, month_names[start_date.month - 1], start_date.day, 
                                       end_date.year, month_names[end_date.month - 1], end_date.day)
    ndvi_map_html = calculate_ndvi(poi, start_date.year, month_names[start_date.month - 1], start_date.day,
                                    end_date.year, month_names[end_date.month - 1], end_date.day)
    dwsi_map_html = calculate_dwsi(poi, start_date.year, month_names[start_date.month - 1], start_date.day,
                                    end_date.year, month_names[end_date.month - 1], end_date.day)
    ndmi_map_html = calculate_ndmi(poi, start_date.year, month_names[start_date.month - 1], start_date.day,
                                    end_date.year, month_names[end_date.month - 1], end_date.day)
    ndni_map_html = calculate_ndni(poi, start_date.year, month_names[start_date.month - 1], start_date.day,
                                    end_date.year, month_names[end_date.month - 1], end_date.day)
    gndvi_map_html = calculate_gndvi(poi, start_date.year, month_names[start_date.month - 1], start_date.day,
                                    end_date.year, month_names[end_date.month - 1], end_date.day)
    #ph_map_html = calculate_ph(poi, start_date.year, month_names[start_date.month - 1], start_date.day,
                                    #end_date.year, month_names[end_date.month - 1], end_date.day)

    
    # Display maps in two rows
    row1_cols = st.columns([.3, .3, .7], gap="small")
    row2_cols = st.columns(4, gap="small")

    # First row of maps
    with row1_cols[0]:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="map-header">
                🌱 Soil & Vegetation (MSAVI)
                <span class="tooltip">
                    <span class="info-icon">ⓘ</span>
                    <span class="tooltiptext">Monitors vegetation health while accounting for soil exposure</span>
                </span>
            </div>
        ''', unsafe_allow_html=True)
        st.components.v1.html(msavi_map_html, height=200, width=350)
        st.markdown('<div class="recommendations">', unsafe_allow_html=True)
        st.markdown("**Key Insights:**")
        st.markdown("• Higher values indicate better vegetation coverage")
        st.markdown("• Useful for early growth stage monitoring")
        st.markdown("• Helps identify areas with soil exposure")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with row1_cols[1]:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="map-header">
                🌿 Crop Vigor (NDVI)
                <span class="tooltip">ⓘ
                    <span class="tooltiptext">Shows overall vegetation health and density</span>
                </span>
            </div>
        ''', unsafe_allow_html=True)
        st.components.v1.html(ndvi_map_html, height=200, width=350)
        st.markdown('<div class="recommendations">', unsafe_allow_html=True)
        st.markdown("**Key Insights:**")
        st.markdown("• Green zones indicate healthy vegetation")
        st.markdown("• Yellow/red areas need attention")
        st.markdown("• Monitor for crop stress patterns")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with row1_cols[2]:
        index_options = ['ndvi', 'gndvi', 'ndmi', 'dswi', 'ndni', 'evi2']
        selected_index = st.selectbox("Select an Index", index_options)

        # Display the mean, min, and max values for the selected index
        if selected_index:
            mean_value = indices_df[f'{selected_index}_mean'].iloc[-1]  # Get the latest mean value
            min_value = indices_df[f'{selected_index}_min'].iloc[-1]    # Get the latest min value
            max_value = indices_df[f'{selected_index}_max'].iloc[-1]    # Get the latest max value

            # Display the line chart for NDVI, GNDVI, and NDMI with min and max values
            chart_data = indices_df.set_index('date')[[f'{selected_index}_mean', f'{selected_index}_min', f'{selected_index}_max']]
            #chart_data = chart_data[['date', f'{selected_index}_mean', f'{selected_index}_min', f'{selected_index}_max']]
            st.line_chart(chart_data)

    with row2_cols[0]:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="map-header">
                💧️ Drought Stress (DWSI)
                <span class="tooltip">ⓘ
                    <span class="tooltiptext">Indicates water stress and drought conditions</span>
                </span>
            </div>
        ''', unsafe_allow_html=True)
        st.components.v1.html(dwsi_map_html, height=200, width=350)
        st.markdown('<div class="recommendations">', unsafe_allow_html=True)
        st.markdown("**Key Insights:**")
        st.markdown("• Higher values indicate water stress")
        st.markdown("• Plan irrigation based on stress zones")
        st.markdown("• Monitor for drought patterns")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Second row of maps
    with row2_cols[1]:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="map-header">
                💧 Moisture Content (NDMI)
                <span class="tooltip">ⓘ
                    <span class="tooltiptext">Shows vegetation water content and hydration status</span>
                </span>
            </div>
        ''', unsafe_allow_html=True)
        st.components.v1.html(ndmi_map_html, height=200, width=350)
        st.markdown('<div class="recommendations">', unsafe_allow_html=True)
        st.markdown("**Key Insights:**")
        st.markdown("• Blue indicates good moisture levels")
        st.markdown("• Red shows water-deficient areas")
        st.markdown("• Use for irrigation planning")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with row2_cols[2]:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="map-header">
                🌾 Nitrogen Status (NDNI)
                <span class="tooltip">ⓘ
                    <span class="tooltiptext">Indicates nitrogen content in vegetation</span>
                </span>
            </div>
        ''', unsafe_allow_html=True)
        st.components.v1.html(ndni_map_html, height=200, width=350)
        st.markdown('<div class="recommendations">', unsafe_allow_html=True)
        st.markdown("**Key Insights:**")
        st.markdown("• Higher values show good nitrogen levels")
        st.markdown("• Low values indicate fertilizer needs")
        st.markdown("• Optimize nutrient management")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with row2_cols[3]:
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="map-header">
                🍃 Chlorophyll Content (GNDVI)
                <span class="tooltip">ⓘ
                    <span class="tooltiptext">Measures chlorophyll and photosynthetic activity</span>
                </span>
            </div>
        ''', unsafe_allow_html=True)
        st.components.v1.html(gndvi_map_html, height=200, width=350)
        st.markdown('<div class="recommendations">', unsafe_allow_html=True)
        st.markdown("**Key Insights:**")
        st.markdown("• Shows photosynthetic efficiency")
        st.markdown("• Helps detect nutrient stress")
        st.markdown("• Monitor plant development")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    


except Exception as e:
    st.error(f"An error occurred: {e}")


# Add a last updated timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
    <div style='text-align: right; color: #666; font-size: 0.8em; padding: 10px;'>
        Last updated: {current_time}
    </div>
""", unsafe_allow_html=True)







