import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_enhanced import TruckingLoadMatcher, create_sample_loads
from models.transcript_model import Transcript, ConversationTurn

st.set_page_config(page_title="Enhanced Trucking Load Matcher", page_icon="🚛", layout="wide")

if 'matcher' not in st.session_state:
    st.session_state.matcher = TruckingLoadMatcher()

st.title("🚛 Enhanced Trucking Load Matcher")
st.subheader("AI-Powered Load Matching with Advanced Entity Extraction")

sample_loads = create_sample_loads()

with st.sidebar:
    st.header("📊 System Stats")
    st.metric("Available Loads", len(sample_loads))
    
    st.subheader("🚛 Available Loads")
    for load in sample_loads:
        with st.expander(f"{load.id}: {load.from_location} → {load.to_location}"):
            st.write(f"**Type**: {load.truck_type}")
            st.write(f"**Price**: ₹{load.price:,}")

st.header("📱 Process Transcript")
transcript_text = st.text_area("Enter conversation:", height=150, 
    placeholder="Shipper: Hello, do you have truck for Mumbai to Delhi?\nTrucker: Yes sir, 25 feet container, 20 ton capacity...")

if st.button("🔄 Process Transcript", type="primary", disabled=not transcript_text.strip()):
    if transcript_text.strip():
        try:
            with st.spinner("Processing with enhanced entity extraction..."):
                transcript = Transcript(
                    conversation_text=transcript_text.strip(),
                    turns=[ConversationTurn(speaker="trucker", text=transcript_text.strip())]
                )
                
                result = st.session_state.matcher.process_transcript(transcript, sample_loads)
                
                st.success("✅ Enhanced processing completed!")
                
                # Enhanced Entity Display
                st.header("🔍 Enhanced Entity Extraction Results")
                
                # Create tabs for different entity categories
                tab1, tab2, tab3, tab4 = st.tabs(["🚛 Truck Details", "📍 Locations", "💰 Pricing", "📞 Contact & Conversation"])
                
                with tab1:
                    st.subheader("Truck Specifications")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Details:**")
                        st.write(f"Type: {result.extracted_entities.truck_type or result.extracted_entities.fo_truck_type or 'Not specified'}")
                        st.write(f"Length: {result.extracted_entities.truck_length or result.extracted_entities.fo_truck_length or 'Not specified'}")
                        st.write(f"Tonnage: {result.extracted_entities.tonnage or result.extracted_entities.fo_tonnage or 'Not specified'}")
                    
                    with col2:
                        st.write("**FO Specific Details:**")
                        st.write(f"FO Truck Type: {result.extracted_entities.fo_truck_type or 'Not specified'}")
                        st.write(f"FO Tonnage: {result.extracted_entities.fo_tonnage or 'Not specified'}")
                        st.write(f"FO Length: {result.extracted_entities.fo_truck_length or 'Not specified'}")
                
                with tab2:
                    st.subheader("Location Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current/General:**")
                        st.write(f"Current Location: {result.extracted_entities.current_location or 'Not specified'}")
                        if result.extracted_entities.preferred_routes:
                            st.write(f"Preferred Routes: {', '.join(result.extracted_entities.preferred_routes)}")
                        else:
                            st.write("Preferred Routes: Not specified")
                    
                    with col2:
                        st.write("**FO Specific Route:**")
                        st.write(f"FO From Location: {result.extracted_entities.fo_from_location or 'Not specified'}")
                        st.write(f"FO To Location: {result.extracted_entities.fo_to_location or 'Not specified'}")
                
                with tab3:
                    st.subheader("Pricing Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**General Pricing:**")
                        st.write(f"Expected Rate: ₹{result.extracted_entities.expected_rate:,}" if result.extracted_entities.expected_rate else "Expected Rate: Not specified")
                        st.write(f"Rate Flexibility: {result.extracted_entities.rate_flexibility or 'Not specified'}")
                    
                    with col2:
                        st.write("**Quoted Prices:**")
                        st.write(f"FO Quoted Price: ₹{result.extracted_entities.fo_quoted_price:,}" if result.extracted_entities.fo_quoted_price else "FO Quoted Price: Not specified")
                        st.write(f"Shipper Quoted Price: ₹{result.extracted_entities.shipper_quoted_price:,}" if result.extracted_entities.shipper_quoted_price else "Shipper Quoted Price: Not specified")
                
                with tab4:
                    st.subheader("Contact & Conversation Analysis")
                    
                    # Contact Information
                    st.write("**📞 Contact Information:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Phone Number: {result.extracted_entities.phone_number or 'Not specified'}")
                    with col2:
                        st.write(f"FO Shared Number: {result.extracted_entities.fo_shared_number or 'Not specified'}")
                    
                    st.write("---")
                    
                    # Conversation Entities
                    st.write("**💬 Conversation Analysis:**")
                    
                    conv_col1, conv_col2 = st.columns(2)
                    
                    with conv_col1:
                        st.write("**Conversation Events:**")
                        st.write(f"📦 TI Pitched Load: {'✅ Yes' if result.extracted_entities.did_ti_pitch_load else '❌ No'}")
                        st.write(f"💰 Price Discussed: {'✅ Yes' if result.extracted_entities.was_price_discussed else '❌ No'}")
                    
                    with conv_col2:
                        st.write("**Communication Status:**")
                        st.write(f"📵 TI Said No Load: {'✅ Yes' if result.extracted_entities.did_ti_say_no_load else '❌ No'}")
                        st.write(f"📱 Number Exchanged: {'✅ Yes' if result.extracted_entities.was_number_exchanged else '❌ No'}")
                
                # Confidence and Quality Metrics
                st.header("📊 Extraction Quality")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    overall_confidence = result.extracted_entities.confidence_scores.get('overall', 0)
                    st.metric("Overall Confidence", f"{overall_confidence:.1%}")
                
                with col2:
                    entities_extracted = len([v for v in result.extracted_entities.dict().values() if v])
                    st.metric("Entities Extracted", entities_extracted)
                
                with col3:
                    conversation_quality = "High" if result.extracted_entities.was_number_exchanged else "Medium" if result.extracted_entities.was_price_discussed else "Basic"
                    st.metric("Conversation Quality", conversation_quality)
                
                # Load Matches (existing functionality)
                if result.load_matches:
                    st.header("🎯 Load Matches")
                    for i, match in enumerate(result.load_matches):
                        match_color = "🟢" if match.overall_score > 0.7 else "🟡" if match.overall_score > 0.5 else "🔴"
                        with st.expander(f"{match_color} Match {i+1}: Load {match.load_id} ({match.overall_score:.1%})"):
                            st.write(f"**Overall Score**: {match.overall_score:.1%}")
                            st.write(f"**Recommendation**: {match.recommendation}")
                
                # Business Recommendation
                st.header("💼 Business Recommendation")
                
                # Show enhanced business recommendation if available
                if hasattr(result, 'business_recommendation'):
                    recommendation = result.business_recommendation
                    reasoning = result.reasoning
                else:
                    # Fallback to basic recommendation logic
                    if result.extracted_entities.was_number_exchanged:
                        recommendation = "create_lead"
                        reasoning = "Number was exchanged - strong lead potential"
                    elif result.extracted_entities.was_price_discussed:
                        recommendation = "human_review"
                        reasoning = "Price discussion occurred - worth following up"
                    else:
                        recommendation = "monitor"
                        reasoning = "Basic conversation - monitor for future opportunities"
                
                # Color-code the recommendation
                rec_color = {"auto_approve": "🟢", "human_review": "🟡", "create_lead": "🔵", "reject": "🔴", "monitor": "⚪"}.get(recommendation, "⚪")
                
                st.write(f"{rec_color} **{recommendation.upper().replace('_', ' ')}**: {reasoning}")
                
                # Show action items if available
                if hasattr(result, 'immediate_actions') and result.immediate_actions:
                    st.write("**⚡ Immediate Actions:**")
                    for action in result.immediate_actions:
                        st.write(f"• {action}")
                
                if hasattr(result, 'follow_up_actions') and result.follow_up_actions:
                    st.write("**📅 Follow-up Actions:**")
                    for action in result.follow_up_actions:
                        st.write(f"• {action}")
                
                # Debug Information (collapsible)
                with st.expander("🔧 Debug Information"):
                    st.write("**Special Requirements:**")
                    for req in result.extracted_entities.special_requirements:
                        st.write(f"• {req}")
                    
                    st.write("**Confidence Scores:**")
                    for key, score in result.extracted_entities.confidence_scores.items():
                        st.write(f"• {key}: {score:.2%}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.write("**Debug Info:**")
            st.code(str(e))