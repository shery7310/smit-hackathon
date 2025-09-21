import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def insert_attendance():
    mongo_uri = os.getenv("db_url")
    client = MongoClient(mongo_uri)
    db = client.get_database("student_data")
    collection = db.get_collection("student_attendance")

    with open("attendance.json") as f:
        attendance_data = json.load(f)

    # Bulk insert
    if attendance_data:
        result = collection.insert_many(attendance_data)
        print(f"Inserted {len(result.inserted_ids)} attendance records.")
    else:
        print("No attendance data found.")

if __name__ == "__main__":
    insert_attendance()

