#!/usr/bin/env python3
"""
Quick fix script to make timestamp optional in the trucking load matcher system
Run this to update your existing files
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the original file"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backed up {filepath} to {backup_path}")

def update_transcript_model():
    """Update the transcript model to make timestamp optional"""
    
    model_path = "models/transcript_model.py"
    
    if not os.path.exists(model_path):
        print(f"❌ File not found: {model_path}")
        return False
    
    # Backup original
    backup_file(model_path)
    
    new_content = '''from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import time

class ConversationTurn(BaseModel):
    speaker: str = Field(default="unknown", description="Speaker identifier")
    text: str = Field(..., description="What the speaker said")
    timestamp: Optional[float] = Field(default=None, description="When this turn happened (Unix timestamp)")

class Transcript(BaseModel):
    conversation_text: str = Field(..., description="Full conversation text")
    turns: Optional[list[ConversationTurn]] = Field(default=None, description="Structured conversation turns")
    timestamp: Optional[float] = Field(default_factory=lambda: time.time(), description="Call timestamp (defaults to now)")
    call_duration: Optional[int] = Field(default=None, description="Duration in seconds")
    call_id: Optional[str] = Field(default=None, description="Unique call identifier")
    participants: Optional[list[str]] = Field(default=None, description="List of participants")
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"
'''
    
    with open(model_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {model_path}")
    return True

def update_main_py():
    """Update main.py to handle optional timestamp"""
    
    main_path = "main.py"
    
    if not os.path.exists(main_path):
        print(f"❌ File not found: {main_path}")
        return False
    
    # Read current content
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Only update if it hasn't been updated already
    if "time.time()" not in content:
        # Backup original
        backup_file(main_path)
        
        # Simple fix - add time import if not present
        if "import time" not in content:
            content = "import time\n" + content
        
        # Update any hardcoded timestamp creation
        content = content.replace(
            'timestamp=1234567890',
            'timestamp=time.time()'
        )
        
        with open(main_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {main_path}")
    else:
        print(f"✅ {main_path} already looks good")
    
    return True

def test_simple_transcript():
    """Test the system with a simple transcript"""
    
    print("\n🧪 Testing simple transcript processing...")
    
    try:
        # Import after updating
        import sys
        sys.path.append('.')
        
        from main import TruckingLoadMatcher
        from models.transcript_model import Transcript
        
        # Test transcript
        simple_text = "I have a 25 feet open vehicle. If there's anything towards Tamil Nadu side, like Madurai or Coimbatore, tell me"
        
        # This should now work without timestamp
        transcript = Transcript(conversation_text=simple_text)
        
        print(f"✅ Successfully created transcript object")
        print(f"   Text: {transcript.conversation_text[:50]}...")
        print(f"   Timestamp: {transcript.timestamp}")
        print(f"   Duration: {transcript.call_duration}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all fixes"""
    print("🔧 Starting quick fix for optional timestamp...")
    print("=" * 50)
    
    success = True
    
    # Check if we're in the right directory
    if not os.path.exists("models") or not os.path.exists("agents"):
        print("❌ Please run this script from the trucking-load-matcher project root directory")
        return False
    
    # Apply fixes
    success &= update_transcript_model()
    success &= update_main_py()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ All fixes applied successfully!")
        print("\n📝 What changed:")
        print("   • Timestamp is now optional (defaults to current time)")
        print("   • Call duration is optional")
        print("   • Simple text input works without metadata")
        
        print("\n🚀 You can now:")
        print("   • Run: streamlit run app.py")
        print("   • Paste just the conversation text")
        print("   • Processing will work without timestamp/duration")
        
        # Test it
        test_simple_transcript()
        
    else:
        print("\n❌ Some fixes failed. Please check the error messages above.")
        
    return success

if __name__ == "__main__":
    main()