"""
Authentication service for VizLearn API
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..core.config import settings

security = HTTPBearer()


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify the authentication token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If authentication fails
    """
    if credentials.credentials != settings.static_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
