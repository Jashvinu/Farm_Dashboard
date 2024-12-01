import streamlit as st
from datetime import datetime, timedelta
from indices.msavi_map import calculate_and_display_map as calculate_msavi
from indices.ndvi_map import calculate_and_display_map as calculate_ndvi
from indices.dwsi_map import calculate_and_display_map as calculate_dwsi
from indices.ndmi_map import calculate_and_display_map as calculate_ndmi
from indices.ndni_map import calculate_and_display_map as calculate_ndni
from indices.gndvi_map import calculate_and_display_map as calculate_gndvi
#from indices.fill_data import ndvi_df, gndvi_df, ndmi_df, dwsi_df, ndni_df, evi2_df
import ee
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

default_start_date = datetime.now() - timedelta(days=30)
default_end_date = datetime.now()

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

st.set_page_config(layout="wide")

# Add custom CSS for new layout
st.markdown("""
    <style>
    /* Navigation bar */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: white;
        border-bottom: 1px solid #eee;
    }
    
    .logo {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    
    /* Main title section */
    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: #1a1a1a;
        margin: 2rem 0 0.5rem 0;
        padding: 0 2rem;
    }
    
    .subtitle {
        font-size: 18px;
        color: #996B4D;
        margin-bottom: 3rem;
        padding: 0 2rem;
    }
    
    /* Form section */
    .form-section {
        padding: 0 2rem;
        margin-bottom: 2rem;
    }
    
    .form-title {
        font-size: 24px;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 1.5rem;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        font-size: 16px;
        font-weight: 500;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    /* Input styling */
    .stSelectbox, .stDateInput {
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
    }

    .info-icon {
        color: #6c757d;
        cursor: pointer;
        margin-left: 8px;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        top: -5px;
        left: 125%;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 14px;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown("""
    <div class="nav-container">
        <div class="logo">🌾 wrkFarm</div>
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
st.markdown('<h1 class="main-title">Farm Health Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Insights powered by wrkFarm\'s AI technology</p>', unsafe_allow_html=True)

# Form Section
st.markdown('<div class="form-section">', unsafe_allow_html=True)
st.markdown('<h2 class="form-title">Select Farm and Date Range</h2>', unsafe_allow_html=True)

# Farm Selection
st.markdown('<div class="form-group">', unsafe_allow_html=True)
st.markdown('<label class="form-label">Farm</label>', unsafe_allow_html=True)
farm_name = st.selectbox("", ["Select a farm...", "Farm 1", "Farm 2", "Farm 3"], label_visibility="collapsed")

# Date Range Selection
col1, col2 = st.columns(2)
with col1:
    st.markdown('<label class="form-label">Start Date</label>', unsafe_allow_html=True)
    start_date = st.date_input("", default_start_date, label_visibility="collapsed")
with col2:
    st.markdown('<label class="form-label">End Date</label>', unsafe_allow_html=True)
    end_date = st.date_input("", default_end_date, label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

# Map Insights Section
st.markdown('<h2 class="form-title">Map Insights</h2>', unsafe_allow_html=True)

# Add after the date inputs but before the if generate_button condition
generate_button = st.button("Generate Maps")

if generate_button:
    try:
        # Calculate all indices
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

        # Display maps in two rows
        row1_cols = st.columns(3, gap="medium")
        row2_cols = st.columns(3, gap="medium")

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
            st.components.v1.html(msavi_map_html, height=350, width=450)
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
            st.components.v1.html(ndvi_map_html, height=350, width=450)
            st.markdown('<div class="recommendations">', unsafe_allow_html=True)
            st.markdown("**Key Insights:**")
            st.markdown("• Green zones indicate healthy vegetation")
            st.markdown("• Yellow/red areas need attention")
            st.markdown("• Monitor for crop stress patterns")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_cols[2]:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.markdown('''
                <div class="map-header">
                    💧️ Drought Stress (DWSI)
                    <span class="tooltip">ⓘ
                        <span class="tooltiptext">Indicates water stress and drought conditions</span>
                    </span>
                </div>
            ''', unsafe_allow_html=True)
            st.components.v1.html(dwsi_map_html, height=350, width=450)
            st.markdown('<div class="recommendations">', unsafe_allow_html=True)
            st.markdown("**Key Insights:**")
            st.markdown("• Higher values indicate water stress")
            st.markdown("• Plan irrigation based on stress zones")
            st.markdown("• Monitor for drought patterns")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Second row of maps
        with row2_cols[0]:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.markdown('''
                <div class="map-header">
                    💧 Moisture Content (NDMI)
                    <span class="tooltip">ⓘ
                        <span class="tooltiptext">Shows vegetation water content and hydration status</span>
                    </span>
                </div>
            ''', unsafe_allow_html=True)
            st.components.v1.html(ndmi_map_html, height=350, width=450)
            st.markdown('<div class="recommendations">', unsafe_allow_html=True)
            st.markdown("**Key Insights:**")
            st.markdown("• Blue indicates good moisture levels")
            st.markdown("• Red shows water-deficient areas")
            st.markdown("• Use for irrigation planning")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_cols[1]:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.markdown('''
                <div class="map-header">
                    🌾 Nitrogen Status (NDNI)
                    <span class="tooltip">ⓘ
                        <span class="tooltiptext">Indicates nitrogen content in vegetation</span>
                    </span>
                </div>
            ''', unsafe_allow_html=True)
            st.components.v1.html(ndni_map_html, height=350, width=450)
            st.markdown('<div class="recommendations">', unsafe_allow_html=True)
            st.markdown("**Key Insights:**")
            st.markdown("• Higher values show good nitrogen levels")
            st.markdown("• Low values indicate fertilizer needs")
            st.markdown("• Optimize nutrient management")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with row2_cols[2]:
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.markdown('''
                <div class="map-header">
                    🍃 Chlorophyll Content (GNDVI)
                    <span class="tooltip">ⓘ
                        <span class="tooltiptext">Measures chlorophyll and photosynthetic activity</span>
                    </span>
                </div>
            ''', unsafe_allow_html=True)
            st.components.v1.html(gndvi_map_html, height=350, width=450)
            st.markdown('<div class="recommendations">', unsafe_allow_html=True)
            st.markdown("**Key Insights:**")
            st.markdown("• Shows photosynthetic efficiency")
            st.markdown("• Helps detect nutrient stress")
            st.markdown("• Monitor plant development")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
