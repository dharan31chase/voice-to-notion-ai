#!/usr/bin/env python3
"""
Cleanup script for Phase 2 testing.
Deletes test Notion entries created during testing.
"""

import json
import os
from pathlib import Path
from notion_client import Client
from dotenv import load_dotenv

def load_processed_files():
    """Load all processed files to extract Notion IDs"""
    processed_dir = Path("processed")
    if not processed_dir.exists():
        print("❌ No processed directory found")
        return []
    
    processed_files = list(processed_dir.glob("*_processed.json"))
    if not processed_files:
        print("❌ No processed files found")
        return []
    
    entries_to_delete = []
    
    for file_path in processed_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle both single and multiple analysis structures
            if "analysis" in data:
                # Single analysis
                analysis = data["analysis"]
                if "notion_entry_id" in analysis:
                    entries_to_delete.append({
                        "file": file_path.name,
                        "id": analysis["notion_entry_id"],
                        "title": analysis.get("title", "Unknown"),
                        "type": "single"
                    })
            elif "analyses" in data:
                # Multiple analyses
                for i, analysis in enumerate(data["analyses"]):
                    if "notion_entry_id" in analysis:
                        entries_to_delete.append({
                            "file": file_path.name,
                            "id": analysis["notion_entry_id"],
                            "title": analysis.get("title", f"Task {i+1}"),
                            "type": "multiple"
                        })
                        
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
    
    return entries_to_delete

def delete_notion_entries(entries):
    """Delete Notion entries by ID"""
    if not entries:
        print("✅ No entries to delete")
        return
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Notion client
    try:
        notion = Client(auth=os.getenv("NOTION_TOKEN"))
        print(f"✅ Notion client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Notion client: {e}")
        return
    
    deleted_count = 0
    failed_count = 0
    
    print(f"\n🗑️ Deleting {len(entries)} test Notion entries...")
    
    for entry in entries:
        try:
            print(f"   🗑️ Deleting: {entry['title'][:50]}... (ID: {entry['id'][:8]}...)")
            
            # Delete the page
            notion.pages.update(
                page_id=entry["id"],
                archived=True  # Archive instead of hard delete
            )
            
            deleted_count += 1
            print(f"      ✅ Deleted successfully")
            
        except Exception as e:
            print(f"      ❌ Failed to delete: {e}")
            failed_count += 1
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   ✅ Successfully deleted: {deleted_count}")
    print(f"   ❌ Failed to delete: {failed_count}")
    print(f"   📁 Total entries processed: {len(entries)}")

def cleanup_processed_files():
    """Remove processed JSON files"""
    processed_dir = Path("processed")
    if not processed_dir.exists():
        print("❌ No processed directory found")
        return
    
    processed_files = list(processed_dir.glob("*_processed.json"))
    if not processed_files:
        print("✅ No processed files to clean up")
        return
    
    print(f"\n🧹 Cleaning up {len(processed_files)} processed files...")
    
    for file_path in processed_files:
        try:
            file_path.unlink()
            print(f"   🗑️ Deleted: {file_path.name}")
        except Exception as e:
            print(f"   ❌ Failed to delete {file_path.name}: {e}")
    
    print("✅ Cleanup complete")

def main():
    """Main cleanup function"""
    print("🧹 Phase 2 Cleanup Script")
    print("=" * 50)
    
    # Step 1: Load entries to delete
    print("\n📋 Step 1: Loading processed files...")
    entries_to_delete = load_processed_files()
    
    if not entries_to_delete:
        print("✅ No test entries found to clean up")
        return
    
    print(f"📝 Found {len(entries_to_delete)} entries to delete:")
    for entry in entries_to_delete:
        print(f"   - {entry['title'][:50]}... ({entry['type']})")
    
    # Step 2: Confirm deletion
    print(f"\n⚠️ This will delete {len(entries_to_delete)} Notion entries!")
    response = input("Type 'DELETE' to confirm: ")
    
    if response != "DELETE":
        print("❌ Cleanup cancelled")
        return
    
    # Step 3: Delete Notion entries
    print("\n🗑️ Step 2: Deleting Notion entries...")
    delete_notion_entries(entries_to_delete)
    
    # Step 4: Clean up processed files
    print("\n🧹 Step 3: Cleaning up processed files...")
    cleanup_processed_files()
    
    print("\n🎉 Phase 2 cleanup complete!")
    print("✅ Environment reset for Phase 3 testing")

if __name__ == "__main__":
    main()

