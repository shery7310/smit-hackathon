import json
from backend.db import student_info_collection, students_attendance_collection

def insert_attendance():
    with open("attendance.json") as f:
        attendance_data = json.load(f)

    # Bulk insert
    if attendance_data:
        result = students_attendance_collection.insert_many(attendance_data)
        print(f"Inserted {len(result.inserted_ids)} attendance records.")
    else:
        print("No attendance data found.")


with open("student_data.json") as f:
    student_data = json.load(f)


def update_many():
    student_info_collection.insert_many(student_data)
    print("Added Students")

update_many()

insert_attendance()

