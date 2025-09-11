import streamlit as st
import sys
import os
import time
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import TruckingLoadMatcher
    from models.transcript_model import Transcript
    from models.load_model import Load
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure you're running from the project root directory")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Trucking Load Matcher",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'matcher' not in st.session_state:
    st.session_state.matcher = TruckingLoadMatcher()

if 'processing_history' not in st.session_state:
    st.session_state.processing_history = []

# Sidebar
with st.sidebar:
    st.header("📊 System Stats")
    
    # Sample loads for testing
    sample_loads = [
        Load(
            id="L001",
            origin="Chennai",
            destination="Bangalore",
            truck_type="Container",
            tonnage=20,
            rate=25000,
            contact="9876543210"
        ),
        Load(
            id="L002", 
            origin="Mumbai",
            destination="Coimbatore",
            truck_type="Open",
            tonnage=15,
            rate=18000,
            contact="9876543211"
        ),
        Load(
            id="L003",
            origin="Tumakuru",
            destination="Madurai", 
            truck_type="Open",
            tonnage=25,
            rate=22000,
            contact="9876543212"
        )
    ]
    
    st.metric("Available Loads", len(sample_loads))
    st.metric("Processed Calls", len(st.session_state.processing_history))
    
    # Load Management
    st.subheader("🚛 Available Loads")
    for load in sample_loads:
        with st.expander(f"{load.id}: {load.origin} → {load.destination}"):
            st.write(f"**Type**: {load.truck_type}")
            st.write(f"**Tonnage**: {load.tonnage}T")
            st.write(f"**Rate**: ₹{load.rate:,}")

# Main content
st.title("🚛 Trucking Load Matcher")
st.subheader("AI-Powered Load Matching for Traffic Incharges")

# Input section
st.header("📱 Process New Transcript")

# Simple text input method
input_method = st.radio(
    "Choose input method:",
    ["Simple Text", "Structured Input", "File Upload"],
    horizontal=True
)

transcript_text = ""

if input_method == "Simple Text":
    st.info("💡 Just paste the conversation text - timestamp and duration are optional!")
    transcript_text = st.text_area(
        "Enter transcript:",
        height=150,
        placeholder="Example: I have a 25 feet open vehicle. If there's anything towards Tamil Nadu side, like Madurai or Coimbatore..."
    )
    
elif input_method == "Structured Input":
    col1, col2 = st.columns(2)
    
    with col1:
        transcript_text = st.text_area(
            "Conversation Text:",
            height=150,
            placeholder="Enter the conversation..."
        )
        
    with col2:
        call_duration = st.number_input("Call Duration (seconds)", min_value=0, value=0)
        call_id = st.text_input("Call ID (optional)", placeholder="AUTO_GENERATED")
        
elif input_method == "File Upload":
    uploaded_file = st.file_uploader(
        "Upload transcript file",
        type=['txt', 'json'],
        help="Upload a text file or JSON file containing the transcript"
    )
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            if uploaded_file.name.endswith('.json'):
                data = json.loads(content)
                transcript_text = data.get('conversation_text', data.get('text', content))
            else:
                transcript_text = content
                
            st.text_area("File Content Preview:", value=transcript_text, height=100)
        except Exception as e:
            st.error(f"Error reading file: {e}")

