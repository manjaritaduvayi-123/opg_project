from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from .env
MONGO_URI = os.getenv("MONGO_URI=mongodb+srv://manjari:manjari2007@cluster0.pshyzto.mongodb.net/opg_project?retryWrites=true&w=majority")

# Create connection
client = MongoClient(MONGO_URI)

# Select database
db = client["opg_project"]

# Collections
users = db["users"]
reports = db["reports"]

# Optional: test connection
try:
    client.admin.command("ping")
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print("❌ MongoDB Connection Failed:", e)