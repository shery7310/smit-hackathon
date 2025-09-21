from tools import add_student, get_student, update_student, delete_student, list_students, update_many

tools = [add_student, get_student, update_student, delete_student, list_students, update_many]

from tools import get_total_students, get_students_by_department, get_recent_onboarded_students, get_active_students_last_7_days

campus_analytics_tools = [get_total_students, get_students_by_department, get_recent_onboarded_students,
    get_active_students_last_7_days
]

tools = tools + campus_analytics_tools

from langchain.schema import HumanMessage, AIMessage

from langchain.schema import AIMessage

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
load_dotenv()

from tools import stream_from_llm

llm = ChatGoogleGenerativeAI(model=os.getenv("gemini-2.5-flash"),
                             google_api_key = os.getenv("gemini"), streaming = True)

agent = create_react_agent(
    model=llm,
    tools= tools,
    prompt="You are helpful assistant")

def stream_from_agent(query: str) -> str:
    """
    Call the LangGraph agent and return only the AI's response as a string.
    """
    response = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    # Extract the AIMessage content
    ai_texts = [
        msg.content for msg in response.get("messages", [])
        if isinstance(msg, AIMessage)
    ]

    # Join multiple AI messages if there are any
    return "\n".join(ai_texts) if ai_texts else "No response from agent."
