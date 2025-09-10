# quick_test.py - Simple test to verify setup
print("🚛 Trucking Load Matcher - Setup Test")
print("=" * 50)

try:
    # Test imports
    from models.load_model import Load, LoadStatus
    from models.transcript_model import Transcript, ConversationTurn
    from models.entities_model import ExtractedEntities, TruckType
    print("✅ Model imports successful")
    
    # Test basic functionality
    from datetime import datetime
    
    # Create a simple load
    load = Load(
        id="test_001",
        booking_office="Test BO",
        message_id="test_msg",
        timestamp=datetime.now(),
        from_location="Test From",
        to_location="Test To", 
        truck_type="Open truck",
        product="Test Product",
        eta="same day"
    )
    print("✅ Load model creation successful")
    
    # Create a simple transcript
    transcript = Transcript(
        id="test_transcript",
        turns=[
            ConversationTurn(speaker="A", text="Hello"),
            ConversationTurn(speaker="B", text="Hi there")
        ]
    )
    print("✅ Transcript model creation successful")
    
    print("\n🎉 Setup verification complete!")
    print("📁 Project structure is working correctly")
    print("🚀 Ready to create the agents!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Check that all model files are created correctly")