#!/usr/bin/env python3
"""
Test script for Step 5: Verify & Archive
Tests the orchestrator's verification and archiving logic with existing state
"""

import sys
from pathlib import Path

# Add the scripts directory to Python path
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from recording_orchestrator import RecordingOrchestrator

def test_step5():
    """Test Step 5 with existing state"""
    print("🧪 Testing Step 5: Verify & Archive")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        orchestrator = RecordingOrchestrator()
        
        # Check current state
        if not orchestrator.state.get("current_session"):
            print("❌ No current session found")
            return False
        
        current_session = orchestrator.state["current_session"]
        print(f"📊 Current Session: {current_session['session_id']}")
        print(f"📝 Transcripts Created: {len(current_session.get('transcripts_created', []))}")
        print(f"🤖 AI Processing: {len(current_session.get('ai_processing_success', []))} successful")
        
        # Create mock successful transcripts for testing
        transcripts_folder = orchestrator.transcripts_folder
        successful_transcripts = []
        
        for transcript_name in current_session.get('transcripts_created', []):
            transcript_path = transcripts_folder / transcript_name
            if transcript_path.exists():
                successful_transcripts.append(transcript_path)
                print(f"✅ Found transcript: {transcript_name}")
            else:
                print(f"⚠️ Missing transcript: {transcript_name}")
        
        if not successful_transcripts:
            print("❌ No transcripts found to test with")
            return False
        
        print(f"\n🎯 Testing with {len(successful_transcripts)} transcripts")
        
        # Test Step 5
        print("\n🚀 Running Step 5: Verify & Archive...")
        success = orchestrator.step5_verify_and_archive(successful_transcripts, [])
        
        if success:
            print("✅ Step 5 completed successfully!")
            
            # Show final state
            print("\n📊 Final State Summary:")
            if "previous_sessions" in orchestrator.state:
                for session in orchestrator.state["previous_sessions"]:
                    print(f"   📅 Session: {session['session_id']}")
                    print(f"   🧹 Cleanup Ready: {session.get('cleanup_ready', False)}")
                    print(f"   🗓️ Cleanup Date: {session.get('cleanup_date', 'N/A')}")
            
            print("🔄 Orchestrator ready for next session!")
        else:
            print("❌ Step 5 failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_step5()
    sys.exit(0 if success else 1)
