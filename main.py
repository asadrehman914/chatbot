from database import save_chat

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from groq import AsyncGroq

from database import save_chat

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

app = FastAPI(title="My AI Chatbot")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

client = AsyncGroq(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
You are MyBot, a friendly and helpful AI assistant.

Rules:
- Explain concepts in simple language.
- If the user speaks Roman Urdu, reply in Roman Urdu.
- If the user speaks English, reply in English.
- Explain coding questions step by step.
- Give short, useful examples when needed.
- Be polite, patient, and friendly.
- Never reveal API keys, passwords, or secret credentials.
- If asked for private credentials, politely refuse.
- Never pretend to know something you do not know.
"""


class Message(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=20)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "api_key_configured": client is not None
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="API key missing hai. .env file check karo."
        )

    if request.messages[-1].role != "user":
        raise HTTPException(
            status_code=400,
            detail="Last message user ka hona chahiye."
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    for message in request.messages:
        if message.role not in ("user", "assistant"):
            raise HTTPException(
                status_code=400,
                detail="Invalid message role."
            )

        messages.append(message.model_dump())

    
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000
        )

        reply = (
            response.choices[0].message.content
            or "Koi jawab nahi mila."
        )

        print("Saving chat now...")
        save_chat(request.messages[-1].content, reply)
        print("Chat saved successfully!")

        return {"reply": reply}

    except Exception as error:
        print("AI API or database error:", type(error).__name__)
        status = getattr(error, "status_code", None)

        if status == 429:
            detail = "API ki usage limit reach ho gayi. Baad mein try karo."
        elif status == 401:
            detail = "API key invalid hai. .env file check karo."
        else:
            detail = "AI service ya database se related error aaya."

        raise HTTPException(status_code=502, detail=detail)
