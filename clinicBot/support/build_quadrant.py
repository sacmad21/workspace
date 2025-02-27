import quadrant
import json
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
QUADRANT_API_KEY = os.getenv("QUADRANT_API_KEY")

# Initialize Quadrant Client
quadrant_client = quadrant.Client(api_key=QUADRANT_API_KEY)
collection = quadrant_client.create_collection("medication_info")

# Load Data
with open("medication_data.json", "r") as f:
    data = json.load(f)

# Index Data
for record in data:
    collection.insert(record["text"], metadata={"source": record["source"]})

print("Quadrant database successfully built!")
