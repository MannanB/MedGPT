from fastapi import FastAPI

from pydantic import BaseModel
from medgpt import MedGPT

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

class Convo(BaseModel):
    query: str
    previous: list[tuple[str, str, float]]

app = FastAPI()
gpt = MedGPT()

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query(req: Convo):
    gpt.query = req.query
    gpt.past_knowledge = req.previous
    
    ans, score, credits = gpt.get_answer()
    return {"response": ans, "score": score, "credits": credits, "query": req.query, "previous": gpt.past_knowledge}