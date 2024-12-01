import geehydro
import folium
import ee
import indices.ee_auth
# ... (Your Earth Engine initialization and POI definition)
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
def calculate_ndvi(image):
    nir = image.select('B8')
    red = image.select('B4')

    # NDVI calculation
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    return ndvi


def get_ndvi_params(poi):
    ndvi_min_max = ndvi.reduceRegion(reducer=ee.Reducer.minMax(), geometry=poi, scale=30).getInfo()
    ndvi_min = ndvi_min_max['NDVI_min']
    ndvi_max = ndvi_min_max['NDVI_max']
    ndvi_params = {
        'min': ndvi_min,  # Adjust as needed
        'max': ndvi_max,  # Adjust as needed
        'palette': ['brown', 'yellow', 'green']  # Customize if you like
    }
    return ndvi_params


def calculate_and_display_map(poi, start_year, start_month, start_day, end_year, end_month, end_day):
    global ndvi
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1
    # Format the date
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'
    print(start_date, ", ", end_date)

    maskImage = ee.Image.constant(1).clip(poi)
    image = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterBounds(poi).filterDate(start_date, end_date).mean()

    ndvi = calculate_ndvi(image)  # Main change here
    ndvi_params = get_ndvi_params(poi) 

    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=17)

    # ... (Printing min/max might be less relevant for NDVI)
    print(ndvi.reduceRegion(reducer=ee.Reducer.minMax(),
          geometry=poi, scale=30).getInfo())
    Map.setOptions('HYBRID')
    Map.addLayer(ndvi.updateMask(maskImage), ndvi_params, 'NDVI image')  # Update layer name 

    Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
    return Map._repr_html_() 
