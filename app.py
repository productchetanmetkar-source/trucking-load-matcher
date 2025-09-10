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
</style>
""", unsafe_allow_html=True)

def safe_get_attr(obj, attr_name, default="N/A"):
    """Safely get attribute from object"""
    try:
        return getattr(obj, attr_name, default)
    except:
        return default

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
        try:
            st.session_state.orchestrator = TruckingMatchingOrchestrator()
            st.session_state.loads = create_sample_loads()
            st.session_state.processing_history = []
            st.success("✅ System initialized successfully!")
        except Exception as e:
            st.error(f"❌ System initialization failed: {e}")
            st.info("💡 Make sure `python main.py` works first")
            return
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    page = st.sidebar.selectbox("Select Page", [
        "📞 Process Transcript",
        "📋 View Loads",
        "📊 Results History",
        "🔍 Debug Info"
    ])
    
    # Show basic stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 System Stats")
    st.sidebar.metric("Available Loads", len(st.session_state.loads))
    st.sidebar.metric("Processed Calls", len(st.session_state.processing_history))
    
    # Route to selected page
    if page == "📞 Process Transcript":
        process_transcript_page()
    elif page == "📋 View Loads":
        view_loads_page()
    elif page == "📊 Results History":
        results_history_page()
    elif page == "🔍 Debug Info":
        debug_info_page()

def process_transcript_page():
    st.header("📞 Process Call Transcript")
    
    # Sample transcripts
    sample_options = {
        "Custom Input": "",
        "Hindi Example": "FO: Namaste sir, main Rajesh bol raha hun\nBO: Haan bhai, kya chahiye?\nFO: Sir mujhe ek 8 tonne ka open truck chahiye\nBO: Route kya hai?\nFO: Mumbai se Delhi jana hai sir\nBO: Phone number?\nFO: 9876543210 sir",
        "English Example": "FO: Hello, I need a container truck\nBO: What capacity?\nFO: 25 tonne container\nBO: Route?\nFO: Mumbai to Delhi, electronics\nBO: Contact?\nFO: +91-8765432109",
        "Mixed Language": "FO: Sir trailer chahiye tha\nBO: Kitna tonne?\nFO: 32 tonne machinery\nBO: Route?\nFO: Chennai to Hyderabad\nBO: Phone?\nFO: 7654321098"
    }
    
    # Select sample
    sample_choice = st.selectbox("Choose Example:", list(sample_options.keys()))
    
    if sample_choice == "Custom Input":
        transcript_text = st.text_area(
            "Enter transcript:",
            placeholder="FO: Hello sir, mujhe truck chahiye...",
            height=150
        )
    else:
        transcript_text = sample_options[sample_choice]
        st.text_area("Selected Example:", transcript_text, height=150, disabled=True)
    
    # Process button
    if st.button("🚀 Process Transcript", type="primary"):
        if transcript_text:
            process_transcript(transcript_text)
        else:
            st.error("Please enter a transcript!")

def process_transcript(transcript_text: str):
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
                caller_phone="+91-9876543210",
                duration_minutes=3,
                booking_office="BO_Web_Interface"
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
            with st.expander("🔍 Error Details"):
                st.code(str(e))
            st.info("💡 Make sure your existing system works: `python main.py`")

def display_results(result: Dict[str, Any]):
    """Display processing results safely"""
    st.success("✅ Transcript processed successfully!")
    
    # Extracted entities
    st.subheader("🔍 Extracted Requirements")
    entities = result['extracted_entities']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚛 Truck Type", safe_get_attr(entities, 'truck_type') or "Not specified")
    with col2:
        tonnage = safe_get_attr(entities, 'tonnage')
        st.metric("⚖️ Tonnage", f"{tonnage}T" if tonnage else "Not specified")
    with col3:
        length = safe_get_attr(entities, 'length')
        st.metric("📏 Length", f"{length}ft" if length else "Not specified")
    with col4:
        phone = safe_get_attr(entities, 'phone_number')
        st.metric("📱 Phone", phone or "Not provided")
    
    # Show confidence scores if available
    confidence = safe_get_attr(entities, 'confidence_scores')
    if confidence and isinstance(confidence, dict):
        st.subheader("🎯 Extraction Confidence")
        conf_cols = st.columns(len(confidence))
        for i, (key, value) in enumerate(confidence.items()):
            with conf_cols[i % len(conf_cols)]:
                st.metric(key.replace('_', ' ').title(), f"{value:.1%}" if isinstance(value, (int, float)) else str(value))
    
    # Matching results
    st.subheader("🎯 Load Matching Results")
    matches = result.get('matches', [])
    
    if matches:
        for i, match in enumerate(matches[:3]):  # Show top 3
            score = match.get('score', 0)
            load = match.get('load')
            
            if load:
                with st.expander(f"🚛 Match #{i+1}: {safe_get_attr(load, 'id')} - {score:.1%}", expanded=i==0):
                    
                    # Display all available load details
                    st.write("**Load Details:**")
                    
                    # Get all attributes safely
                    load_attrs = {}
                    for attr in ['id', 'truck_type', 'tonnage', 'product', 'price', 'availability']:
                        val = safe_get_attr(load, attr)
                        if val != "N/A":
                            load_attrs[attr] = val
                    
                    # Display in a nice format
                    if 'id' in load_attrs:
                        st.write(f"- **ID:** {load_attrs['id']}")
                    if 'truck_type' in load_attrs:
                        st.write(f"- **Truck Type:** {load_attrs['truck_type']}")
                    if 'tonnage' in load_attrs:
                        st.write(f"- **Tonnage:** {load_attrs['tonnage']}")
                    if 'product' in load_attrs:
                        st.write(f"- **Product:** {load_attrs['product']}")
                    if 'price' in load_attrs:
                        st.write(f"- **Price:** ₹{load_attrs['price']:,}" if isinstance(load_attrs['price'], (int, float)) else f"Price: {load_attrs['price']}")
                    if 'availability' in load_attrs:
                        st.write(f"- **Available:** {'✅ Yes' if load_attrs['availability'] else '❌ No'}")
                    
                    # Match score with color
                    if score >= 0.8:
                        color = "#28a745"
                        status = "Excellent Match"
                    elif score >= 0.6:
                        color = "#ffc107" 
                        status = "Good Match"
                    elif score >= 0.4:
                        color = "#17a2b8"
                        status = "Fair Match"
                    else:
                        color = "#dc3545"
                        status = "Poor Match"
                    
                    st.markdown(f"**Match Score:** <span style='color: {color}; font-size: 1.2em; font-weight: bold'>{score:.1%} - {status}</span>", 
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
    
    rec_descriptions = {
        'auto_approve': 'Excellent match - can be automatically assigned',
        'human_review': 'Good match - requires Traffic Incharge review', 
        'create_lead': 'Potential opportunity - add to leads database',
        'reject': 'Poor match - suggest alternatives'
    }
    
    rec_color = rec_colors.get(recommendation.lower(), '#6c757d')
    rec_desc = rec_descriptions.get(recommendation.lower(), 'Processing completed')
    
    st.markdown(f"""
    <div style='background: {rec_color}20; border-left: 4px solid {rec_color}; padding: 1rem; border-radius: 4px;'>
        <h4 style='color: {rec_color}; margin: 0;'>📋 {recommendation.replace('_', ' ').title()}</h4>
        <p style='margin: 0.5rem 0 0 0; color: #666;'>{rec_desc}</p>
    </div>
    """, unsafe_allow_html=True)

def view_loads_page():
    st.header("📋 Available Loads")
    
    if not st.session_state.loads:
        st.warning("No loads available")
        return
    
    # Create safe load data
    loads_data = []
    for i, load in enumerate(st.session_state.loads):
        try:
            # Safely extract all possible attributes
            load_info = {'Index': i + 1}
            
            # Common attributes to check
            attrs_to_check = [
                ('id', 'ID'),
                ('truck_type', 'Truck Type'),
                ('tonnage', 'Tonnage'), 
                ('product', 'Product'),
                ('price', 'Price'),
                ('availability', 'Available'),
                ('length', 'Length'),
                ('from_location', 'From'),
                ('to_location', 'To'),
                ('route_from', 'From'),
                ('route_to', 'To'),
                ('booking_office', 'Booking Office')
            ]
            
            for attr_name, display_name in attrs_to_check:
                value = safe_get_attr(load, attr_name)
                if value != "N/A":
                    if attr_name == 'truck_type':
                        load_info[display_name] = str(value).title()
                    elif attr_name == 'tonnage':
                        load_info[display_name] = f"{value}T" if str(value).replace('.', '').isdigit() else str(value)
                    elif attr_name == 'length':
                        load_info[display_name] = f"{value}ft" if str(value).replace('.', '').isdigit() else str(value)
                    elif attr_name == 'price':
                        if isinstance(value, (int, float)):
                            load_info[display_name] = f"₹{value:,}"
                        else:
                            load_info[display_name] = str(value)
                    elif attr_name == 'availability':
                        load_info[display_name] = '✅ Yes' if value else '❌ No'
                    else:
                        load_info[display_name] = str(value)
            
            loads_data.append(load_info)
            
        except Exception as e:
            # If there's any error with a specific load, show what we can
            loads_data.append({
                'Index': i + 1,
                'ID': f"Load_{i+1}",
                'Status': f'Error: {str(e)[:50]}...'
            })
    
    # Display loads table
    if loads_data:
        df = pd.DataFrame(loads_data)
        st.dataframe(df, use_container_width=True)
        
        # Summary stats
        total_loads = len(loads_data)
        available_count = sum(1 for load_info in loads_data if load_info.get('Available') == '✅ Yes')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📦 Total Loads", total_loads)
        with col2:
            st.metric("✅ Available", available_count)
        with col3:
            st.metric("❌ Unavailable", total_loads - available_count)

def results_history_page():
    st.header("📊 Processing History")
    
    if not st.session_state.processing_history:
        st.info("📈 No processing history yet. Process some transcripts to see data!")
        return
    
    history_data = []
    for h in st.session_state.processing_history:
        try:
            result = h.get('result', {})
            matches = result.get('matches', [])
            
            history_data.append({
                'Time': h['timestamp'].strftime('%H:%M:%S'),
                'Date': h['timestamp'].strftime('%Y-%m-%d'),
                'Transcript ID': h['transcript_id'],
                'Matches Found': len(matches),
                'Top Score': f"{max([m.get('score', 0) for m in matches], default=0):.1%}",
                'Recommendation': result.get('recommendation', 'Unknown').replace('_', ' ').title()
            })
        except Exception as e:
            history_data.append({
                'Time': 'Error',
                'Transcript ID': 'Processing Error',
                'Error': str(e)[:50]
            })
    
    # Display history table
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True)
    
    # Simple metrics
    if history_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📞 Total Processed", len(st.session_state.processing_history))
        with col2:
            successful = sum(1 for h in history_data if h.get('Matches Found', 0) > 0)
            st.metric("✅ With Matches", successful)
        with col3:
            success_rate = (successful / len(history_data) * 100) if history_data else 0
            st.metric("📈 Success Rate", f"{success_rate:.1f}%")

def debug_info_page():
    st.header("🔍 Debug Information")
    
    st.subheader("🏗️ System Status")
    
    # Check system components
    try:
        st.write("✅ Orchestrator:", type(st.session_state.orchestrator).__name__)
        st.write("✅ Loads count:", len(st.session_state.loads))
        st.write("✅ History count:", len(st.session_state.processing_history))
    except Exception as e:
        st.error(f"❌ System status error: {e}")
    
    # Show load model structure
    st.subheader("📦 Load Model Structure")
    if st.session_state.loads:
        sample_load = st.session_state.loads[0]
        
        st.write("**Available attributes:**")
        try:
            # Get all attributes (excluding private ones)
            attributes = [attr for attr in dir(sample_load) if not attr.startswith('_')]
            st.write(attributes)
            
            st.write("**Sample load data:**")
            # Try different ways to display the load data
            try:
                if hasattr(sample_load, 'dict'):
                    st.json(sample_load.dict())
                else:
                    st.write("Load object:", sample_load)
            except Exception as e:
                st.write(f"Could not serialize load data: {e}")
                
                # Try to show individual attributes
                st.write("**Individual attributes:**")
                for attr in attributes[:10]:  # Show first 10 attributes
                    try:
                        value = getattr(sample_load, attr)
                        st.write(f"- {attr}: {value} ({type(value).__name__})")
                    except Exception as attr_e:
                        st.write(f"- {attr}: Error accessing ({attr_e})")
                        
        except Exception as e:
            st.error(f"Error inspecting load model: {e}")
    
    # Test basic functions
    st.subheader("🧪 Function Tests")
    if st.button("Test create_sample_loads()"):
        try:
            test_loads = create_sample_loads()
            st.success(f"✅ Created {len(test_loads)} sample loads")
            if test_loads:
                st.write("First load type:", type(test_loads[0]).__name__)
        except Exception as e:
            st.error(f"❌ create_sample_loads() failed: {e}")

if __name__ == "__main__":
    main()