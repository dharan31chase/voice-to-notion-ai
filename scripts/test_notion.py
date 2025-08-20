import os
from dotenv import load_dotenv
from notion_client import Client

# Load environment variables
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def test_notion_connection():
    try:
        print("Testing Notion connection...")
        me = notion.users.me()
        print(f"✅ Connected as: {me['name']}")
        
        # Test database access
        tasks_db_id = os.getenv("TASKS_DATABASE_ID")
        if tasks_db_id:
            db_info = notion.databases.retrieve(database_id=tasks_db_id)
            print(f"✅ Can access Tasks database: {db_info['title'][0]['plain_text']}")
        else:
            print("❌ No Tasks database ID found")
            
        return True
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        return False

if __name__ == "__main__":
    test_notion_connection()