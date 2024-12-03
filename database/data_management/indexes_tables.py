import ee
from datetime import datetime, timedelta
import pandas as pd

def calculate_indices(image):
    """
    Calculate various spectral indices for a Sentinel-2 image.
    
    Indices calculated:
    - NDVI: Normalized Difference Vegetation Index
    - GNDVI: Green Normalized Difference Vegetation Index
    - NDMI: Normalized Difference Moisture Index
    - DSWI: Difference Water Stress Index
    - NDNI: Normalized Difference Nitrogen Index
    - EVI2: Enhanced Vegetation Index 2
    """
    # Band selections for Sentinel-2
    nir = image.select('B8')
    red = image.select('B4')
    green = image.select('B3')
    swir1 = image.select('B11')
    swir2 = image.select('B12')
    red_edge = image.select('B5')

    # Calculate indices
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    gndvi = nir.subtract(green).divide(nir.add(green)).rename('GNDVI')
    ndmi = nir.subtract(swir1).divide(nir.add(swir1)).rename('NDMI')
    dswi = (nir.add(swir1)).divide(red.add(swir2)).rename('DSWI')
    
    ndni = (nir.subtract(red_edge).log()).divide(
        nir.add(red_edge).log()
    ).rename('NDNI')

    evi2 = ee.Image(2.5).multiply(nir.subtract(red)).divide(
        nir.add(ee.Image(2.4).multiply(red)).add(ee.Image(1))
    ).rename('EVI2')

    return image.addBands([ndvi, gndvi, ndmi, dswi, ndni, evi2])

def get_indices_data(poi, start_date, end_date):
    """
    Retrieve indices data for a specific point of interest over a date range.
    
    Args:
        poi (ee.Geometry): Point of interest
        start_date (ee.Date): Start date for data collection
        end_date (ee.Date): End date for data collection
    
    Returns:
        list: List of dictionaries with indices data for each date
    """
    indices_data = []
    current_date = start_date

    print(f"Fetching indices data from {start_date.format('YYYY-MM-dd').getInfo()} to {end_date.format('YYYY-MM-dd').getInfo()}")

    try:
        while current_date.getInfo()['value'] < end_date.getInfo()['value']:
            next_date = current_date.advance(5, 'day')
            
            # Filter image collection
            image_collection = (
                ee.ImageCollection('COPERNICUS/S2')
                .filterDate(current_date, next_date)
                .filterBounds(poi)
                .filter(ee.Filter.lessThan('CLOUDY_PIXEL_PERCENTAGE', 30))
            )
            
            # Check if images are available
            if image_collection.size().getInfo() > 0:
                # Compute mean indices for the period
                image_with_indices = image_collection.map(calculate_indices).mean()
                
                # Reduce region to get statistics
                stats = image_with_indices.reduceRegion(
                    reducer=ee.Reducer.mean().combine(
                        ee.Reducer.minMax(), 
                        sharedInputs=True
                    ),
                    geometry=poi,
                    scale=30,
                    maxPixels=1e9
                ).getInfo()
                
                # Structure data for MongoDB
                indices_record = {
                    'date': current_date.format('YYYY-MM-dd').getInfo(),
                    'indices': {
                        'NDVI': {
                            'mean': stats.get('NDVI_mean', None),
                            'min': stats.get('NDVI_min', None),
                            'max': stats.get('NDVI_max', None)
                        },
                        'GNDVI': {
                            'mean': stats.get('GNDVI_mean', None),
                            'min': stats.get('GNDVI_min', None),
                            'max': stats.get('GNDVI_max', None)
                        },
                        'NDMI': {
                            'mean': stats.get('NDMI_mean', None),
                            'min': stats.get('NDMI_min', None),
                            'max': stats.get('NDMI_max', None)
                        },
                        'DSWI': {
                            'mean': stats.get('DSWI_mean', None),
                            'min': stats.get('DSWI_min', None),
                            'max': stats.get('DSWI_max', None)
                        },
                        'NDNI': {
                            'mean': stats.get('NDNI_mean', None),
                            'min': stats.get('NDNI_min', None),
                            'max': stats.get('NDNI_max', None)
                        },
                        'EVI2': {
                            'mean': stats.get('EVI2_mean', None),
                            'min': stats.get('EVI2_min', None),
                            'max': stats.get('EVI2_max', None)
                        }
                    }
                }
                
                indices_data.append(indices_record)
            
            current_date = next_date

    except Exception as e:
        print(f"Error in get_indices_data: {e}")
        return []

    if not indices_data:
        print("No indices data available for the specified period.")
    
    return indices_data