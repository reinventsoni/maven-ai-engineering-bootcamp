from fastapi import FastAPI, Request
from pydantic import BaseModel

from openai import OpenAI
from google import genai
from groq import Groq
from src.api.core.config import config

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_llm(provider, model_name, messages, max_tokens=500):
    if provider == "OpenAI":
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    elif provider == "Google":
        client = genai.Client(api_key=config.GOOGLE_API_KEY)
    else:
        client = Groq(api_key=config.GROQ_API_KEY)
    
    if provider == "Google":
        response = client.models.generate_content(
            model= model_name,
            contents=[message["content"] for message in messages])
        return response.text    
    else:
        response = client.chat.completions.create(
            model= model_name,
            messages=messages,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

class ChatRequest(BaseModel):
    provider: str
    model_name: str
    messages: list[dict]


class ChatResponse(BaseModel):
    message: str


app = FastAPI()
@app.post("/chat")
def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    result = run_llm(payload.provider, payload.model_name, payload.messages, max_tokens=500)
    return ChatResponse(message=result)

