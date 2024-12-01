import geehydro
import folium
import ee
import indices.ee_auth
import numpy as np 
#Nitrogen
#Nitrogen
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
def calculate_ndni(image):
    nir = image.select('B8')
    red_edge = image.select('B5')  # Assuming Sentinel-2

    # NDNI calculation (Logarithmic Formula)
    numerator = np.log(nir.subtract(red_edge))
    denominator = np.log(nir.add(red_edge))
    ndni = numerator.subtract(denominator).rename('NDNI')

    return ndni

def get_ndni_params(poi):
    ndni_min_max = ndni.reduceRegion(reducer=ee.Reducer.minMax(), geometry=poi, scale=30).getInfo()
    ndni_min = ndni_min_max['NDNI_min']
    ndni_max = ndni_min_max['NDNI_max']
    ndni_params = {
        'min': ndni_min,  # Adjust as needed
        'max': ndni_max,  # Adjust as needed
        'palette': ['brown', 'yellow', 'green']  # Customize if you like
    }
    return ndni_params

def calculate_and_display_map(poi, start_year, start_month, start_day, end_year, end_month, end_day, index_choice="NDNI"):
    global ndni
    # (Your date formatting logic)
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1
    # Format the date
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'
    print(start_date, ", ", end_date)
    maskImage = ee.Image.constant(1).clip(poi)
    image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(poi).filterDate(start_date, end_date).mean()

    if index_choice == "NDNI":
        ndni = calculate_ndni(image)
        ndni_params = get_ndni_params(poi) 
    else: 
        # Handle other potential index calculations if needed 
        pass 

    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=17)

   # ... (Printing min/max might be less relevant for NDNI)

    Map.setOptions('HYBRID')
    Map.addLayer(ndni.updateMask(maskImage), ndni_params, 'NDNI image') 

    Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
    return Map._repr_html_() 

