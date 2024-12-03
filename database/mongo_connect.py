from pymongo import MongoClient

# Your MongoDB connection URI
uri = "mongodb+srv://jashvinuy:fnHilZSUgh76p3le@farmdata.m122q.mongodb.net/?retryWrites=true&w=majority&appName=FarmData"

# Create a new client and connect to the server
client = MongoClient(uri)

# Access the FamDashboard database
db = client['FamDashboard']

# Access the indices collection
collection = db['indices']

# Example: Perform a simple query to fetch one document
document = collection.find_one()  # Fetch one document from the collection
print(document)

