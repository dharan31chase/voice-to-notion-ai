#!/usr/bin/env python3
"""
Test script for the new category detection logic
Run this to validate the updated analyze_transcript function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from process_transcripts import analyze_transcript

def test_category_detection():
    """Test various transcript formats to validate category detection"""
    
    print("🧪 Testing Category Detection Logic")
    print("=" * 60)
    
    # Test cases based on your requirements
    test_cases = [
        # Single Task Tests
        {
            "name": "Single Task - Standard Format",
            "input": "Email the plumber about repairs. Life Admin HQ. Task",
            "expected": "single_task"
        },
        {
            "name": "Single Task - Alternative Format", 
            "input": "Email the plumber about repairs. Task. Life Admin HQ",
            "expected": "single_task"
        },
        
        # Multiple Task Tests
        {
            "name": "Multiple Tasks - Standard Format",
            "input": "Email plumber. Task. Call electrician. Task. Life Admin HQ. Task",
            "expected": "multiple_tasks"
        },
        {
            "name": "Multiple Tasks - With Commas",
            "input": "Email plumber, Task. Call electrician. Task. Life Admin HQ. Task",
            "expected": "multiple_tasks"
        },
        
        # Note Tests
        {
            "name": "Single Note - Standard Format",
            "input": "Meeting notes from today's discussion. Product Strategy. Note",
            "expected": "note"
        },
        {
            "name": "Single Note - Alternative Format",
            "input": "Meeting notes from today's discussion. Note. Product Strategy",
            "expected": "note"
        },
        
        # Edge Cases
        {
            "name": "Missing Periods",
            "input": "Email plumber Task Life Admin HQ Task",
            "expected": "single_task"
        },
        {
            "name": "Extra Punctuation",
            "input": "Email plumber... Task. Life Admin HQ. Task!",
            "expected": "single_task"
        },
        
        # Real Examples from Your Transcripts
        {
            "name": "Real Example 1",
            "input": "Task Simplify calendar workflow Using voice recorder Task Product Craftsman",
            "expected": "single_task"
        },
        {
            "name": "Real Example 2", 
            "input": "Demo notion workflow to Peter task improving second brain improved notion second brain ultimate notion second brain",
            "expected": "unclear"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        
        try:
            # Run the analysis
            result = analyze_transcript(test_case['input'])
            
            # Determine what type of result we got
            if isinstance(result, list):
                result_type = "multiple_tasks"
                task_count = len(result)
                print(f"✅ Result: {result_type} ({task_count} tasks)")
                
                for j, task in enumerate(result, 1):
                    print(f"   Task {j}: {task.get('title', 'No title')}")
                    print(f"   Project: {task.get('project', 'No project')}")
                    print(f"   Manual Review: {task.get('manual_review', False)}")
                    
            elif isinstance(result, dict):
                if result.get('category') == 'note':
                    result_type = "note"
                elif result.get('category') == 'task':
                    if result.get('manual_review', False):
                        result_type = "unclear"
                    else:
                        result_type = "single_task"
                else:
                    result_type = "unknown"
                
                print(f"✅ Result: {result_type}")
                print(f"   Title: {result.get('title', 'No title')}")
                print(f"   Project: {result.get('project', 'No project')}")
                print(f"   Manual Review: {result.get('manual_review', False)}")
            
            # Check if result matches expectation
            expected = test_case['expected']
            if result_type == expected:
                print(f"🎯 PASS: Expected {expected}, got {result_type}")
                results.append(True)
            else:
                print(f"❌ FAIL: Expected {expected}, got {result_type}")
                results.append(False)
                
        except Exception as e:
            print(f"💥 ERROR: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT: Category detection is working well!")
        return True
    elif success_rate >= 70:
        print("⚠️ GOOD: Some issues to address before proceeding")
        return False
    else:
        print("🚨 POOR: Significant issues need fixing")
        return False

if __name__ == "__main__":
    print("🚀 Starting Category Detection Tests...")
    success = test_category_detection()
    
    if success:
        print("\n✅ Ready to proceed to Step 2!")
    else:
        print("\n❌ Please fix issues before proceeding to Step 2.")
