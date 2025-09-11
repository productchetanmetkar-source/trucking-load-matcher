#!/usr/bin/env python3
"""
Enhanced Main orchestrator for the Trucking Load Matching System
Now with comprehensive entity extraction and conversation analysis
"""

import time
from typing import List, Optional
from datetime import datetime

# Import enhanced components
from agents.entity_extraction_agent import EntityExtractionAgent
from agents.load_matching_agent import LoadMatchingAgent
from models.transcript_model import Transcript, ConversationTurn
from models.load_model import Load, LoadStatus
from models.entities_model import ExtractedEntities, TruckType, EnhancedMatchResult, ConversationAnalysis


class EnhancedTruckingLoadMatcher:
    """
    Enhanced orchestrator class with comprehensive entity extraction
    and conversation analysis capabilities
    """
    
    def __init__(self):
        """Initialize the enhanced matcher with required agents"""
        self.entity_agent = EntityExtractionAgent()
        self.load_agent = LoadMatchingAgent()
        self.processing_history = []
        
    def process_transcript(self, transcript: Transcript, available_loads: List[Load]) -> EnhancedMatchResult:
        """
        Enhanced transcript processing with comprehensive analysis
        """
        
        try:
            print(f"🔍 Enhanced processing started for transcript with {len(transcript.turns)} turns...")
            
            # Step 1: Enhanced entity extraction with conversation analysis
            extracted_entities = self.entity_agent.extract_entities(transcript)
            
            if not extracted_entities:
                return EnhancedMatchResult(
                    extracted_entities=ExtractedEntities(),
                    load_matches=[],
                    business_recommendation="reject",
                    reasoning="Could not extract any meaningful entities from transcript",
                    processing_timestamp=time.time(),
                    confidence_level="low",
                    immediate_actions=["Review transcript quality", "Retry with manual processing"],
                    follow_up_actions=[]
                )
            
            # Step 2: Perform conversation analysis
            conversation_analysis = self._analyze_conversation(transcript, extracted_entities)
            
            # Step 3: Enhanced load matching with conversation context
            load_matches = self.load_agent.find_matching_loads(extracted_entities, available_loads)
            
            # Step 4: Enhanced business recommendation with conversation insights
            business_recommendation, reasoning = self._determine_enhanced_business_action(
                extracted_entities, load_matches, conversation_analysis
            )
            
            # Step 5: Generate action items
            immediate_actions, follow_up_actions = self._generate_action_items(
                extracted_entities, load_matches, conversation_analysis
            )
            
            # Step 6: Determine confidence level
            confidence_level = self._calculate_confidence_level(extracted_entities, conversation_analysis)
            
            # Step 7: Create comprehensive result
            result = EnhancedMatchResult(
                extracted_entities=extracted_entities,
                load_matches=load_matches,
                business_recommendation=business_recommendation,
                reasoning=reasoning,
                conversation_analysis=conversation_analysis,
                processing_timestamp=time.time(),
                confidence_level=confidence_level,
                immediate_actions=immediate_actions,
                follow_up_actions=follow_up_actions
            )
            
            # Step 8: Log detailed results
            self._log_processing_results(result)
            
            print(f"✅ Enhanced processing completed: {business_recommendation}")
            return result
            
        except Exception as e:
            print(f"❌ Error in enhanced processing: {e}")
            import traceback
            traceback.print_exc()
            return EnhancedMatchResult(
                extracted_entities=ExtractedEntities(),
                load_matches=[],
                business_recommendation="reject",
                reasoning=f"Processing error: {str(e)}",
                processing_timestamp=time.time(),
                confidence_level="error",
                immediate_actions=["Check system logs", "Manual review required"],
                follow_up_actions=["System diagnostics"]
            )
    
    def _analyze_conversation(self, transcript: Transcript, entities: ExtractedEntities) -> ConversationAnalysis:
        """Perform detailed conversation analysis"""
        
        # Count speakers and participation
        speakers = set()
        total_words = 0
        fo_words = 0
        ti_words = 0
        
        for turn in transcript.turns:
            speakers.add(turn.speaker)
            words = len(turn.text.split())
            total_words += words
            
            # Classify speaker type for participation analysis
            if 'trucker' in turn.speaker.lower() or 'fo' in turn.speaker.lower():
                fo_words += words
            elif 'ti' in turn.speaker.lower() or 'shipper' in turn.speaker.lower():
                ti_words += words
        
        # Calculate participation percentages
        fo_participation = (fo_words / total_words * 100) if total_words > 0 else 0
        ti_participation = (ti_words / total_words * 100) if total_words > 0 else 0
        
        # Analyze topics discussed
        full_text = " ".join([turn.text for turn in transcript.turns]).lower()
        topics_discussed = []
        
        if any(word in full_text for word in ['truck', 'vehicle', 'tonnage', 'feet']):
            topics_discussed.append("truck_specifications")
        if any(word in full_text for word in ['rate', 'price', 'amount', 'rupees']):
            topics_discussed.append("pricing")
        if any(word in full_text for word in ['load', 'cargo', 'material']):
            topics_discussed.append("load_requirements")
        if any(word in full_text for word in ['location', 'from', 'to', 'route']):
            topics_discussed.append("route_planning")
        if any(word in full_text for word in ['number', 'phone', 'mobile', 'contact']):
            topics_discussed.append("contact_exchange")
        
        # Calculate information completeness
        required_info = ['truck_type', 'tonnage', 'location', 'contact']
        provided_info = []
        
        if entities.truck_type or entities.fo_truck_type:
            provided_info.append('truck_type')
        if entities.tonnage or entities.fo_tonnage:
            provided_info.append('tonnage')
        if entities.current_location or entities.fo_from_location:
            provided_info.append('location')
        if entities.phone_number or entities.fo_shared_number:
            provided_info.append('contact')
        
        information_completeness = len(provided_info) / len(required_info) * 100
        
        # Identify success and failure indicators
        call_success_indicators = []
        call_failure_indicators = []
        
        if entities.was_number_exchanged:
            call_success_indicators.append("phone_number_exchanged")
        if entities.was_price_discussed:
            call_success_indicators.append("price_discussion_occurred")
        if entities.did_ti_pitch_load:
            call_success_indicators.append("load_opportunity_presented")
        
        if entities.did_ti_say_no_load:
            call_failure_indicators.append("no_load_available")
        if not entities.was_price_discussed and not entities.did_ti_pitch_load:
            call_failure_indicators.append("limited_engagement")
        
        # Generate market insights
        market_insights = []
        if entities.fo_quoted_price and entities.shipper_quoted_price:
            price_diff = abs(entities.fo_quoted_price - entities.shipper_quoted_price)
            if price_diff > 1000:
                market_insights.append("significant_price_gap_detected")
        
        # Urgency and relationship indicators
        urgency_indicators = []
        relationship_indicators = []
        
        if 'immediate' in full_text or 'urgent' in full_text:
            urgency_indicators.append("immediate_requirement")
        if 'brother' in full_text or 'bhai' in full_text:
            relationship_indicators.append("familial_address_used")
        if entities.was_number_exchanged:
            relationship_indicators.append("contact_willingly_shared")
        
        return ConversationAnalysis(
            total_speakers=len(speakers),
            fo_participation=fo_participation,
            ti_participation=ti_participation,
            topics_discussed=topics_discussed,
            information_completeness=information_completeness,
            call_success_indicators=call_success_indicators,
            call_failure_indicators=call_failure_indicators,
            market_insights=market_insights,
            competitive_intelligence=[],
            urgency_indicators=urgency_indicators,
            relationship_indicators=relationship_indicators
        )
    
    def _determine_enhanced_business_action(self, entities: ExtractedEntities, 
                                           matches: List, analysis: ConversationAnalysis) -> tuple:
        """Enhanced business recommendation using conversation insights"""
        
        # Base recommendation logic
        if not matches:
            if entities.was_number_exchanged and entities.truck_type:
                return "create_lead", f"Strong lead potential - number exchanged, truck details available. Info completeness: {analysis.information_completeness:.0f}%"
            elif len(analysis.call_success_indicators) >= 2:
                return "create_lead", f"Good engagement indicators: {', '.join(analysis.call_success_indicators)}"
            else:
                return "reject", "Insufficient engagement and no current matches"
        
        # Enhanced scoring with conversation factors
        best_match = max(matches, key=lambda x: x.overall_score)
        base_score = best_match.overall_score
        
        # Apply conversation bonuses
        conversation_bonus = 0
        if entities.was_number_exchanged:
            conversation_bonus += 0.1
        if entities.was_price_discussed:
            conversation_bonus += 0.05
        if len(analysis.call_success_indicators) >= 3:
            conversation_bonus += 0.05
        
        enhanced_score = min(1.0, base_score + conversation_bonus)
        
        if enhanced_score >= 0.8:
            return "auto_approve", f"High match score ({enhanced_score:.1%}) with strong conversation indicators"
        elif enhanced_score >= 0.6:
            return "human_review", f"Good match ({enhanced_score:.1%}) - conversation analysis suggests potential"
        elif enhanced_score >= 0.4:
            return "create_lead", f"Moderate match with conversation engagement - follow up recommended"
        else:
            return "reject", f"Low match scores (best: {enhanced_score:.1%})"
    
    def _generate_action_items(self, entities: ExtractedEntities, matches: List, 
                              analysis: ConversationAnalysis) -> tuple:
        """Generate immediate and follow-up action items"""
        
        immediate_actions = []
        follow_up_actions = []
        
        # Immediate actions based on conversation
        if entities.was_number_exchanged and not entities.phone_number:
            immediate_actions.append("Extract and validate shared phone number")
        
        if entities.was_price_discussed and not entities.expected_rate:
            immediate_actions.append("Review conversation for price details")
        
        if analysis.information_completeness < 50:
            immediate_actions.append("Gather missing truck/route information")
        
        # Follow-up actions
        if entities.was_number_exchanged:
            follow_up_actions.append("Call back within 24 hours to maintain engagement")
        
        if entities.did_ti_pitch_load and matches:
            follow_up_actions.append("Send detailed load information via WhatsApp")
        
        if len(analysis.urgency_indicators) > 0:
            follow_up_actions.append("Priority follow-up - urgency indicators detected")
        
        return immediate_actions, follow_up_actions
    
    def _calculate_confidence_level(self, entities: ExtractedEntities, 
                                   analysis: ConversationAnalysis) -> str:
        """Calculate overall confidence level"""
        
        confidence_factors = []
        
        # Entity extraction confidence
        if entities.confidence_scores.get('overall', 0) > 0.8:
            confidence_factors.append("high_extraction")
        elif entities.confidence_scores.get('overall', 0) > 0.5:
            confidence_factors.append("medium_extraction")
        else:
            confidence_factors.append("low_extraction")
        
        # Conversation completeness
        if analysis.information_completeness > 75:
            confidence_factors.append("complete_info")
        elif analysis.information_completeness > 50:
            confidence_factors.append("partial_info")
        else:
            confidence_factors.append("incomplete_info")
        
        # Engagement level
        if len(analysis.call_success_indicators) >= 3:
            confidence_factors.append("high_engagement")
        elif len(analysis.call_success_indicators) >= 1:
            confidence_factors.append("medium_engagement")
        else:
            confidence_factors.append("low_engagement")
        
        # Determine overall confidence
        high_factors = sum(1 for f in confidence_factors if 'high' in f)
        medium_factors = sum(1 for f in confidence_factors if 'medium' in f)
        
        if high_factors >= 2:
            return "high"
        elif high_factors >= 1 or medium_factors >= 2:
            return "medium"
        else:
            return "low"
    
    def _log_processing_results(self, result: EnhancedMatchResult):
        """Log detailed processing results"""
        
        print(f"\n📊 ENHANCED PROCESSING RESULTS:")
        print(f"   🎯 Business Recommendation: {result.business_recommendation}")
        print(f"   🔍 Confidence Level: {result.confidence_level}")
        print(f"   📋 Extracted Entities: {len([k for k, v in result.extracted_entities.dict().items() if v])}")
        print(f"   🤝 Load Matches: {len(result.load_matches)}")
        
        if result.conversation_analysis:
            print(f"   💬 Topics Discussed: {', '.join(result.conversation_analysis.topics_discussed)}")
            print(f"   📈 Info Completeness: {result.conversation_analysis.information_completeness:.1f}%")
            print(f"   ✅ Success Indicators: {len(result.conversation_analysis.call_success_indicators)}")
        
        if result.immediate_actions:
            print(f"   ⚡ Immediate Actions: {len(result.immediate_actions)}")
        
        # Store in processing history
        self.processing_history.append({
            'timestamp': result.processing_timestamp,
            'recommendation': result.business_recommendation,
            'confidence': result.confidence_level,
            'entities_count': len([k for k, v in result.extracted_entities.dict().items() if v])
        })


