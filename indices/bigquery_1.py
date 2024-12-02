import os
import ee
from google.cloud import bigquery
from indexes_tables import get_indices_data
from datetime import datetime, timedelta
import ee_auth
import pandas as pd 

# Initialize Earth Engine
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/jashvinuyeshwanth/Satellite_output/new_App/indices/wrkfarm-415118-3652909893e8.json"
ee.Initialize()

# Define your point of interest (farmland)
poi = ee.Geometry.Polygon([
    [77.77333199305133, 12.392392446684909],
    [77.77285377084087, 12.391034719901086],
    [77.77415744218291, 12.390603704636632],
    [77.77438732135664, 12.391302225016886],
    [77.77376792469431, 12.391501801924363],
    [77.77399141833513, 12.392187846379386],
    [77.77333199305133, 12.392392446684909]
])

# Create a BigQuery client
client = bigquery.Client()

# Specify the table details
table_id = 'wrkfarm-415118.Major_indices.indices_web'

# Define the schema for your BigQuery table
schema = [
    bigquery.SchemaField("date", "STRING"), 
    bigquery.SchemaField("ndvi_mean", "FLOAT"),
    bigquery.SchemaField("ndvi_min", "FLOAT"),
    bigquery.SchemaField("ndvi_max", "FLOAT"),
    bigquery.SchemaField("gndvi_mean", "FLOAT"),
    bigquery.SchemaField("gndvi_min", "FLOAT"),
    bigquery.SchemaField("gndvi_max", "FLOAT"),
    bigquery.SchemaField("ndmi_mean", "FLOAT"),
    bigquery.SchemaField("ndmi_min", "FLOAT"),
    bigquery.SchemaField("ndmi_max", "FLOAT"),
    bigquery.SchemaField("dswi_mean", "FLOAT"),
    bigquery.SchemaField("dswi_min", "FLOAT"),
    bigquery.SchemaField("dswi_max", "FLOAT"),
    bigquery.SchemaField("ndni_mean", "FLOAT"),
    bigquery.SchemaField("ndni_min", "FLOAT"),
    bigquery.SchemaField("ndni_max", "FLOAT"),
    bigquery.SchemaField("evi2_mean", "FLOAT"),
    bigquery.SchemaField("evi2_min", "FLOAT"),
    bigquery.SchemaField("evi2_max", "FLOAT")
]



def update_bigquery_table():
    """Updates the BigQuery table with the latest indices data."""

    # Get the current date and the latest date from the BigQuery table
    current_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))
    latest_date = get_latest_date_from_bigquery(table_id)

    if latest_date < current_date:
        # Calculate the start and end dates for fetching new data
        new_start_date = ee.Date(latest_date.advance(1, 'day'))
        new_end_date = current_date

        # Get the new indices data from Earth Engine
        new_df = get_indices_data(poi, new_start_date, new_end_date)

        # Load the updated data into BigQuery
        load_data_to_bigquery(new_df, table_id, schema)

    else:
        print("The latest date in the table is already up-to-date.")


def get_latest_date_from_bigquery(table_id):
    """Gets the latest date from the specified BigQuery table."""
    query = f"SELECT MAX(date) AS latest_date FROM `{table_id}`"
    query_job = client.query(query)
    result = query_job.result()
    for row in result:
        return datetime.strptime(row.latest_date, '%Y-%m-%d').date()  # Convert to date object


def load_data_to_bigquery(df, table_id, schema):
    """Loads the DataFrame into the specified BigQuery table."""
    try:
        job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_APPEND")
        client.load_table_from_dataframe(df, table_id, job_config=job_config).result()
        print(f"Data appended to BigQuery table: {table_id}")
    except Exception as e:
        print(f"Error updating BigQuery: {e}")

# Run the update function
update_bigquery_table() 
