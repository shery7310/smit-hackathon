import os
import pprint
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Generator

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid
import json
from langchain.memory import ConversationSummaryBufferMemory

from bson import ObjectId
from pydantic import BaseModel, EmailStr
from enum import Enum
from langchain_core.tools import tool
import datetime
load_dotenv()

from db import student_info_collection, students_attendance_collection


memory = ConversationBufferMemory(return_messages=True) # this can blow out of context after a while

# memory = ConversationSummaryBufferMemory(
#     llm=ChatMistralAI(model=os.getenv("mistral_model_name"), api_key=api_key),
#     return_messages=True,
#     max_token_limit=10000  # you can adjust this
# )
#
# memory = ConversationSummaryBufferMemory(
#     llm=ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"),
#                                google_api_key=os.getenv("gemini")),
#     return_messages=True,
#     max_token_limit=10000  # you can adjust this
# )

def stream_from_llm(query: str, system_query: str,
                    thread_id: str = None) -> Generator[str, None, None]:
    """
    This is yielding because it keeps yielding an LLM response as it comes and where it is called
    a for loop is iterating
    """

    if thread_id is None:
        thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    llm = ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"), streaming= True, google_api_key= os.getenv("gemini"))
    """We use chat prompt template because we are basically using chat models"""

     # ConversationSummaryBufferMemory
    full_ai_response = ""

    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_query}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{query}")
    ])

    chain = prompt | llm
    response = chain.stream({"system_query":system_query,
                             "query": query,
                             "history": memory.load_memory_variables({})["history"]})
    for chunk in response:
        full_ai_response += chunk.content
        yield chunk.content

    human_message = HumanMessage(content=query)
    ai_message = AIMessage(content=full_ai_response)
    memory.save_context(
        {"input": query},
        {"output": full_ai_response}
    )
    print("Updated memory:", memory.chat_memory)



def stream_full_response_from_llm(query: str, system_query: str):
    """This actually emulates how streaming actually works"""
    llm = ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"), streaming= True, google_api_key= os.getenv("gemini"))

    """We use chat prompt template because we are basically using chat models"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_query}"),
        ("human", "{query}")]
    )

    chain = prompt | llm
    full_response = ""  # Optional: accumulate if you want final text
    for chunk in chain.stream({"system_query": system_query, "query": query}):
        # Each `chunk` is usually an AIMessageChunk
        content = chunk.content
        full_response += content  # builds full response
    return full_response


def non_stream_llm(query: str, system_query: str, thread_id: str = None):

    if thread_id is None:
        thread_id =  f"thread_{uuid.uuid4().hex[:8]}"
    llm = ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"), streaming=False, google_api_key=os.getenv("gemini"))

    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_query}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{query}")
    ])

    chain = prompt | llm

    response = chain.invoke({"system_query": system_query,
                             "query": query,
                             "history": memory.load_memory_variables({})["history"]})

    ai_response = response.content
    human_message = HumanMessage(content=query)
    ai_message = AIMessage(content=str(ai_response))
    memory.save_context(
        {"input": query},
        {"output": ai_response}
    )
    print("Updated memory:", memory.chat_memory)
    return response.content


"""
response = {'messages':
                [HumanMessage(content='What is the weather in Faisalabad?',
                              additional_kwargs={}, response_metadata={},
                              id='cb061e78-9f7a-4de1-822c-ead93594ad09'),
                AIMessage(content='',
                           additional_kwargs={'function_call': {'name': 'get_weather', 'arguments': '{"city": "Faisalabad"}'}},
                           response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': []},
                           id='run--2140df9d-d1fd-4bd4-b742-e57f116757dc-0',
                           tool_calls=[{'name': 'get_weather', 'args': {'city': 'Faisalabad'},
                                        'id': '9a246a82-13b8-4073-9816-5bb941ee4e96', 'type': 'tool_call'}],
                           usage_metadata={'input_tokens': 53, 'output_tokens': 60, 'total_tokens': 113, 'input_token_details': {'cache_read': 0},
                                           'output_token_details': {'reasoning': 43}}),
                ToolMessage(content="It's always sunny in Faisalabad!",
                name='get_weather', id='ea07cf95-c3bd-41e8-a5a1-b974fe55720e',
                tool_call_id='9a246a82-13b8-4073-9816-5bb941ee4e96'),
                AIMessage(content="It's always sunny in Faisalabad!",
                additional_kwargs={}, response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': []},
                id='run--91d752ed-1910-403d-9711-b86fd0f3ba86-0', usage_metadata={'input_tokens': 93, 'output_tokens': 9, 'total_tokens': 102, 'input_token_details': {'cache_read': 0}})]
                }