# Alias for backward compatibility
TruckingLoadMatcher = EnhancedTruckingLoadMatcher


def create_sample_loads() -> List[Load]:
    """Create sample loads for testing"""
    
    return [
        Load(
            id="L001",
            booking_office="Chennai Office",
            message_id="MSG001", 
            timestamp=datetime.now(),
            from_location="Chennai",
            to_location="Bangalore",
            truck_type="Container",
            truck_length="20",
            tonnage="20",
            product="General Cargo", 
            price=25000.0,
            num_trucks=1,
            eta="2 days",
            status=LoadStatus.AVAILABLE
        ),
        Load(
            id="L002",
            booking_office="Mumbai Office",
            message_id="MSG002",
            timestamp=datetime.now(), 
            from_location="Mumbai",
            to_location="Coimbatore",
            truck_type="Open",
            truck_length="25",
            tonnage="15",
            product="Textiles",
            price=18000.0,
            num_trucks=1,
            eta="1 day",
            status=LoadStatus.AVAILABLE
        ),
        Load(
            id="L003",
            booking_office="Tumakuru Office",
            message_id="MSG003",
            timestamp=datetime.now(),
            from_location="Tumakuru", 
            to_location="Madurai",
            truck_type="Open",
            truck_length="25",
            tonnage="25",
            product="Agriculture",
            price=22000.0,
            num_trucks=1,
            eta="3 days",
            status=LoadStatus.AVAILABLE
        )
    ]


