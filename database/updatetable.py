from pymongo import MongoClient


def push_data_to_mongo(data):
    global collection
    # Connect to MongoDB
    # Update with your MongoDB URI
    uri = "mongodb+srv://jashvinuy:fnHilZSUgh76p3le@farmdata.m122q.mongodb.net/?retryWrites=true&w=majority&appName=FarmData"

    # Create a new client and connect to the server
    client = MongoClient(uri)
    db = client['FamDashboard']  # Replace with your database name
    collection = db['indices']  # Replace with your collection name

    # Insert data into the collection
    collection.insert_one(data)  # Assuming 'data' is a dictionary