"""

@tool
def get_student(id: str):
    """
        Retrieve a student record by student ID.

        Args:
            id (str): The unique student ID.

        Returns:
            dict: A dictionary containing student information such as name,
                  department, email, GPA, semester, etc.
                  If the student is not found, returns {"error": "..."}.
        """
    result = student_info_collection.find_one({"studentId": id})
    if result is None:
        return {"error": f"Student with ID {id} not found."}

    if "_id" in result:
        result["_id"] = str(result["_id"])

    # Remove _id field before returning
    result.pop("_id", None)

    return result

@tool
def list_students() -> list[dict]:
    """
    Retrieve the last 10 student records from the database.

    Use this tool when the user requests to list all students.

    Returns:
        list[dict]: A list of up to 10 student records, where each record
                    contains fields such as name, department, email, GPA,
                    and semester.
    """
    result = student_info_collection.find()
    students = []
    for student in result:
        student["_id"] = str(student["_id"])
        student.pop("_id", None)
        students.append(student)
    # return json.dumps(students[0]) # wlll list all students
    # return json.dumps(students[-10:], indent=2) # will list last 10 students
    return students

@tool
def delete_student(id: str):
    """
    Delete a student record by student ID.

    Use this tool only when the user explicitly requests to remove a student.

    Args:
        id (str): The unique student ID.

    Returns:
        dict: A confirmation message, e.g. {"message": "Student with ID <id> deleted."}.
              If no record is found, returns {"error": "Student with ID <id> not found."}.
    """
    query_filter = {"studentId": id}
    result = student_info_collection.delete_one(query_filter)
    return {"message": f"Student with {id} Record Deleted"}

# print(delete_student("6622")) # 8721 6622

class AddStudentInput(BaseModel):
    name: str
    id: str
    department: str
    email: EmailStr

@tool
def add_student(input_data: AddStudentInput):
    """
    Add a new student to the database.

    Use this tool only when the user explicitly requests to add one student at a time.

    Args:
        input_data (AddStudentInput): An object containing the student's details:
            - name (str): Full name of the student.
            - id (str): Unique student ID.
            - department (str): Department name.
            - email (str): Student email address.

    Example:
        AddStudentInput(
            name="Hameed Khan",
            id="8721",
            department="Computing",
            email="smit_thanks@gg.com"
        )

    Returns:
        dict: The inserted student record with all provided fields.
    """

    student_info_collection.insert_one({"name": input_data.name, "studentId": input_data.id,
                                        "department": input_data.department, "email": input_data.email})
    return {"message": f"New Record created for student: {input_data.name} with id: {input_data.id}"}



@tool
class Attendance(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"

@tool
def update_student(
    id: str,
    new_value: str = None,
    currentSemester: int = None,
    field: str = None
) -> dict:
    """
    Update a specific field of a student record.

    Use this tool for:
      - Changing department → allowed only if currentSemester == 1.
      - Updating attendance → set new_value to "present" or "absent".
      - Other updates → specify the field name and new_value.

    Args:
        id (str): The unique student ID.
        new_value (str | None): The new value for the field (e.g., "present", "absent").
        currentSemester (int | None): Current semester, required if updating department.
        field (str | None): The field to update (e.g., "department").

    Returns:
        dict: A confirmation message if the update was successful,
              or {"message": "Error: No action taken"} if no update was applied.
    """
    if field is not None and currentSemester is not None:
        query_filter = {"studentId": id}
        update_operation = {"$set": {"department": field}}
        result = student_info_collection.update_one(query_filter, update_operation)
        return {"message": "Department successfully changed"}

    elif new_value is not None:
        query_filter = {"studentId": id}
        update_operation = {"$set": {"status": new_value}}
        result = students_attendance_collection.update_one(query_filter, update_operation)
        return {"message": "Attendance status updated"}

    return {"message": "Error: No action taken"}

@tool
def update_many(students: list[dict]) -> dict:
    """
    Add several students to the database at once.

    Use this tool only when the user provides multiple student records.
    Each record must include: 'studentId', 'name', 'department', and 'email'.
    Optional fields: 'age', 'gpa', 'graduationYear', 'enrollmentYear',
    'currentSemester', 'lastActive'.

    Args:
        students (list[dict]): A list of student dictionaries.

    Example:
        [
            {
                "studentId": "8721",
                "name": "Michael Kim",
                "department": "Computer Science",
                "email": "michael@example.com"
            },
            {
                "studentId": "8722",
                "name": "Sarah Lee",
                "department": "Mathematics",
                "email": "sarah@example.com"
            },
            {
                "studentId": "8723",
                "name": "James Chen",
                "department": "Physics",
                "email": "james@example.com"
            }
        ]

    Returns:
        dict: A confirmation message with the number of inserted students,
              or {"error": "..."} if the operation fails.
    """
    result = student_info_collection.insert_many(students)
    return {"message": f"{len(result.inserted_ids)} students added successfully."}

# Campus Analytics Part

@tool()
def get_total_students() -> int:
    """
    Return the total number of students in the database.
    Use this when you need the overall student count.
    """
    return student_info_collection.count_documents({})

@tool
def get_students_by_department(department: str) -> list:
    """
    Return all students in the given department.
    Input: department name (string).
    Use this when asked about students in a specific department.
    """
    students = student_info_collection.find({"department": department}, {"_id": 0})
    return list(students)

@tool
def get_recent_onboarded_students(limit: int = 5) -> list:
    """
    Return the most recently onboarded students.
    Input: optional limit (integer, default = 5).
    Use this when asked for the latest enrolled students.
    """
    students = student_info_collection.find({}, {"_id": 0}).sort("enrollmentYear", -1).limit(limit)
    return list(students)


from langchain_core.tools import tool
from datetime import datetime, timedelta


@tool
def get_active_students_last_7_days() -> list:
    """
    Returns a list of students who were active in the last 7 days.

    Output format: list of dictionaries with keys:
    - studentId
    - name
    - lastActive (ISO string)

    Use this tool when asked for recently active students.
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    # Query students whose lastActive is within last 7 days
    students_cursor = student_info_collection.find(
        {"lastActive": {"$gte": seven_days_ago.isoformat()}},
        {"_id": 0, "studentId": 1, "name": 1, "lastActive": 1}
    )

    return list(students_cursor)


