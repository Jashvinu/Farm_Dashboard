from database.data_management.indexes_tables import get_indices_data
from datetime import datetime
import ee
#from database.mongo_connect import collection  # Use absolute import
from database.updatetable import push_data_to_mongo  # Import the function to push data

# Initialize Earth Engine
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

def main():
    # Define the start and end dates
    end_date = ee.Date(datetime.now().strftime('%Y-%m-%d'))  # Today's date
    start_date = end_date.advance(-30, 'day')  # 30 days before today

    print(f"Fetching indices data from {start_date} to {end_date}")

    try:
        # Get the new indices data
        indices_data = get_indices_data(poi, start_date, end_date)

        # Check if data is available
        if not indices_data:
            print("No new data to append.")
            return

        # Insert data into MongoDB
        for data in indices_data:
            push_data_to_mongo(data)
        
        print(f"Inserted {len(indices_data)} records into MongoDB ")
        
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")

if __name__ == "__main__":
    main()