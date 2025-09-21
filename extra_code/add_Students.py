# from pymongo import MongoClient
# import json
# import os
# from dotenv import load_dotenv
# load_dotenv()
#
# # This bulk adds student_data.json to students collection
#
# with open("student_data.json") as f:
#     student_data = json.load(f)
#
#
# def update_many(student_data):
#     client = MongoClient(os.getenv("db_url"))
#     db = client["student_data"]
#     collection = db["students"]
#
#     # for each student, update by studentId
#     for student in student_data:
#         collection.update_one(
#             {"studentId": student["studentId"]},
#             {"$set": student},
#             upsert=True
#         )
#
#     print("Update completed.")
#
# update_many(student_data)