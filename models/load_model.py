from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class LoadStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Load(BaseModel):
    id: str = Field(..., description="Unique load identifier")
    booking_office: str = Field(..., description="Booking office name")
    message_id: str = Field(..., description="WhatsApp message ID")
    timestamp: datetime = Field(..., description="Load posting timestamp")
    
    # Route information
    from_location: str = Field(..., description="Pickup location")
    to_location: str = Field(..., description="Drop location")
    
    # Truck requirements
    truck_type: str = Field(..., description="Type of truck required")
    truck_length: Optional[str] = Field(None, description="Length in feet")
    tonnage: Optional[str] = Field(None, description="Weight capacity in tonnes")
    
    # Load details
    product: str = Field(..., description="Product/material to be transported")
    price: Optional[float] = Field(None, description="Price in rupees")
    num_trucks: int = Field(1, description="Number of trucks required")
    eta: str = Field(..., description="Expected time of availability")
    
    # Status
    status: LoadStatus = Field(LoadStatus.AVAILABLE, description="Current load status")
    assigned_to: Optional[str] = Field(None, description="Assigned trucker ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }