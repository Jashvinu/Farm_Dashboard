import geehydro
import folium
import ee
import os
import indices.ee_auth


# Initialize Earth Engine
import ee

try:
    ee.Initialize(project='wrkfarm-415118')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='wrkfarm-415118')


# Define your specific Point of Interest (POI) as an EE Geometry
poi = ee.Geometry.Polygon([
    [77.77333199305133, 12.392392446684909],
    [77.77285377084087, 12.391034719901086],
    [77.77415744218291, 12.390603704636632],
    [77.77438732135664, 12.391302225016886],
    [77.77376792469431, 12.391501801924363],
    [77.77399141833513, 12.392187846379386],
    [77.77333199305133, 12.392392446684909]
])


# poi = ee.Geometry.Polygon([
#     [77.775624,12.393202 ],
#     [77.775533,12.391877 ],
#     [77.776635,12.391124 ],
#     [77.777140,12.392875 ],
#     [77.775624,12.393202 ]
# ])

month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def calculate_msavi(image):
    nir = image.select('B8')
    red = image.select('B4')

    # MSAVI with dynamically calculated soil adjustment factor L
    L = nir.multiply(2).add(1).subtract(
        (nir.multiply(2).add(1).pow(2).subtract(
            nir.subtract(red).multiply(8))).sqrt()
    ).divide(2)

    msavi = nir.multiply(2).add(1).subtract(
        (nir.multiply(2).add(1).pow(2).subtract(
            nir.subtract(red).multiply(8))).sqrt()
    ).divide(nir.multiply(2).add(1).add(L))

    return msavi.rename('MSAVI')


def get_msavi_params(poi):
    msavi_min_max = msavi.reduceRegion(reducer=ee.Reducer.minMax(), geometry=poi, scale=30).getInfo()
    msavi_min = msavi_min_max['MSAVI_min']
    msavi_max = msavi_min_max['MSAVI_max']

    msavi_params = {
        'min': msavi_min,
        'max': msavi_max,
        'palette': ['brown', 'yellow', 'green']
    }

    return msavi_params


def calculate_and_display_map(poi,start_year, start_month, start_day, end_year, end_month, end_day):
    global msavi
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1
    # Format the date
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'
    print(start_date, ", ", end_date)

    maskImage = ee.Image.constant(1).clip(poi)
    image = ee.ImageCollection(
        'COPERNICUS/S2_HARMONIZED'
    ).filterBounds(poi).filterDate(start_date, end_date).mean()

    msavi = calculate_msavi(image)
    msavi_params = get_msavi_params(poi)
    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=17)

    # Print the minimum and maximum MSAVI values
    print(msavi.reduceRegion(reducer=ee.Reducer.minMax(),
          geometry=poi, scale=30).getInfo())
    Map.setOptions('HYBRID')
    # Add the MSAVI layer to the map
    Map.addLayer(msavi.updateMask(maskImage), msavi_params, 'MSAVI image')

    # Set control visibility
    Map.setControlVisibility(
        layerControl=True, fullscreenControl=True, latLngPopup=True)
    map_html = Map._repr_html_()
    return map_html

    # ... (rest of the calculate_and_display_map function remains the same)
