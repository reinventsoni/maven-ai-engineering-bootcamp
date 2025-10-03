from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI
from groq import Groq
from google import genai
from google.genai.types import GenerateContentConfig
from src.api.core.config import config

import uvicorn
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_llm(provider, model_name, messages, temperature=0.5, max_output_tokens=500):
    if provider == "OpenAI":
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    elif provider == "Groq":
        client = Groq(api_key=config.GROQ_API_KEY)
    else:
        client = genai.Client(api_key=config.GOOGLE_API_KEY)

    if provider == "Google":
        return client.models.generate_content(
            model=model_name,
            contents=[message["content"] for message in messages],
            config = GenerateContentConfig(temperature=temperature, max_output_tokens=max_output_tokens)
            ).text
    else:
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_output_tokens
        ).choices[0].message.content


class ChatRequest(BaseModel):
    provider: str
    model_name: str
    messages: list[dict]
    temperature: float
    max_output_tokens: int

class ChatResponse(BaseModel):
    message: str


app = FastAPI()
@app.post("/chat")
def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    result = run_llm(payload.provider, payload.model_name, payload.messages, payload.temperature, payload.max_output_tokens)
    return ChatResponse(message=result)
