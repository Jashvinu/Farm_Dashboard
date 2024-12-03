from google.cloud import bigquery
from indexes_tables import get_indices_data
from datetime import datetime, timedelta
import ee
import pandas as pd
import ee_auth
import os
import json
from dotenv import load_dotenv

# Initialize Earth Engine
<<<<<<< HEAD
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "indices/wrkfarm-415118-3652909893e8.json"
=======
load_dotenv()
creds_text = os.getenv("CREDS")
creds_json = json.loads(creds_text)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_json
>>>>>>> 8102a8798cd7714ebdf71206587cc812e6cc2ebf
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
client = bigquery.Client()

# Specify the table details
table_id = 'wrkfarm-415118.Major_indices.indices_web'

current_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))

# Load the existing data from the BigQuery table
table = client.get_table(table_id)
existing_data = client.list_rows(table).to_dataframe()

# Get the latest date from the existing data
latest_date = existing_data['date'].max()  # Assuming 'date' is the column name
latest_date = ee.Date(latest_date)

# Define the start and end dates for the new data
new_start_date = latest_date.advance(5, 'day')  # Start date is 5 days after the latest date
new_end_date = current_date  # End date is the current date
print("New start date:", new_start_date)
print("New end date:", new_end_date)

# Get the new indices data
new_df = get_indices_data(poi, new_start_date, new_end_date)

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