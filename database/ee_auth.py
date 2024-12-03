import ee
from dotenv import load_dotenv
import os 
load_dotenv()
project_id = os.getenv("EE_PROJECT")
try:
    ee.Initialize(project=project_id)
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project=project_id)
