# test_entity_extraction.py
from agents.entity_extraction_agent import EntityExtractionAgent
from models.transcript_model import Transcript, ConversationTurn

# Create test transcript
transcript = Transcript(
    id="test_001",
    turns=[
        ConversationTurn(speaker="B", text="Ours is 8 tons, Madam. It's a wooden vehicle, 8 tons, Madam, 8 tons, 19 feet, 8 tons."),
        ConversationTurn(speaker="A", text="This is 4 tons, 19 feet, this is 4 tons."),
        ConversationTurn(speaker="B", text="Not a container, Madam. It's an open vehicle, we put a tarpaulin on top and close it."),
    ]
)

# Test entity extraction
agent = EntityExtractionAgent()
entities = agent.extract_entities(transcript)

print("🔍 Entity Extraction Test")
print("=" * 40)
print(f"Truck Type: {entities.truck_type}")
print(f"Tonnage: {entities.tonnage}")
print(f"Length: {entities.truck_length}")
print(f"Special Requirements: {entities.special_requirements}")
print(f"Confidence Scores: {entities.confidence_scores}")