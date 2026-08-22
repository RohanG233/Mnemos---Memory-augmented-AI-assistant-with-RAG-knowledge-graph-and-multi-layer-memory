from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow the frontend (served from a different origin/port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten this in real projects
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class GreetRequest(BaseModel):
    name: str

# Response body schema
class GreetResponse(BaseModel):
    message: str

@app.post("/greet", response_model=GreetResponse)
def greet(payload: GreetRequest):
    return GreetResponse(message=f"Hello, {payload.name}! 👋")