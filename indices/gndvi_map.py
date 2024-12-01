import geehydro
import folium
import ee
import indices.ee_auth
import numpy as np 
#Chlorophyll
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
def calculate_gndvi(image):
    nir = image.select('B8')
    green = image.select('B3')  # Green band for Sentinel-2

    # GNDVI calculation
    gndvi = nir.subtract(green).divide(nir.add(green)).rename('GNDVI') 
    return gndvi

def get_gndvi_params(poi):
    gndvi_min_max = gndvi.reduceRegion(reducer=ee.Reducer.minMax(), geometry=poi, scale=30).getInfo()
    gndvi_min = gndvi_min_max['GNDVI_min']
    gndvi_max = gndvi_min_max['GNDVI_max']
    gndvi_params = {
        'min': gndvi_min,  # Adjust as needed
        'max': gndvi_max,  # Adjust as needed
        'palette': ['brown', 'yellow', 'green']  # Customize if you like
    }
    return gndvi_params

def calculate_and_display_map(poi, start_year, start_month, start_day, end_year, end_month, end_day, index_choice="GNDVI"):
    global gndvi
    # (Your date formatting logic)
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1
    # Format the date
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'
    print(start_date, ", ", end_date)
    maskImage = ee.Image.constant(1).clip(poi)
    image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(poi).filterDate(start_date, end_date).mean()

    if index_choice == "GNDVI":
        gndvi = calculate_gndvi(image)
        gndvi_params = get_gndvi_params(poi) 
    else: 
        # Handle other potential index calculations if needed 
        pass 

    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=17)

   # ... (Printing min/max might be less relevant for NDNI)

    Map.setOptions('HYBRID')
    Map.addLayer(gndvi.updateMask(maskImage), gndvi_params, 'GNDVI image') 

    Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
    return Map._repr_html_() 