def main():
    """Enhanced main function for testing the system"""
    
    print("🚛 Enhanced Trucking Load Matcher - Testing")
    print("=" * 60)
    
    try:
        # Initialize the enhanced matcher
        matcher = EnhancedTruckingLoadMatcher()
        
        # Test transcript that includes number sharing (like your screenshot)
        conversation_text = """Trucker: Yes, was there a load of yours for Gujarat?
Shipper: Yes, tell me your number, your mobile number.
Trucker: 98... 9867... 33... 74... 13.
Shipper: Sir, what is your truck's payload capacity?
Trucker: The truck is 10 ton capacity. Your load here is also 10 ton.
Shipper: Is it an Open truck? Is it an Open truck?"""
        
        test_transcript = Transcript(
            conversation_text=conversation_text,
            turns=[
                ConversationTurn(speaker="trucker", text="Yes, was there a load of yours for Gujarat?", timestamp=time.time()),
                ConversationTurn(speaker="shipper", text="Yes, tell me your number, your mobile number.", timestamp=time.time()),
                ConversationTurn(speaker="trucker", text="98... 9867... 33... 74... 13.", timestamp=time.time()),
                ConversationTurn(speaker="shipper", text="Sir, what is your truck's payload capacity?", timestamp=time.time()),
                ConversationTurn(speaker="trucker", text="The truck is 10 ton capacity. Your load here is also 10 ton.", timestamp=time.time()),
                ConversationTurn(speaker="shipper", text="Is it an Open truck? Is it an Open truck?", timestamp=time.time())
            ]
        )
        
        # Create sample loads
        sample_loads = create_sample_loads()
        print(f"✅ Created {len(sample_loads)} sample loads")
        
        # Process the transcript with enhanced system
        result = matcher.process_transcript(test_transcript, sample_loads)
        
        # Display enhanced results
        print(f"\n🔍 ENHANCED EXTRACTED ENTITIES:")
        entities = result.extracted_entities
        
        print(f"   🚛 Truck Type: {entities.truck_type or entities.fo_truck_type}")
        print(f"   ⚖️ Tonnage: {entities.tonnage or entities.fo_tonnage}")
        print(f"   📏 Length: {entities.truck_length or entities.fo_truck_length}")
        print(f"   📍 From Location: {entities.fo_from_location}")
        print(f"   📍 To Location: {entities.fo_to_location}")
        print(f"   📞 Shared Number: {entities.fo_shared_number}")
        print(f"   💰 FO Quoted Price: {entities.fo_quoted_price}")
        print(f"   💰 Shipper Quoted Price: {entities.shipper_quoted_price}")
        
        print(f"\n💬 CONVERSATION ANALYSIS:")
        if result.conversation_analysis:
            analysis = result.conversation_analysis
            print(f"   📊 Info Completeness: {analysis.information_completeness:.1f}%")
            print(f"   🎯 Topics Discussed: {', '.join(analysis.topics_discussed)}")
            print(f"   ✅ Success Indicators: {', '.join(analysis.call_success_indicators)}")
            print(f"   ❌ Failure Indicators: {', '.join(analysis.call_failure_indicators)}")
        
        print(f"\n📞 CONVERSATIONAL ENTITIES:")
        print(f"   📱 Number Exchanged: {entities.was_number_exchanged}")
        print(f"   💰 Price Discussed: {entities.was_price_discussed}")
        print(f"   📦 TI Pitched Load: {entities.did_ti_pitch_load}")
        print(f"   ❌ TI Said No Load: {entities.did_ti_say_no_load}")
        
        print(f"\n🎯 Load Matches: {len(result.load_matches)}")
        for i, match in enumerate(result.load_matches[:3]):
            print(f"   {i+1}. Load {match.load_id} - Score: {match.overall_score:.1%}")
        
        print(f"\n💼 Business Recommendation: {result.business_recommendation}")
        print(f"   Reasoning: {result.reasoning}")
        print(f"   Confidence: {result.confidence_level}")
        
        if result.immediate_actions:
            print(f"\n⚡ Immediate Actions:")
            for action in result.immediate_actions:
                print(f"   • {action}")
        
        if result.follow_up_actions:
            print(f"\n📅 Follow-up Actions:")
            for action in result.follow_up_actions:
                print(f"   • {action}")
        
        print(f"\n✅ Enhanced system test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()