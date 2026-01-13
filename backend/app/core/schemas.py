"""
Common schemas used across multiple endpoints
"""
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Standard response for delete and other operations"""
    message: str
