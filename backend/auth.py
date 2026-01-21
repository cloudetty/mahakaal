import os
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

router = APIRouter(prefix="/auth", tags=["auth"])

# Configuration
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Use environment variables for redirects, default to localhost for development
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@router.get("/login")
def login():
    """
    Initiates the OAuth2 flow.
    Returns the authorization URL for the user to visit.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        raise HTTPException(status_code=500, detail="credentials.json not found on server.")

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return {"url": authorization_url}

@router.get("/callback")
def callback(code: str):
    """
    Handles the callback from Google. 
    Exchanges the code for tokens and saves them to token.json.
    """
    try:
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Save credentials
        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())
            
        # Redirect back to the frontend app
        return RedirectResponse(FRONTEND_URL)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/status")
def status():
    """
    Checks if a valid token.json exists.
    """
    if not os.path.exists(TOKEN_FILE):
        return {"authenticated": False}
        
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        return {"authenticated": creds.valid}
    except Exception:
        return {"authenticated": False}
