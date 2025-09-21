from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["analytics"])
from datetime import datetime, timedelta
from collections import Counter

from db import student_info_collection, students_attendance_collection


@router.get("/students/stats")
async def student_statistics():
    # Total students
    total_students = student_info_collection.count_documents({})

    # Students by department
    students = student_info_collection.find({}, {"_id": 0, "department": 1})
    departments = [s.get("department", "Unknown") for s in students]
    students_by_department = dict(Counter(departments))

    # Recently onboarded (last 5 students)
    recent_students = list(student_info_collection.find({}, {"_id": 0}).sort("enrollmentYear", -1).limit(5))

    # Active in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_students = list(student_info_collection.find(
        {"lastActive": {"$gte": seven_days_ago.isoformat()}},
        {"_id": 0, "studentId": 1, "name": 1, "lastActive": 1}
    ))

    # Prepare JSON response
    stats = {
        "total_students": total_students,
        "students_by_department": students_by_department,
        "recent_onboarded": recent_students,
        "active_last_7_days": active_students
    }

    return stats

