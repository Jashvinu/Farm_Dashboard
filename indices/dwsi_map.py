import geehydro
import folium
import ee
import indices.ee_auth
import numpy as np
# disease water index
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def calculate_dwsi(image):
    nir = image.select('B8')
    red = image.select('B4')
    swir1 = image.select('B11')
    swir2 = image.select('B12')

    dwsi = (nir.add(swir1)).divide(red.add(swir2)).rename('dwsi')
    return dwsi


def get_dwsi_params(poi):
    dwsi_min_max = dwsi.reduceRegion(
        reducer=ee.Reducer.minMax(), geometry=poi, scale=30).getInfo()
    dwsi_min = dwsi_min_max['dwsi_min']
    dwsi_max = dwsi_min_max['dwsi_max']
    dwsi_params = {
        'min': dwsi_min,  # Adjust as needed
        'max': dwsi_max,  # Adjust as needed
        'palette': ['brown', 'yellow', 'green']  # Customize if you like
    }
    return dwsi_params


def calculate_and_display_map(poi, start_year, start_month, start_day, end_year, end_month, end_day, index_choice="dwsi"):
    global dwsi
    # (Your date formatting logic)
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1
    # Format the date
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'
    print(start_date, ", ", end_date)
    maskImage = ee.Image.constant(1).clip(poi)
    image = ee.ImageCollection(
        'COPERNICUS/S2_HARMONIZED').filterBounds(poi).filterDate(start_date, end_date).mean()

    if index_choice == "dwsi":
        dwsi = calculate_dwsi(image)
        dwsi_params = get_dwsi_params(poi)
    else:
        # Handle other potential index calculations if needed
        pass

    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=17)

   # ... (Printing min/max might be less relevant for NDNI)

    Map.setOptions('HYBRID')
    Map.addLayer(dwsi.updateMask(maskImage), dwsi_params, 'dwsi image')

    Map.setControlVisibility(
        layerControl=True, fullscreenControl=True, latLngPopup=True)
    return Map._repr_html_()
