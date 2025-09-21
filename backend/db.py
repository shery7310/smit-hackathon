import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from fastapi import FastAPI

app = FastAPI()

# Load environment variables
load_dotenv()

# Database Logic
db_url = os.getenv("db_url")
if not db_url:
    raise ValueError("db_url environment variable is not set")

def get_db_client():
    try:
        # Enable SSL and increase timeout for debugging
        client = MongoClient(
            db_url,
            serverSelectionTimeoutMS=10000,  # 10 seconds timeout
            ssl=True
        )
        client.server_info()  # Test the connection
        print("Connected to MongoDB")
        return client
    except ServerSelectionTimeoutError as e:
        print("Server selection timeout:", e)
        return None
    except Exception as e:
        print("Error connecting to DB:", e)
        return None

db_client = get_db_client()

def students(collection):
    if db_client is None:
        return None
    db = db_client.get_database("student_data")
    return db.get_collection(collection)

students_collection = students("students")

@app.patch("/update_student")
def change_student_status(student_id: str):
    if students_collection is None:
        return {"error": "Database connection failed"}
    students_by_id = students_collection.find({"studentId": student_id})
    student_list = []
    for student in students_by_id:
        student["_id"] = str(student["_id"])  # Convert ObjectId to string
        student_list.append(student)
    return student_list if student_list else {"message": "No students found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)