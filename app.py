import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import TruckingLoadMatcher, create_sample_loads
from models.transcript_model import Transcript, ConversationTurn

st.set_page_config(page_title="Trucking Load Matcher", page_icon="🚛", layout="wide")

if 'matcher' not in st.session_state:
    st.session_state.matcher = TruckingLoadMatcher()

st.title("🚛 Trucking Load Matcher")
st.subheader("AI-Powered Load Matching System")

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
    placeholder="I have a 25 feet open vehicle. If there's anything towards Tamil Nadu side...")

if st.button("🔄 Process Transcript", type="primary", disabled=not transcript_text.strip()):
    if transcript_text.strip():
        try:
            with st.spinner("Processing..."):
                transcript = Transcript(
                    conversation_text=transcript_text.strip(),
                    turns=[ConversationTurn(speaker="trucker", text=transcript_text.strip())]
                )
                
                result = st.session_state.matcher.process_transcript(transcript, sample_loads)
                
                st.success("✅ Processing completed!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("🚛 Truck Details")
                    st.write(f"**Type**: {result.extracted_entities.truck_type or 'Not specified'}")
                    st.write(f"**Length**: {result.extracted_entities.truck_length or 'Not specified'}")
                    st.write(f"**Tonnage**: {result.extracted_entities.tonnage or 'Not specified'}")
                    
                with col2:
                    st.subheader("📍 Locations")
                    st.write(f"**Current**: {result.extracted_entities.current_location or 'Not specified'}")
                    st.write(f"**Routes**: {', '.join(result.extracted_entities.preferred_routes) if result.extracted_entities.preferred_routes else 'Not specified'}")
                    
                with col3:
                    st.subheader("📞 Contact")
                    st.write(f"**Phone**: {result.extracted_entities.phone_number or 'Not specified'}")
                
                if result.load_matches:
                    st.header("🎯 Load Matches")
                    for i, match in enumerate(result.load_matches):
                        match_color = "🟢" if match.overall_score > 0.7 else "🟡" if match.overall_score > 0.5 else "🔴"
                        with st.expander(f"{match_color} Match {i+1}: Load {match.load_id} ({match.overall_score:.1%})"):
                            st.write(f"**Overall Score**: {match.overall_score:.1%}")
                            st.write(f"**Recommendation**: {match.recommendation}")
                
                st.header("💼 Business Recommendation")
                st.write(f"**{result.business_recommendation}**: {result.reasoning}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
