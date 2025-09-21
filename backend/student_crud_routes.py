from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
router = APIRouter(prefix="/students", tags=["student-crud"])
from tools import (
    add_student, get_student, update_student, delete_student, list_students, update_many,
    get_total_students, get_students_by_department,
    get_recent_onboarded_students, get_active_students_last_7_days
)

from enum import Enum
from datetime import datetime, timedelta
from db import student_info_collection, students_attendance_collection


class AddStudentInput(BaseModel):
    name: str
    id: str
    department: str
    email: EmailStr

class UpdateStudentInput(BaseModel):
    new_value: str = None
    currentSemester: int = None
    field: str = None

class Attendance(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"

# ---------------- CRUD Endpoints ----------------

@router.post("/add_student")
async def add_student_endpoint(input_data: AddStudentInput):
    student_info_collection.insert_one({
        "name": input_data.name,
        "studentId": input_data.id,
        "department": input_data.department,
        "email": input_data.email
    })
    return {"message": f"New Record created for student: {input_data.name} with id: {input_data.id}"}


@router.get("/get_student/{student_id}")
async def get_student_endpoint(student_id: str):
    result = student_info_collection.find_one({"studentId": student_id})
    if not result:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    result.pop("_id", None)
    return result


@router.get("/list_students")
async def list_students_endpoint():
    result = student_info_collection.find()
    students = []
    for student in result:
        student.pop("_id", None)
        students.append(student)
    return students


@router.delete("/delete_student/{student_id}")
async def delete_student_endpoint(student_id: str):
    result = student_info_collection.delete_one({"studentId": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Student with ID {student_id} not found")
    return {"message": f"Student with ID {student_id} deleted"}


@router.put("/update_student/{student_id}")
async def update_student_endpoint(student_id: str, data: UpdateStudentInput):
    if data.field and data.currentSemester is not None:
        # update department
        student_info_collection.update_one(
            {"studentId": student_id},
            {"$set": {"department": data.field}}
        )
        return {"message": "Department successfully changed"}

    elif data.new_value:
        # update attendance
        students_attendance_collection.update_one(
            {"studentId": student_id},
            {"$set": {"status": data.new_value}}
        )
        return {"message": "Attendance status updated"}

    return {"message": "Error: No action taken"}


@router.post("/add_many_students")
async def add_many_students_endpoint(students: list[AddStudentInput]):
    student_dicts = [s.dict() for s in students]
    result = student_info_collection.insert_many(student_dicts)
    return {"message": f"{len(result.inserted_ids)} students added successfully."}

# ---------------- Campus Analytics Endpoints ----------------

@router.get("/total_students")
async def total_students_endpoint():
    return {"total": student_info_collection.count_documents({})}


@router.get("/students_by_department/{department}")
async def students_by_department_endpoint(department: str):
    students = student_info_collection.find({"department": department}, {"_id": 0})
    return list(students)


@router.get("/recent_onboarded")
async def recent_onboarded_endpoint(limit: int = 5):
    students = student_info_collection.find({}, {"_id": 0}).sort("enrollmentYear", -1).limit(limit)
    return list(students)


@router.get("/active_last_7_days")
async def active_last_7_days_endpoint():
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    students_cursor = student_info_collection.find(
        {"lastActive": {"$gte": seven_days_ago.isoformat()}},
        {"_id": 0, "studentId": 1, "name": 1, "lastActive": 1}
    )
    return list(students_cursor)