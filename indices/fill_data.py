from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv
import json 

load_dotenv()
creds_text = os.getenv("CREDS")
creds_json = json.loads(creds_text)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_json
# Define the BigQuery table details
table_id = 'wrkfarm-415118.Major_indices.indices_web'

# Get the current date
current_date = datetime.now().date()

# Calculate the start date for the last 30 days
start_date = current_date - timedelta(days=30)

# Create a BigQuery client
client = bigquery.Client()

# Construct the query to fetch the data for the last 30 days
query = f"""
SELECT
  date,
  ndvi_mean, ndvi_min, ndvi_max,
  gndvi_mean, gndvi_min, gndvi_max,
  ndmi_mean, ndmi_min, ndmi_max,
  dswi_mean, dswi_min, dswi_max,
  ndni_mean, ndni_min, ndni_max,
  evi2_mean, evi2_min, evi2_max
FROM
  {table_id}
WHERE
  date >= '{start_date.strftime('%Y-%m-%d')}' AND
  date <= '{current_date.strftime('%Y-%m-%d')}'
ORDER BY
  date ASC
"""

# Execute the query and fetch the results
query_job = client.query(query)
results = query_job.result()

# Convert the results to a pandas DataFrame
df = results.to_dataframe()

# Create individual DataFrames for each index
ndvi_df = df[['date', 'ndvi_mean', 'ndvi_min', 'ndvi_max']]
gndvi_df = df[['date', 'gndvi_mean', 'gndvi_min', 'gndvi_max']]
ndmi_df = df[['date', 'ndmi_mean', 'ndmi_min', 'ndmi_max']]
dwsi_df = df[['date', 'dswi_mean', 'dswi_min', 'dswi_max']]
ndni_df = df[['date', 'ndni_mean', 'ndni_min', 'ndni_max']]
evi2_df = df[['date', 'evi2_mean', 'evi2_min', 'evi2_max']]
#msavi_df = df[['date', 'msavi_mean', 'msavi_min', 'msavi_max']]

# Print the individual DataFrames
print("NDVI DataFrame:")
print(ndvi_df)
print("\nGNDVI DataFrame:")
print(gndvi_df)
print("\nNDMI DataFrame:")
print(ndmi_df)
print("\nDWSI DataFrame:")
print(dwsi_df)
print("\nNDNI DataFrame:")
print(ndni_df)
print("\nEVI2 DataFrame:")
print(evi2_df)