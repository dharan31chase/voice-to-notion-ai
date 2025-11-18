#!/usr/bin/env python3
"""
Backfill Roadmap database with all Strategy Board initiatives
Avoids creating duplicates by checking if Roadmap entry already exists
"""

import os
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

notion = Client(auth=os.getenv('NOTION_TOKEN'))
strategy_board_id = os.getenv('STRATEGY_BOARD_DATABASE_ID')
roadmap_db_id = os.getenv('NOTION_ROADMAP_DB')
user_id = os.getenv('NOTION_USER_ID')

def backfill_roadmap():
    """Backfill Roadmap with all Strategy Board initiatives"""

    print("="*70)
    print("ROADMAP BACKFILL - Strategy Board → Roadmap")
    print("="*70)
    print()

    # 1. Get all Strategy Board initiatives
    print("Step 1: Fetching all Strategy Board initiatives...")
    all_initiatives = []
    has_more = True
    start_cursor = None

    while has_more:
        response = notion.databases.query(
            database_id=strategy_board_id,
            start_cursor=start_cursor
        )
        all_initiatives.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')

    print(f"✅ Found {len(all_initiatives)} initiatives in Strategy Board")
    print()

    # 2. Get all existing Roadmap entries
    print("Step 2: Fetching existing Roadmap entries...")
    existing_roadmap = []
    has_more = True
    start_cursor = None

    while has_more:
        response = notion.databases.query(
            database_id=roadmap_db_id,
            start_cursor=start_cursor
        )
        existing_roadmap.extend(response.get('results', []))
        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')

    # Build set of initiative IDs that already have Roadmap entries
    existing_initiative_ids = set()
    for roadmap_entry in existing_roadmap:
        strategy_board_relation = roadmap_entry['properties'].get('🎯 Strategy Board', {}).get('relation', [])
        for relation in strategy_board_relation:
            existing_initiative_ids.add(relation['id'])

    print(f"✅ Found {len(existing_roadmap)} existing Roadmap entries")
    print(f"✅ {len(existing_initiative_ids)} initiatives already have Roadmap entries")
    print()

    # 3. Create Roadmap entries for initiatives that don't have one
    print("Step 3: Creating Roadmap entries for missing initiatives...")
    print()

    created_count = 0
    skipped_count = 0
    error_count = 0

    for initiative in all_initiatives:
        initiative_id = initiative['id']

        # Get initiative name
        title_prop = initiative['properties'].get('Initiative Name', {})
        if title_prop.get('title'):
            initiative_name = title_prop['title'][0]['text']['content']
        else:
            initiative_name = "Unnamed Initiative"

        # Get status
        status_prop = initiative['properties'].get('Status', {}).get('select', {})
        status = status_prop.get('name', 'No status')

        # Check if already exists in Roadmap
        if initiative_id in existing_initiative_ids:
            print(f"⏭️  SKIP: '{initiative_name}' (Status: {status}) - Already in Roadmap")
            skipped_count += 1
            continue

        # Create Roadmap entry
        try:
            roadmap_properties = {
                "Initiative Name": {
                    "title": [{"text": {"content": initiative_name}}]
                },
                "🎯 Strategy Board": {
                    "relation": [{"id": initiative_id}]
                }
            }

            # Add Owner if NOTION_USER_ID is set
            if user_id:
                roadmap_properties["Owner"] = {
                    "people": [{"object": "user", "id": user_id}]
                }

            roadmap_page = notion.pages.create(
                parent={"database_id": roadmap_db_id},
                properties=roadmap_properties
            )

            print(f"✅ CREATE: '{initiative_name}' (Status: {status})")
            print(f"   URL: {roadmap_page.get('url', 'N/A')}")
            created_count += 1

        except Exception as e:
            print(f"❌ ERROR: '{initiative_name}' - {str(e)}")
            error_count += 1

    # 4. Summary
    print()
    print("="*70)
    print("BACKFILL SUMMARY")
    print("="*70)
    print(f"Total initiatives in Strategy Board: {len(all_initiatives)}")
    print(f"Already in Roadmap (skipped):        {skipped_count}")
    print(f"Created new Roadmap entries:         {created_count}")
    print(f"Errors:                              {error_count}")
    print()

    if created_count > 0:
        print("🎉 Roadmap backfill complete!")
        print()
        print("Next steps:")
        print("1. Open Roadmap database in Notion")
        print("2. Verify rollups are calculating correctly:")
        print("   - Start Date (from Sessions)")
        print("   - End Date (formula)")
        print("   - Total Execution Time (from Sessions)")
        print("   - Status (from Strategy Board)")
        print("3. Check that Sessions auto-appear via relation chain")
    elif skipped_count == len(all_initiatives):
        print("ℹ️  All initiatives already have Roadmap entries - nothing to backfill!")

    print()
    print("="*70)

if __name__ == "__main__":
    backfill_roadmap()
