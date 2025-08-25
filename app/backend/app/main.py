import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.agent import create_agent

from loguru import logger as log

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(title="Gemini Weather & Activities (Chat)")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

agent = create_agent()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    messages: List[Message]

@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id

    # Push new human message into graph
    result = await agent.ainvoke({"messages": [m.dict() for m in req.messages]})

    # The graph agent usually appends AI reply to `messages`
    reply_msg = result["messages"][-1].content

    return {"response": reply_msg}

