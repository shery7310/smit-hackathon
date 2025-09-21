import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.prompts import PromptTemplate
from typing import Generator

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uuid

from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.chat_models import ChatOllama
from langchain_ollama.llms import OllamaLLM

#### DB Logic
import os
from dotenv import load_dotenv
load_dotenv()
from pymongo.mongo_client import MongoClient

db_url = os.getenv("db_url")

def get_db_client():
    try:
        client = MongoClient(db_url)
        print("Connected to MongoDB")
        return client
    except Exception as e:
        print("Error connecting to DB:", e)
    return None

db_client = get_db_client()

def students(collection):
    db = db_client.get_database("student_data")
    return db.get_collection(collection)

def student_attendance(collection):
    db = db_client.get_database("student_data")
    return db.get_collection(collection)

import time
students_attendance_collection = student_attendance("student_attendance")
students_collection = students("students")
print(students_collection.find_one({"studentId": "8721"}))

# memory = ConversationBufferMemory(return_messages=True) # this can blow out of context after a while
#
# # memory = ConversationSummaryBufferMemory(
# #     llm=ChatMistralAI(model=os.getenv("mistral_model_name"), api_key=api_key),
# #     return_messages=True,
# #     max_token_limit=10000  # you can adjust this
# # )
#
# # memory = ConversationSummaryBufferMemory(
# #     llm=ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"),
# #                                google_api_key=os.getenv("gemini")),
# #     return_messages=True,
# #     max_token_limit=10000  # you can adjust this
# # )
#
# def stream_from_llm(query: str, system_query: str,
#                     thread_id: str = None) -> Generator[str, None, None]:
#     """
#     This is yielding because it keeps yielding an LLM response as it comes and where it is called
#     a for loop is iterating
#     """
#
#     if thread_id is None:
#         thread_id = f"thread_{uuid.uuid4().hex[:8]}"
#
#     llm = ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"), streaming= True, google_api_key= os.getenv("gemini"))
#     """We use chat prompt template because we are basically using chat models"""
#
#      # ConversationSummaryBufferMemory
#     full_ai_response = ""
#
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "{system_query}"),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{query}")
#     ])
#
#     chain = prompt | llm
#     response = chain.stream({"system_query":system_query,
#                              "query": query,
#                              "history": memory.load_memory_variables({})["history"]})
#     for chunk in response:
#         full_ai_response += chunk.content
#         yield chunk.content
#
#     human_message = HumanMessage(content=query)
#     ai_message = AIMessage(content=full_ai_response)
#     memory.save_context(
#         {"input": query},
#         {"output": full_ai_response}
#     )
#     print("Updated memory:", memory.chat_memory)
#
#
#
# def stream_full_response_from_llm(query: str, system_query: str):
#     """This actually emulates how streaming actually works"""
#     llm = ChatGoogleGenerativeAI(model= os.getenv("gemini"), streaming=True, google_api_key = api_key)
#
#     """We use chat prompt template because we are basically using chat models"""
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "{system_query}"),
#         ("human", "{query}")]
#     )
#
#     chain = prompt | llm
#     full_response = ""  # Optional: accumulate if you want final text
#     for chunk in chain.stream({"system_query": system_query, "query": query}):
#         # Each `chunk` is usually an AIMessageChunk
#         content = chunk.content
#         full_response += content  # builds full response
#     return full_response
#
#
# def non_stream_llm(query: str, system_query: str, thread_id: str = None):
#
#     if thread_id is None:
#         thread_id =  f"thread_{uuid.uuid4().hex[:8]}"
#     llm = ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"), streaming=False, google_api_key=os.getenv("gemini"))
#     llm = ChatGoogleGenerativeAI(model=os.getenv("mistral_mode_name"), streaming=False,
#                                  google_api_key=os.getenv("mistral"))
#
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", "{system_query}"),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{query}")
#     ])
#
#     chain = prompt | llm
#
#     response = chain.invoke({"system_query": system_query,
#                              "query": query,
#                              "history": memory.load_memory_variables({})["history"]})
#
#     ai_response = response.content
#     human_message = HumanMessage(content=query)
#     ai_message = AIMessage(content=str(ai_response))
#     memory.save_context(
#         {"input": query},
#         {"output": ai_response}
#     )
#     print("Updated memory:", memory.chat_memory)
#     return response.content
#
#
# """
# response = {'messages':
#                 [HumanMessage(content='What is the weather in Faisalabad?',
#                               additional_kwargs={}, response_metadata={},
#                               id='cb061e78-9f7a-4de1-822c-ead93594ad09'),
#                 AIMessage(content='',
#                            additional_kwargs={'function_call': {'name': 'get_weather', 'arguments': '{"city": "Faisalabad"}'}},
#                            response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': []},
#                            id='run--2140df9d-d1fd-4bd4-b742-e57f116757dc-0',
#                            tool_calls=[{'name': 'get_weather', 'args': {'city': 'Faisalabad'},
#                                         'id': '9a246a82-13b8-4073-9816-5bb941ee4e96', 'type': 'tool_call'}],
#                            usage_metadata={'input_tokens': 53, 'output_tokens': 60, 'total_tokens': 113, 'input_token_details': {'cache_read': 0},
#                                            'output_token_details': {'reasoning': 43}}),
#                 ToolMessage(content="It's always sunny in Faisalabad!",
#                 name='get_weather', id='ea07cf95-c3bd-41e8-a5a1-b974fe55720e',
#                 tool_call_id='9a246a82-13b8-4073-9816-5bb941ee4e96'),
#                 AIMessage(content="It's always sunny in Faisalabad!",
#                 additional_kwargs={}, response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-2.5-flash', 'safety_ratings': []},
#                 id='run--91d752ed-1910-403d-9711-b86fd0f3ba86-0', usage_metadata={'input_tokens': 93, 'output_tokens': 9, 'total_tokens': 102, 'input_token_details': {'cache_read': 0}})]
#                 }
#
# """
#

# def add_student(name, id, department, email):
#     pass
# def update_student(id, field, new_value):
#     pass
# def delete_student(id):
#     pass
# def list_students():
#     pass
#
# def update_many():
#     pass

print(students_collection.find_one({"studentId": "8721"}))
print(students_collection.find_one({"studentId": 8721}))
print(students_collection.find_one())

#
# print(get_student("8721"))
