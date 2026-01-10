from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from agent import run_agent_stream
from auth import router as auth_router
from database import init_db, get_db
from chat_storage import (
    create_chat_session, save_message, get_chat_sessions,
    get_chat_session, get_session_messages, delete_chat_session,
    update_session_title, session_to_dict, message_to_dict
)

app = FastAPI(title="Mahakaal API")
app.include_router(auth_router)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

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

# ===== Chat Session Management Endpoints =====

class CreateSessionRequest(BaseModel):
    title: Optional[str] = None

class UpdateSessionRequest(BaseModel):
    title: str

class SaveMessageRequest(BaseModel):
    session_id: int
    role: str
    content: Optional[str]
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    name: Optional[str] = None

@app.post("/chat/sessions")
def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Create a new chat session"""
    session = create_chat_session(db, title=request.title)
    return session_to_dict(session)

@app.get("/chat/sessions")
def list_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    sessions = get_chat_sessions(db)
    return [session_to_dict(s) for s in sessions]

@app.get("/chat/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific chat session with all messages"""
    session = get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_to_dict(session, include_messages=True)

@app.delete("/chat/sessions/{session_id}")
def remove_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session"""
    success = delete_chat_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}

@app.patch("/chat/sessions/{session_id}")
def update_session(session_id: int, request: UpdateSessionRequest, db: Session = Depends(get_db)):
    """Update a chat session title"""
    session = update_session_title(db, session_id, request.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_to_dict(session)

@app.post("/chat/messages")
def add_message(request: SaveMessageRequest, db: Session = Depends(get_db)):
    """Save a message to a chat session"""
    message = save_message(
        db,
        session_id=request.session_id,
        role=request.role,
        content=request.content,
        tool_call_id=request.tool_call_id,
        tool_calls=request.tool_calls,
        name=request.name
    )
    return {"status": "saved", "message_id": message.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
