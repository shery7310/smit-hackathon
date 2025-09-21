import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from fastapi import FastAPI

app = FastAPI()

load_dotenv()

db_url = os.getenv("db_url")
if not db_url:
    raise ValueError("db_url environment variable is not set")

def get_db_client():
    try:
        # Enable SSL and increase timeout for debugging
        client = MongoClient(db_url)
        print(client.server_info())  # Test the connection
        return client
    except Exception as e:
        print("Error connecting to DB:", e)
        return None

db_client = get_db_client()

def get_collection(collection):
    db = db_client.get_database("student_records")
    return db.get_collection(collection)

student_info_collection = get_collection("student_info")
students_attendance_collection = get_collection("students_attendance")