# Processing button
if st.button("🔄 Process Transcript", type="primary", disabled=not transcript_text.strip()):
    if transcript_text.strip():
        try:
            with st.spinner("Processing transcript..."):
                # Create transcript object with minimal required data
                transcript = Transcript(
                    conversation_text=transcript_text.strip(),
                    timestamp=time.time(),  # Will default to current time
                    call_duration=locals().get('call_duration', None),
                    call_id=locals().get('call_id', f"CALL_{int(time.time())}")
                )
                
                # Process the transcript
                result = st.session_state.matcher.process_transcript(
                    transcript, 
                    sample_loads
                )
                
                # Add to processing history
                st.session_state.processing_history.append({
                    'timestamp': datetime.now(),
                    'transcript': transcript_text[:100] + "...",
                    'result': result
                })
                
                # Display results
                st.success("✅ Processing completed!")
                
                # Extracted entities
                st.header("🔍 Extracted Information")
                entities = result.extracted_entities
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("🚛 Truck Details")
                    st.write(f"**Type**: {entities.truck_type or 'Not specified'}")
                    st.write(f"**Tonnage**: {entities.tonnage or 'Not specified'}")
                    st.write(f"**Length**: {entities.truck_length or 'Not specified'}")
                    
                with col2:
                    st.subheader("📍 Locations")
                    st.write(f"**Current**: {entities.current_location or 'Not specified'}")
                    st.write(f"**Destination**: {', '.join(entities.destinations) if entities.destinations else 'Not specified'}")
                    
                with col3:
                    st.subheader("📞 Contact")
                    st.write(f"**Phone**: {', '.join(entities.phone_numbers) if entities.phone_numbers else 'Not specified'}")
                    st.write(f"**Names**: {', '.join(entities.contact_names) if entities.contact_names else 'Not specified'}")
                
                # Confidence scores
                st.subheader("📊 Extraction Confidence")
                confidence_cols = st.columns(4)
                
                with confidence_cols[0]:
                    st.metric("Overall", f"{entities.overall_confidence:.1%}")
                with confidence_cols[1]:
                    st.metric("Truck Type", f"{entities.truck_type_confidence:.1%}")
                with confidence_cols[2]:
                    st.metric("Location", f"{entities.location_confidence:.1%}")
                with confidence_cols[3]:
                    st.metric("Contact", f"{entities.contact_confidence:.1%}")
                
                # Load matches
                if result.load_matches:
                    st.header("🎯 Load Matches")
                    
                    for i, match in enumerate(result.load_matches):
                        match_color = "🟢" if match.match_score > 0.7 else "🟡" if match.match_score > 0.5 else "🔴"
                        
                        with st.expander(f"{match_color} Match {i+1}: {match.load.from_location} → {match.load.to_location} ({match.match_score:.1%})"):
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Load ID**: {match.load.id}")
                                st.write(f"**Route**: {match.load.from_location} → {match.load.to_location}")
                                st.write(f"**Truck Type**: {match.load.truck_type}")
                                st.write(f"**Tonnage**: {match.load.tonnage}T")
                                st.write(f"**Product**: {match.load.product}")
                                st.write(f"**Price**: ₹{match.load.price:,}")
                                st.write(f"**ETA**: {match.load.eta}")
                                st.write(f"**Status**: {match.load.status}")
                            
                            with col2:
                                st.write("**Score Breakdown:**")
                                for criterion, score in match.score_breakdown.items():
                                    st.write(f"- {criterion.title()}: {score:.1%}")
                                
                                st.write(f"**Business Rule**: {match.business_rule}")
                                if match.reasoning:
                                    st.write(f"**Reasoning**: {match.reasoning}")
                
                # Business recommendation
                st.header("💼 Business Recommendation")
                rec_color = {
                    "auto_approve": "🟢",
                    "human_review": "🟡", 
                    "create_lead": "🔵",
                    "reject": "🔴"
                }.get(result.business_recommendation, "⚪")
                
                st.write(f"{rec_color} **{result.business_recommendation.replace('_', ' ').title()}**")
                
                if result.reasoning:
                    st.write(f"**Reasoning**: {result.reasoning}")
                
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            st.error("Please check that your system is properly configured and try again.")
            
            # Debug information
            with st.expander("🐛 Debug Information"):
                st.code(str(e))
                st.write("**Transcript text length:**", len(transcript_text))
                st.write("**System status:** Please run `python main.py` in terminal to test core functionality")

# Processing History
if st.session_state.processing_history:
    st.header("📋 Recent Processing History")
    
    for i, entry in enumerate(reversed(st.session_state.processing_history[-5:])):  # Show last 5
        with st.expander(f"Call {len(st.session_state.processing_history) - i}: {entry['timestamp'].strftime('%H:%M:%S')}"):
            st.write(f"**Transcript**: {entry['transcript']}")
            if entry.get('result') and hasattr(entry['result'], 'business_recommendation'):
                st.write(f"**Recommendation**: {entry['result'].business_recommendation}")

# Footer
st.markdown("---")
st.markdown("**🚛 Trucking Load Matcher** - AI-Powered Load Matching System")
st.markdown("*Now supports simple text input - no timestamp required!*")