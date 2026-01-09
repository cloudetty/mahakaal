from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi.responses import StreamingResponse
from agent import run_agent_stream
from auth import router as auth_router

app = FastAPI(title="Mahakaal API")
app.include_router(auth_router)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]

@app.get("/")
def read_root():
    return {"message": "Mahakaal Agent is Online. Time flows."}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Streaming endpoint.
    Client receives line-delimited JSON events.
    """
    return StreamingResponse(
        run_agent_stream(request.messages), 
        media_type="application/x-ndjson"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
