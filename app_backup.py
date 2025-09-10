import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# Import your existing system
from main import TruckingMatchingOrchestrator, create_sample_loads, create_sample_transcripts

# Page config
st.set_page_config(
    page_title="Trucking Load Matcher",
    page_icon="🚛",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚛 Trucking Load Matching System</h1>
        <p>AI-Powered Load Assignment for Field Officers & Truckers</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize your existing system
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = TruckingMatchingOrchestrator()
        st.session_state.loads = create_sample_loads()
        st.session_state.processing_history = []
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    page = st.sidebar.selectbox("Select Page", [
        "📞 Process Transcript",
        "📋 View Loads",
        "📊 Results History"
    ])
    
    if page == "📞 Process Transcript":
        process_transcript_page()
    elif page == "📋 View Loads":
        view_loads_page()
    elif page == "📊 Results History":
        results_history_page()

def process_transcript_page():
    st.header("📞 Process Call Transcript")
    
    # Sample transcripts
    sample_options = {
        "Custom Input": "",
        "Hindi Example": "FO: Namaste sir, main Rajesh bol raha hun Mumbai se\nBO: Haan Rajesh bhai, kya chahiye?\nFO: Sir mujhe ek 8 tonne ka open truck chahiye, 19 feet length\nBO: Route kya hai?\nFO: Mumbai se Delhi jana hai sir, aur tarpaulin lagana padega\nBO: Phone number?\nFO: 9876543210 sir",
        "English Example": "FO: Hello, I need a container truck for a shipment\nBO: What capacity?\nFO: 25 tonne, 40 feet container\nBO: Route?\nFO: From Mumbai to Delhi, electronics goods\nBO: Contact?\nFO: +91-8765432109",
        "Mixed Language": "FO: Sir trailer chahiye tha\nBO: Kitna tonne?\nFO: 32 tonne, machinery hai\nBO: Route?\nFO: Chennai to Hyderabad\nBO: Phone?\nFO: 7654321098"
    }
    
    # Select sample
    sample_choice = st.selectbox("Choose Example or Enter Custom", list(sample_options.keys()))
    
    if sample_choice == "Custom Input":
        transcript_text = st.text_area(
            "Enter transcript:",
            placeholder="FO: Hello sir, mujhe truck chahiye...",
            height=150
        )
    else:
        transcript_text = sample_options[sample_choice]
        st.text_area("Transcript Preview", transcript_text, height=150, disabled=True)
    
    # Metadata
    col1, col2 = st.columns(2)
    with col1:
        caller_phone = st.text_input("📱 Phone", "+91-9876543210")
    with col2:
        booking_office = st.selectbox("🏢 Booking Office", [
            "BO_Mumbai_Central", "BO_Pune_West", "BO_Chennai_North"
        ])
    
    # Process button
    if st.button("🚀 Process Transcript", type="primary"):
        if transcript_text:
            process_transcript(transcript_text, caller_phone, booking_office)
        else:
            st.error("Please enter a transcript!")

def process_transcript(transcript_text: str, phone: str, bo: str):
    """Process transcript using your existing system"""
    
    with st.spinner("🔄 Processing with AI agents..."):
        try:
            # Use your existing sample transcripts structure
            from models.transcript_model import Transcript, ConversationTurn
            
            transcript = Transcript(
                id=f"WEB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                turns=[
                    ConversationTurn(
                        speaker="combined",
                        text=transcript_text,
                        timestamp=datetime.now()
                    )
                ],
                caller_phone=phone,
                duration_minutes=3,
                booking_office=bo
            )
            
            # Process with your orchestrator
            result = st.session_state.orchestrator.process_call_transcript(
                transcript, st.session_state.loads
            )
            
            # Store result
            st.session_state.processing_history.append({
                'timestamp': datetime.now(),
                'transcript_id': transcript.id,
                'result': result
            })
            
            # Display results
            display_results(result)
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            st.info("💡 Make sure your existing system is working: `python main.py`")

