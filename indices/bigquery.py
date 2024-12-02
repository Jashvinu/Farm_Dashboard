from google.cloud import bigquery
from indexes_tables import get_indices_data
from datetime import datetime, timedelta
import ee
import pandas as pd
import ee_auth
import os
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

# Define the start and end dates for the last 30 days
end_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))
print("End date:", end_date)
print(type(end_date))
start_date = end_date.advance(-30, 'day')

# Create a BigQuery client
client = bigquery.Client()

# Specify the table details
table_id = 'wrkfarm-415118.Major_indices.indices_web'

# Get the latest date from the BigQuery table
query = f"SELECT MAX(date) AS latest_date FROM `{table_id}`"
query_job = client.query(query)
result = query_job.result()
for row in result:
    latest_date = row.latest_date
latest_date = datetime.strptime(latest_date, '%Y-%m-%d')

print("Latest date in the table:", latest_date)
print(type(latest_date))
current_date = datetime.now()
print("Current date:", current_date)
print(type(current_date))
# Convert the latest date string to a datetime.datetime object

# Get the current date as an ee.Date object

print("Current date:", current_date)
# Check if the latest date is older than the current date
if latest_date < current_date:
    current_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))
    latest_date = ee.Date(latest_date.strftime('%Y-%m-%d'))
    # Define the start and end dates for the new data
    new_start_date = ee.Date(latest_date.advance(1, 'day'))
    new_end_date = current_date
    print("New start date:", new_start_date)
    print("New end date:", new_end_date)

    # Get the new indices data

    new_df = get_indices_data(poi, new_start_date, new_end_date)

    # Load the existing data from the BigQuery table
    table = client.get_table(table_id)
    existing_data = client.list_rows(table).to_dataframe()

    # Concatenate the new and existing data
    df = new_df
    print(df)
    if df.empty:
        print("No new data to append.")
        exit()

    # Upload the updated DataFrame to BigQuery
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

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table, exists_ok=True)
    #job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    #client.load_table_from_dataframe(df, table_id, job_config=job_config).result()
    job_config = bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_APPEND") 
    print(client.load_table_from_dataframe(df, table_id, job_config=job_config).result())
    print(f"Data appended to BigQuery table: {table_id}")
else:
    print("The latest date in the table is already up-to-date.")