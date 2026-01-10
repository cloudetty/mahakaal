from sqlalchemy.orm import Session
from database import ChatSession, ChatMessage
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

def create_chat_session(db: Session, title: str = None) -> ChatSession:
    """Create a new chat session"""
    if not title:
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    session = ChatSession(title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def save_message(
    db: Session, 
    session_id: int, 
    role: str, 
    content: Optional[str],
    tool_call_id: Optional[str] = None,
    tool_calls: Optional[List[Dict]] = None,
    name: Optional[str] = None
) -> ChatMessage:
    """Save a single message to a chat session"""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        tool_call_id=tool_call_id,
        tool_calls=json.dumps(tool_calls) if tool_calls else None,
        name=name
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Update session's updated_at timestamp
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.updated_at = datetime.utcnow()
        db.commit()
    
    return message

def get_chat_sessions(db: Session, limit: int = 50) -> List[ChatSession]:
    """Get all chat sessions, ordered by most recent"""
    return db.query(ChatSession).order_by(ChatSession.updated_at.desc()).limit(limit).all()

def get_chat_session(db: Session, session_id: int) -> Optional[ChatSession]:
    """Get a specific chat session by ID"""
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_session_messages(db: Session, session_id: int) -> List[ChatMessage]:
    """Get all messages for a specific session"""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()

def delete_chat_session(db: Session, session_id: int) -> bool:
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def update_session_title(db: Session, session_id: int, title: str) -> Optional[ChatSession]:
    """Update the title of a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.title = title
        db.commit()
        db.refresh(session)
        return session
    return None

def message_to_dict(message: ChatMessage) -> Dict[str, Any]:
    """Convert a ChatMessage to a dictionary for API response"""
    result = {
        "role": message.role,
        "content": message.content,
    }
    
    if message.tool_call_id:
        result["tool_call_id"] = message.tool_call_id
    
    if message.tool_calls:
        result["tool_calls"] = json.loads(message.tool_calls)
    
    if message.name:
        result["name"] = message.name
    
    return result

def session_to_dict(session: ChatSession, include_messages: bool = False) -> Dict[str, Any]:
    """Convert a ChatSession to a dictionary for API response"""
    result = {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }
    
    if include_messages:
        result["messages"] = [message_to_dict(msg) for msg in session.messages]
    else:
        result["message_count"] = len(session.messages)
    
    return result