def display_results(result: Dict[str, Any]):
    """Display processing results"""
    st.success("✅ Transcript processed successfully!")
    
    # Extracted entities
    st.subheader("🔍 Extracted Requirements")
    entities = result['extracted_entities']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚛 Truck Type", entities.truck_type or "Not specified")
    with col2:
        st.metric("⚖️ Tonnage", f"{entities.tonnage}T" if entities.tonnage else "Not specified")
    with col3:
        st.metric("📏 Length", f"{entities.length}ft" if entities.length else "Not specified")
    with col4:
        st.metric("📱 Phone", entities.phone_number or "Not provided")
    
    # Matching results
    st.subheader("🎯 Load Matching Results")
    matches = result['matches']
    
    if matches:
        for i, match in enumerate(matches[:3]):  # Show top 3
            with st.expander(f"🚛 Match #{i+1}: {match['load'].id} - {match['score']:.1%}", expanded=i==0):
                
                # Display load details (using safe attribute access)
                load = match['load']
                
                st.write("**Load Details:**")
                st.write(f"- **ID:** {load.id}")
                
                # Safe attribute checking
                if hasattr(load, 'truck_type'):
                    st.write(f"- **Truck Type:** {load.truck_type}")
                if hasattr(load, 'tonnage'):
                    st.write(f"- **Tonnage:** {load.tonnage}")
                if hasattr(load, 'length'):
                    st.write(f"- **Length:** {load.length}ft")
                if hasattr(load, 'product'):
                    st.write(f"- **Product:** {load.product}")
                if hasattr(load, 'price'):
                    st.write(f"- **Price:** ₹{load.price:,}")
                if hasattr(load, 'availability'):
                    st.write(f"- **Available:** {'✅ Yes' if load.availability else '❌ No'}")
                
                # Route information
                if hasattr(load, 'from_location') and hasattr(load, 'to_location'):
                    st.write(f"- **Route:** {load.from_location} → {load.to_location}")
                elif hasattr(load, 'route_from') and hasattr(load, 'route_to'):
                    st.write(f"- **Route:** {load.route_from} → {load.route_to}")
                
                # Match score
                score_color = "#28a745" if match['score'] >= 0.8 else "#ffc107" if match['score'] >= 0.6 else "#17a2b8"
                st.markdown(f"**Match Score:** <span style='color: {score_color}; font-size: 1.2em'>{match['score']:.1%}</span>", 
                           unsafe_allow_html=True)
    else:
        st.warning("⚠️ No matching loads found")
    
    # Recommendation
    recommendation = result.get('recommendation', 'Unknown')
    st.subheader("🎯 AI Recommendation")
    
    rec_colors = {
        'auto_approve': '#28a745',
        'human_review': '#ffc107', 
        'create_lead': '#17a2b8',
        'reject': '#dc3545'
    }
    
    rec_color = rec_colors.get(recommendation.lower(), '#6c757d')
    st.markdown(f"""
    <div style='background: {rec_color}20; border-left: 4px solid {rec_color}; padding: 1rem; border-radius: 4px;'>
        <h4 style='color: {rec_color}; margin: 0;'>📋 {recommendation.replace('_', ' ').title()}</h4>
    </div>
    """, unsafe_allow_html=True)

def view_loads_page():
    st.header("📋 Available Loads")
    
    if st.session_state.loads:
        loads_data = []
        for load in st.session_state.loads:
            loads_data.append({
                'ID': load.id,
                'Truck Type': load.truck_type.title(),
                'Tonnage': str(load.tonnage),
                'Length': f"{load.length}ft",
                'Product': load.product,
                'Price': f"₹{load.price:,}",
                'Available': '✅ Yes' if load.availability else '❌ No'
            })
        
        df = pd.DataFrame(loads_data)
        st.dataframe(df, use_container_width=True)
        
        st.info(f"📊 Total loads: {len(loads_data)} | Available: {sum(1 for load in st.session_state.loads if load.availability)}")
    else:
        st.warning("No loads available")

def results_history_page():
    st.header("📊 Processing History")
    
    if st.session_state.processing_history:
        history_data = []
        for h in st.session_state.processing_history:
            history_data.append({
                'Time': h['timestamp'].strftime('%H:%M:%S'),
                'Transcript ID': h['transcript_id'],
                'Matches Found': len(h['result']['matches']),
                'Recommendation': h['result'].get('recommendation', 'Unknown').title(),
                'Top Score': f"{max([m['score'] for m in h['result']['matches']], default=0):.1%}"
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # Simple metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Processed", len(st.session_state.processing_history))
        with col2:
            successful = sum(1 for h in st.session_state.processing_history if h['result']['matches'])
            st.metric("With Matches", successful)
        with col3:
            success_rate = (successful / len(st.session_state.processing_history) * 100) if st.session_state.processing_history else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
    else:
        st.info("📈 No processing history yet. Process some transcripts to see data!")

if __name__ == "__main__":
    main()