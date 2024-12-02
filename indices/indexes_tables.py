import ee
from datetime import datetime, timedelta
import pandas as pd

def calculate_indices(image):
    # NDVI
    nir = image.select('B8')
    red = image.select('B4')
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')

    # GNDVI
    green = image.select('B3')
    gndvi = nir.subtract(green).divide(nir.add(green)).rename('GNDVI')

    # NDMI
    swir = image.select('B11')
    ndmi = nir.subtract(swir).divide(nir.add(swir)).rename('NDMI')

    # DSWI
    swir1 = image.select('B11')
    swir2 = image.select('B12')
    dswi = (nir.add(swir1)).divide(red.add(swir2)).rename('DSWI')

    # NDNI
    red_edge = image.select('B5')
    numerator = nir.subtract(red_edge).log()
    denominator = nir.add(red_edge).log()
    ndni = numerator.subtract(denominator).rename('NDNI')

    # EVI2
    evi2 = ee.Image(2.5).multiply(nir.subtract(red)).divide(nir.add(ee.Image(2.4).multiply(red)).add(ee.Image(1))).rename('EVI2')

    return image.addBands([ndvi, gndvi, ndmi, dswi, ndni, evi2])

def get_indices_data(poi, start_date, end_date):
    indices_data = []
    print(indices_data)
    current_date = start_date
    while current_date.getInfo()['value'] < end_date.getInfo()['value']:
        next_date = current_date.advance(5, 'day')
        image_collection = (
            ee.ImageCollection('COPERNICUS/S2')
            .filterDate(current_date, next_date)
            .filterBounds(poi)
        )
        if image_collection.size().getInfo() > 0:
            image_with_indices = image_collection.map(calculate_indices).mean()
            stats = image_with_indices.reduceRegion(
                reducer=ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True),
                geometry=poi,
                scale=30
            ).getInfo()
            indices_data.append({
                'date': current_date.format('YYYY-MM-dd').getInfo(),
                'ndvi_mean': stats['NDVI_mean'],
                'ndvi_min': stats['NDVI_min'],
                'ndvi_max': stats['NDVI_max'],
                'gndvi_mean': stats['GNDVI_mean'],
                'gndvi_min': stats['GNDVI_min'],
                'gndvi_max': stats['GNDVI_max'],
                'ndmi_mean': stats['NDMI_mean'],
                'ndmi_min': stats['NDMI_min'],
                'ndmi_max': stats['NDMI_max'],
                'dswi_mean': stats['DSWI_mean'],
                'dswi_min': stats['DSWI_min'],
                'dswi_max': stats['DSWI_max'],
                'ndni_mean': stats['NDNI_mean'],
                'ndni_min': stats['NDNI_min'],
                'ndni_max': stats['NDNI_max'],
                'evi2_mean': stats['EVI2_mean'],
                'evi2_min': stats['EVI2_min'],
                'evi2_max': stats['EVI2_max']
            })
        current_date = next_date
        print(indices_data)
    return pd.DataFrame(indices_data)