import logging
import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# allow cors
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/auth/validate")
async def authenticate(authorization: Optional[str] = Header(None)):
    valid_token = os.getenv("VALID_TOKEN")

    if not valid_token:
        logger.error("VALID_TOKEN environment variable not set")
        raise HTTPException(
            status_code=500, detail="Authentication configuration error"
        )

    if not authorization:
        logger.warning("No authorization token provided")
        raise HTTPException(status_code=401, detail="No authorization token provided")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            logger.warning(f"Invalid authentication scheme: {scheme}")
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        if token != valid_token:
            logger.warning("Invalid token attempt")
            raise HTTPException(status_code=401, detail="Invalid token")
        response = Response(content='{"authenticated": true}')
        response.headers["X-Auth-User"] = "authenticated"
        return response
    except ValueError:
        logger.warning("Malformed authorization header")
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )


@app.get("/auth/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}


@app.get("/auth/error")
async def auth_error():
    """Custom error page for authentication failures"""
    return {
        "error": "Authentication failed",
        "message": "Please provide valid credentials",
    }
