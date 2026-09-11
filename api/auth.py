import os
import logging
from typing import Dict
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, str]:
    """
    Validate the Bearer token using Supabase Auth.
    If testing/mock mode is active, accepts any token and returns a dummy user ID.
    Returns a dict with {"id": "user_uuid"}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    
    # Check if we are running in testing/mock mode
    if os.environ.get("DATABASE_BACKEND", "").lower() == "mock":
        # For offline testing, accept only the explicit dummy token
        if token == "test-token-valid":
            return {"id": "test-user-id"}
        elif token == "test-token-valid-user-b":
            return {"id": "test-user-id-b"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Production/Supabase token validation
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SECRET_KEY")
        
        if not url or not key:
            raise RuntimeError("Supabase credentials missing.")
            
        client = create_client(url, key)
        # Verify token by fetching user details from Supabase
        user_response = client.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("No user returned from Supabase auth")
            
        return {"id": str(user_response.user.id)}
        
    except Exception as e:
        logger.warning(f"Auth failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
