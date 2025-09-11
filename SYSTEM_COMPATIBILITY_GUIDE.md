# TRUCKING LOAD MATCHER - SYSTEM COMPATIBILITY GUIDE
## Auto-generated from existing codebase

This document serves as the definitive reference for writing compatible code.
ALL new code must follow these exact interfaces and data structures.

## MODELS (Data Structures)

### load_model.py
**File**: `models/load_model.py`

#### Class: LoadStatus
**Inherits from**: str, Enum
**Fields**:
- `AVAILABLE: unknown` = assigned
- `ASSIGNED: unknown` = assigned
- `COMPLETED: unknown` = assigned
- `CANCELLED: unknown` = assigned
**Methods**:

#### Class: Load
**Inherits from**: BaseModel
**Fields**:
- `id: str` = complex_default
- `booking_office: str` = complex_default
- `message_id: str` = complex_default
- `timestamp: datetime` = complex_default
- `from_location: str` = complex_default
- `to_location: str` = complex_default
- `truck_type: str` = complex_default
- `truck_length: Optional[str]` = complex_default
- `tonnage: Optional[str]` = complex_default
- `product: str` = complex_default
- `price: Optional[float]` = complex_default
- `num_trucks: int` = complex_default
- `eta: str` = complex_default
- `status: LoadStatus` = complex_default
- `assigned_to: Optional[str]` = complex_default
**Methods**:

#### Class: Config
**Fields**:
- `json_encoders: unknown` = assigned
**Methods**:

---

### transcript_model.py
**File**: `models/transcript_model.py`

#### Class: ConversationTurn
**Inherits from**: BaseModel
**Fields**:
- `speaker: str` = complex_default
- `text: str` = complex_default
- `timestamp: Optional[float]` = complex_default
**Methods**:

#### Class: Transcript
**Inherits from**: BaseModel
**Fields**:
- `conversation_text: str` = complex_default
- `turns: Optional[list[ConversationTurn]]` = complex_default
- `timestamp: Optional[float]` = complex_default
- `call_duration: Optional[int]` = complex_default
- `call_id: Optional[str]` = complex_default
- `participants: Optional[list[str]]` = complex_default
**Methods**:

#### Class: Config
**Fields**:
- `extra: unknown` = assigned
**Methods**:

---

### __init__.py
**File**: `models/__init__.py`

---

### entities_model.py
**File**: `models/entities_model.py`

#### Class: TruckType
**Inherits from**: str, Enum
**Fields**:
- `OPEN: unknown` = assigned
- `CONTAINER: unknown` = assigned
- `CLOSED: unknown` = assigned
- `MULTI_AXLE: unknown` = assigned
- `SINGLE_AXLE: unknown` = assigned
**Methods**:

#### Class: ExtractedEntities
**Inherits from**: BaseModel
**Fields**:
- `truck_type: Optional[TruckType]` = complex_default
- `truck_length: Optional[int]` = complex_default
- `tonnage: Optional[float]` = complex_default
- `current_location: Optional[str]` = complex_default
- `preferred_routes: List[str]` = complex_default
- `expected_rate: Optional[float]` = complex_default
- `rate_flexibility: Optional[str]` = complex_default
- `available_immediately: bool` = complex_default
- `availability_constraints: List[str]` = complex_default
- `phone_number: Optional[str]` = complex_default
- `special_requirements: List[str]` = complex_default
- `confidence_scores: Dict[str, float]` = complex_default
**Methods**:

#### Class: MatchingResult
**Inherits from**: BaseModel
**Fields**:
- `load_id: str` = complex_default
- `trucker_requirements_id: str` = complex_default
- `overall_score: float` = complex_default
- `detailed_scores: Dict[str, float]` = complex_default
- `mandatory_match: bool` = complex_default
- `recommendation: str` = complex_default
- `match_reasons: List[str]` = complex_default
- `mismatch_reasons: List[str]` = complex_default
- `price_gap: Optional[float]` = complex_default
- `negotiation_likelihood: float` = complex_default
**Methods**:

---

## AGENTS (Processing Logic)

### entity_extraction_agent.py
**File**: `agents/entity_extraction_agent.py`

#### Class: EntityExtractionAgent
**Key Methods**:
- `extract_entities(transcript)`
- `extract_entities_with_knowledge(transcript)`

---

### load_matching_agent.py
**File**: `agents/load_matching_agent.py`

#### Class: LoadMatchingAgent
**Key Methods**:
- `find_matching_loads(trucker_requirements, available_loads)`
- `get_best_match(trucker_requirements, available_loads)`

---

### __init__.py
**File**: `agents/__init__.py`

---

### entity_extraction_agent_backup.py
**File**: `agents/entity_extraction_agent_backup.py`

#### Class: EntityExtractionAgent
**Key Methods**:
- `extract_entities(transcript)`

---

## UTILITIES

### text_processing.py
**File**: `utils/text_processing.py`

#### Class: TextProcessor
- `clean_text(text)`
- `normalize_units(text)`

**Functions**:
- `clean_text(self, text)`
- `normalize_units(self, text)`
---

### __init__.py
**File**: `utils/__init__.py`

---

### fuzzy_matching.py
**File**: `utils/fuzzy_matching.py`

#### Class: FuzzyMatcher
- `find_best_match(query, choices, scorer)`
- `find_all_matches(query, choices, limit)`

**Functions**:
- `find_best_match(self, query, choices, scorer)`
- `find_all_matches(self, query, choices, limit)`
---

## CRITICAL INTERFACES FOR MAIN.PY

Based on the codebase scan, any main.py orchestrator MUST:

### Entity Extraction Interface
```python
# Your EntityExtractionAgent expects:
extracted_entities = entity_agent.extract_entities(transcript_object)
# Where transcript_object has .turns attribute
```

### Load Matching Interface  
```python
# Your LoadMatchingAgent expects:
load_matches = load_agent.match_loads(extracted_entities, available_loads)
```

### Data Model Requirements
- ExtractedEntities: Use EXACT field names from models/entities_model.py
- Load: Use EXACT field names from models/load_model.py  
- Transcript: Must have .turns attribute with ConversationTurn objects

### Import Statements (Copy exactly)
```python
from agents.entity_extraction_agent import EntityExtractionAgent
from agents.load_matching_agent import LoadMatchingAgent
from models.transcript_model import Transcript, ConversationTurn
from models.load_model import Load, LoadStatus
from models.entities_model import ExtractedEntities, TruckType
```

