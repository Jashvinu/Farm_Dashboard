import ee
import folium
import geehydro  # Enables the visualization of Earth Engine data layers in folium
import indices.ee_auth

# Initialize the Earth Engine API
ee.Initialize()

# Function to apply scaling factors for Landsat 8 imagery
def apply_scale_factors(image):
    # Apply scaling factors for optical bands
    optical_bands = image.select('SR_B.*').multiply(0.0000275).add(-0.2)
    
    # Apply scaling factors for thermal bands (not used in pH calculation but included for completeness)
    thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    
    # Add the scaled bands to the image
    return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)

# Function to calculate pH based on spectral indices
def calculate_ph(image):
    B2 = image.select('SR_B2')  # Blue band
    B3 = image.select('SR_B3')  # Green band
    B4 = image.select('SR_B4')  # Red band
    B6 = image.select('SR_B6')  # SWIR1 band
    B7 = image.select('SR_B7')  # SWIR2 band

    # pH Calculation using the given formula
    ph_eq1 = ee.Image(6.493).subtract(ee.Image(35.152).multiply(B2)) \
        .subtract(ee.Image(52.380).multiply(B3)) \
        .add(ee.Image(1.099).multiply(B4)) \
        .add(ee.Image(30.040).multiply(B6)) \
        .subtract(ee.Image(8.181).multiply(B7)) \
        .rename('pH')
    
    return ph_eq1

# Function to get visualization parameters for pH
def get_ph_params(ph_image, poi):
    ph_min_max = ph_image.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=poi,
        scale=30,
        bestEffort=True
    ).getInfo()

    ph_min = ph_min_max.get('pH_min', 3)
    ph_max = ph_min_max.get('pH_max', 11)  # Default to pH range 0-14 if unavailable

    vis_params = {
        'min': ph_min,
        'max': ph_max,
        'palette': ['red', 'orange', 'yellow', 'green', 'blue']  # Customize pH color palette
    }
    return vis_params


# Month name list
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Function to calculate and display pH map with proper date formatting
def calculate_and_display_ph_map(poi, start_year, start_month, start_day, end_year, end_month, end_day):
    start_month_index = month_names.index(start_month) + 1
    end_month_index = month_names.index(end_month) + 1

    # Format the date correctly
    start_date = f'{start_year}-{start_month_index:02}-{start_day:02}'
    end_date = f'{end_year}-{end_month_index:02}-{end_day:02}'

    print(f"Date Range: {start_date} to {end_date}")  # Debugging line

    # Load the Landsat 8 dataset and filter by date and location
    dataset = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
        .filterDate(start_date, end_date) \
        .filterBounds(poi) \
        .map(apply_scale_factors)

    # Select the first image in the filtered dataset
    image = dataset.first()

    # Calculate pH
    ph_image = calculate_ph(image).clip(poi)

    # Get pH visualization parameters (as described earlier)
    vis_params = get_ph_params(ph_image, poi)

    # Get the center coordinates of the POI for map centering
    center_lat = poi.centroid().coordinates().get(1).getInfo()
    center_lon = poi.centroid().coordinates().get(0).getInfo()

    # Create the folium map
    Map = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    Map.add_ee_layer(ph_image, vis_params, 'Soil pH')

    # Add controls for the map
    Map.add_child(folium.LayerControl())
    Map.add_child(folium.LatLngPopup())

    return Map._repr_html_()

