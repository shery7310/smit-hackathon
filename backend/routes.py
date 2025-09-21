from fastapi import APIRouter
from tools import stream_from_llm, non_stream_llm # my own functions
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from fastapi.responses import StreamingResponse, Response, JSONResponse, PlainTextResponse
from agents import stream_from_agent
import json

router = APIRouter(prefix="/chat", tags=["chat"])
                        # langgraph agents do not support streaming as of yet so using llm here
@router.get("/stream") # this is only supports streaming with LLM rather than agent
async def stream_llm(query: str):
    response = StreamingResponse(stream_from_llm(query, system_query="You are helpful Assistant"),
                                 media_type="text/plain")
    return response

@router.get("/nonstream") # This is not streaming response from LLM instead of agent
async def non_stream(query: str):
    response = Response(non_stream_llm(query, system_query="You are helpful Assistant"), media_type="text/plain")
    return response

"""
Example Prompt
prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful assistant that answer's appropriately",
        ),
        ("human", "{input}"),
    ]
)

Sample Endpoint for Non Streaming: 
http://127.0.0.1:8000/chat/nonstream?query=What%20is%20python%20language
Sample Endpoint for Streaming:
http://127.0.0.1:8000/chat/stream?query=What%20is%20python%20language
Sample Endpoint for Agent:
http://127.0.0.1:8000/chat/agent?query=Hey%20show%20data%20of%20all%20students
"""

# two more endpoints required
# /analytics
# /students
# (Optional) Next.js dashboard.


"""
1. FastAPI backend with:
    - /chat (normal chat)
    - /chat/stream (streaming chat)
    - /analytics (JSON stats)
    - /students (CRUD endpoints)
2. Agent with memory & tool calls
3. Postman collection testing all endpoints
4. Analytics features (total students, dept breakdown, etc.)
5. (Optional) Next.js dashboard

Submit: https://forms.gle/Q9z8vuwdZF5erPSq5
"""

@router.get("/agent")
async def non_stream(query: str):
    text = stream_from_agent(query)
    return PlainTextResponse(content=text)