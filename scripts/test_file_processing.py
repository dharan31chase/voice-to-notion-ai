#!/usr/bin/env python3
"""
Test script for file processing logic
Tests both single and multiple task scenarios
"""

import sys
import os
import tempfile
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_transcripts import process_transcript_file

def test_file_processing():
    """Test file processing with both single and multiple tasks"""
    
    print("🧪 Testing File Processing Logic")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Single Task",
            "content": "Email the plumber about repairs. Life Admin HQ. Task",
            "expected_type": "single"
        },
        {
            "name": "Multiple Tasks", 
            "content": "Email plumber. Task. Call electrician. Task. Life Admin HQ. Task",
            "expected_type": "multiple"
        },
        {
            "name": "Single Note",
            "content": "Meeting notes from today's discussion. Product Strategy. Note",
            "expected_type": "single"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Content: {test_case['content']}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_case['content'])
            temp_file_path = Path(f.name)
        
        try:
            # Process the file
            result = process_transcript_file(temp_file_path)
            
            # Check if result is list (multiple) or dict (single)
            if isinstance(result, list):
                result_type = "multiple"
                print(f"✅ Result: Multiple tasks ({len(result)} tasks)")
            else:
                result_type = "single"
                print(f"✅ Result: Single analysis ({result.get('category', 'unknown')})")
            
            # Check if result matches expectation
            expected = test_case['expected_type']
            if result_type == expected:
                print(f"🎯 PASS: Expected {expected}, got {result_type}")
                results.append(True)
            else:
                print(f"❌ FAIL: Expected {expected}, got {result_type}")
                results.append(False)
            
            # Check if processed file was created
            processed_file = Path("processed") / f"{temp_file_path.stem}_processed.json"
            if processed_file.exists():
                print(f"✅ Processed file created: {processed_file.name}")
                
                # Read and display JSON structure
                import json
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                
                if "analyses" in data:
                    print(f"   📁 JSON Structure: Multiple analyses ({len(data['analyses'])} tasks)")
                elif "analysis" in data:
                    print(f"   📁 JSON Structure: Single analysis")
                else:
                    print(f"   ⚠️ Unknown JSON structure")
                    
            else:
                print(f"❌ Processed file not created")
                results.append(False)
                
        except Exception as e:
            print(f"💥 ERROR: {e}")
            results.append(False)
        finally:
            # Clean up
            temp_file_path.unlink(missing_ok=True)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FILE PROCESSING TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 File processing is working correctly!")
        return True
    else:
        print("⚠️ Some issues to address")
        return False

if __name__ == "__main__":
    print("🚀 Starting File Processing Tests...")
    success = test_file_processing()
    
    if success:
        print("\n✅ Step 2 implementation is working!")
    else:
        print("\n❌ Please fix issues before proceeding.")
