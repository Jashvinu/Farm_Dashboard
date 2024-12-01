import geehydro
import folium
import ee
import indices.ee_auth
import numpy as np 
#Soil Moisture Stress Index
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def calculate_ndmi(image):
    nir = image.select('B8')
    swir = image.select('B11')  # SWIR band for Sentinel-2

    # NDMI calculation
    ndmi = nir.subtract(swir).divide(nir.add(swir)).rename('NDMI') 
    return ndmi

def get_ndmi_params(poi):
    ndmi_min_max = ndmi.reduceRegion(reducer=ee.Reducer.minMax(), geometry=poi, scale=30).getInfo()
    ndmi_min = ndmi_min_max['NDMI_min']
    ndmi_max = ndmi_min_max['NDMI_max']
    ndmi_params = {
        'min': ndmi_min,  # Adjust as needed
        'max': ndmi_max,  # Adjust as needed
        'palette': ['brown', 'yellow', 'green']  # Customize if you like
    }
    return ndmi_params

def calculate_and_display_map(poi, start_year, start_month, start_day, end_year, end_month, end_day, index_choice="NDMI"):
    global ndmi
    # (Your date formatting logic)
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1
    # Format the date
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'
    print(start_date, ", ", end_date)
    maskImage = ee.Image.constant(1).clip(poi)
    image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(poi).filterDate(start_date, end_date).mean()

    if index_choice == "NDMI":
        ndmi = calculate_ndmi(image)
        ndmi_params = get_ndmi_params(poi) 
    else: 
        # Handle other potential index calculations if needed 
        pass 

    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=17)

   # ... (Printing min/max might be less relevant for NDNI)

    Map.setOptions('HYBRID')
    Map.addLayer(ndmi.updateMask(maskImage), ndmi_params, 'NDMI image') 

    Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
    return Map._repr_html_() 

