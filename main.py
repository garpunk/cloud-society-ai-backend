from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.get("/")
def home():
    return {"message": "AI server is running"}

@app.post("/chat")
def chat(request: ChatRequest):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:mini",
            "prompt": request.prompt,
            "stream": False
        }
    )

    data = response.json()

    return {
        "response": data.get("response", "No response generated")
    }