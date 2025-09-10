from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

class TruckType(str, Enum):
    OPEN = "open"
    CONTAINER = "container" 
    CLOSED = "closed"
    MULTI_AXLE = "multi_axle"
    SINGLE_AXLE = "single_axle"

class ExtractedEntities(BaseModel):
    # Truck specifications
    truck_type: Optional[TruckType] = Field(None, description="Type of truck")
    truck_length: Optional[int] = Field(None, description="Length in feet")
    tonnage: Optional[float] = Field(None, description="Capacity in tonnes")
    
    # Route information
    current_location: Optional[str] = Field(None, description="Current truck location")
    preferred_routes: List[str] = Field(default_factory=list, description="Preferred pickup locations")
    
    # Commercial terms
    expected_rate: Optional[float] = Field(None, description="Expected rate in rupees")
    rate_flexibility: Optional[str] = Field(None, description="Rate negotiation flexibility")
    
    # Availability
    available_immediately: bool = Field(True, description="Immediate availability")
    availability_constraints: List[str] = Field(default_factory=list, description="Time/day constraints")
    
    # Contact information
    phone_number: Optional[str] = Field(None, description="Trucker's phone number")
    
    # Special requirements
    special_requirements: List[str] = Field(default_factory=list, description="Special needs (tarpaulin, etc.)")
    
    # Confidence scores for each extracted entity
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Confidence per entity")

class MatchingResult(BaseModel):
    load_id: str = Field(..., description="Matched load ID")
    trucker_requirements_id: str = Field(..., description="Trucker requirements ID")
    
    # Overall match score
    overall_score: float = Field(..., description="Overall match percentage (0-1)")
    
    # Detailed scores
    detailed_scores: Dict[str, float] = Field(..., description="Score breakdown by parameter")
    
    # Match quality indicators
    mandatory_match: bool = Field(..., description="All mandatory criteria met")
    recommendation: str = Field(..., description="auto_approve, human_review, or create_lead")
    
    # Explanation
    match_reasons: List[str] = Field(default_factory=list, description="Why this is a good match")
    mismatch_reasons: List[str] = Field(default_factory=list, description="Areas of concern")
    
    # Commercial viability
    price_gap: Optional[float] = Field(None, description="Difference in expected vs offered price")
    negotiation_likelihood: float = Field(..., description="Likelihood of successful negotiation")