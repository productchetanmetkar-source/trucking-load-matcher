from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ConversationTurn(BaseModel):
    speaker: str = Field(..., description="Speaker identifier (A/B)")
    text: str = Field(..., description="Spoken text")
    timestamp: Optional[float] = Field(None, description="Timestamp in conversation")

class Transcript(BaseModel):
    id: str = Field(..., description="Unique transcript identifier")
    call_duration: Optional[float] = Field(None, description="Duration in seconds")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Conversation data
    turns: List[ConversationTurn] = Field(..., description="List of conversation turns")
    
    # Metadata
    caller_number: Optional[str] = Field(None, description="Trucker's phone number")
    load_id: Optional[str] = Field(None, description="Referenced load ID if known")
    language_detected: Optional[str] = Field("mixed", description="Primary language")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }