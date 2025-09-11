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
    """Enhanced model for extracted entities with deterministic and conversational data"""
    
    # Original truck specifications
    truck_type: Optional[TruckType] = Field(None, description="Type of truck")
    truck_length: Optional[int] = Field(None, description="Length in feet")
    tonnage: Optional[float] = Field(None, description="Capacity in tonnes")
    
    # Original route information
    current_location: Optional[str] = Field(None, description="Current truck location")
    preferred_routes: List[str] = Field(default_factory=list, description="Preferred pickup locations")
    
    # Original commercial terms
    expected_rate: Optional[float] = Field(None, description="Expected rate in rupees")
    rate_flexibility: Optional[str] = Field(None, description="Rate negotiation flexibility")
    
    # Original availability
    available_immediately: bool = Field(True, description="Immediate availability")
    availability_constraints: List[str] = Field(default_factory=list, description="Time/day constraints")
    
    # Original contact information
    phone_number: Optional[str] = Field(None, description="Trucker's phone number")
    
    # Original special requirements
    special_requirements: List[str] = Field(default_factory=list, description="Special needs (tarpaulin, etc.)")
    
    # Original confidence scores
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Confidence per entity")
    
    # ===== NEW DETERMINISTIC ENTITIES =====
    
    # FO (Field Officer/Trucker) Location Information
    fo_from_location: Optional[str] = Field(None, description="FO's departure location")
    fo_to_location: Optional[str] = Field(None, description="FO's destination location")
    
    # FO Truck Specifications (duplicated for clarity)
    fo_truck_type: Optional[TruckType] = Field(None, description="FO's truck type")
    fo_tonnage: Optional[float] = Field(None, description="FO's truck tonnage capacity")
    fo_truck_length: Optional[int] = Field(None, description="FO's truck length in feet")
    
    # Pricing Information
    shipper_quoted_price: Optional[float] = Field(None, description="Price quoted by shipper/TI")
    fo_quoted_price: Optional[float] = Field(None, description="Price quoted/expected by FO")
    
    # Contact Information
    fo_shared_number: Optional[str] = Field(None, description="Phone number shared by FO")
    
    # ===== NEW CONVERSATIONAL ENTITIES =====
    
    # Conversation Flow Indicators
    did_ti_pitch_load: bool = Field(False, description="Did TI pitch any load during call")
    was_price_discussed: bool = Field(False, description="Was price/rate discussed in the call")
    did_ti_say_no_load: bool = Field(False, description="Did TI say no load available")
    was_number_exchanged: bool = Field(False, description="Was phone number exchanged in call")
    
    # Additional Conversation Metadata
    conversation_quality: Optional[str] = Field(None, description="Overall conversation quality assessment")
    lead_potential: Optional[str] = Field(None, description="Potential for future business")
    call_outcome: Optional[str] = Field(None, description="Overall outcome of the call")
    
    class Config:
        # Allow extra fields for future extensibility
        extra = "allow"

class MatchingResult(BaseModel):
    """Enhanced matching result with conversation context"""
    
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
    
    # ===== NEW CONVERSATION-AWARE SCORING =====
    
    # Conversation Context Factors
    conversation_engagement_score: Optional[float] = Field(None, description="How engaged was the conversation")
    number_exchange_bonus: Optional[float] = Field(None, description="Bonus score if number was exchanged")
    price_discussion_factor: Optional[float] = Field(None, description="Factor based on price discussion quality")
    
    # Enhanced Recommendations
    follow_up_recommendation: Optional[str] = Field(None, description="Specific follow-up action recommended")
    timing_recommendation: Optional[str] = Field(None, description="When to follow up")
    
class ConversationAnalysis(BaseModel):
    """Separate model for detailed conversation analysis"""
    
    # Speaker Analysis
    total_speakers: int = Field(..., description="Number of distinct speakers")
    fo_participation: float = Field(..., description="FO participation percentage")
    ti_participation: float = Field(..., description="TI participation percentage")
    
    # Content Analysis
    topics_discussed: List[str] = Field(default_factory=list, description="Main topics covered")
    information_completeness: float = Field(..., description="How complete was the information exchange")
    
    # Outcome Analysis
    call_success_indicators: List[str] = Field(default_factory=list, description="Positive indicators")
    call_failure_indicators: List[str] = Field(default_factory=list, description="Negative indicators")
    
    # Business Intelligence
    market_insights: List[str] = Field(default_factory=list, description="Market insights from conversation")
    competitive_intelligence: List[str] = Field(default_factory=list, description="Competitive insights")
    
    # Follow-up Intelligence
    urgency_indicators: List[str] = Field(default_factory=list, description="Urgency signals detected")
    relationship_indicators: List[str] = Field(default_factory=list, description="Relationship building signals")
    
class EnhancedMatchResult(BaseModel):
    """Complete result object with entities, matches, and conversation analysis"""
    
    # Core Results
    extracted_entities: ExtractedEntities = Field(..., description="All extracted entities")
    load_matches: List[MatchingResult] = Field(default_factory=list, description="Matched loads")
    
    # Business Recommendation
    business_recommendation: str = Field(..., description="Primary business action")
    reasoning: str = Field(..., description="Reasoning for recommendation")
    
    # Enhanced Analysis
    conversation_analysis: Optional[ConversationAnalysis] = Field(None, description="Detailed conversation analysis")
    
    # Metadata
    processing_timestamp: float = Field(..., description="When this was processed")
    confidence_level: str = Field(..., description="Overall confidence level")
    
    # Action Items
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate action items")
    follow_up_actions: List[str] = Field(default_factory=list, description="Follow-up action items")
    
    class Config:
        extra = "allow"