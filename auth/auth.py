from fastapi import FastAPI, HTTPException, Header
from typing import Optional
import os

app = FastAPI()

@app.get("/auth")
async def authenticate(authorization: Optional[str] = Header(None)):
    valid_token = os.getenv("VALID_TOKEN")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token provided")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        if token != valid_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"authenticated": True}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")