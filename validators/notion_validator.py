#!/usr/bin/env python3
"""
Notion Entry Validator

Validates that Notion entries actually exist in the database before allowing
destructive file operations (archiving/deletion).

This module prevents data loss by ensuring entries are verified in Notion
before source files are deleted.

Single Responsibility: Verify Notion entries exist
"""

import sys
from pathlib import Path
from typing import Tuple, Optional, List, Dict

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from scripts.notion_manager import AdvancedNotionManager

logger = get_logger(__name__)


class NotionValidator:
    """
    Validates Notion entries before allowing destructive operations.
    
    Prevents data loss by verifying entries actually exist in Notion
    before source files are archived or deleted.
    """
    
    def __init__(self, notion_manager: AdvancedNotionManager):
        """
        Initialize validator with a Notion manager instance.
        
        Args:
            notion_manager: Instance of AdvancedNotionManager for API calls
        """
        self.notion_manager = notion_manager
        logger.debug("✅ NotionValidator initialized")
        
    def verify_entry_exists(self, entry_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verifies a Notion entry actually exists in the database.
        
        Args:
            entry_id: The Notion page ID to verify
            
        Returns:
            Tuple of (exists: bool, error_message: Optional[str])
            - (True, None) if entry exists
            - (False, error_message) if entry doesn't exist or verification fails
        """
        if not entry_id:
            logger.warning("⚠️ Verification called with empty entry_id")
            return False, "No entry ID provided"
            
        try:
            # Query Notion to verify entry exists
            response = self.notion_manager.client.pages.retrieve(page_id=entry_id)
            
            if response and response.get('id') == entry_id:
                logger.debug(f"✅ Verified Notion entry exists: {entry_id[:8]}...")
                return True, None
            else:
                error_msg = "Entry not found in Notion"
                logger.error(f"❌ Verification failed for {entry_id[:8]}...: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Notion verification failed for {entry_id[:8]}...: {error_msg}")
            return False, error_msg
    
    def verify_batch(self, entry_ids: List[str]) -> Dict[str, any]:
        """
        Verifies multiple Notion entries in batch.
        
        Args:
            entry_ids: List of Notion page IDs to verify
            
        Returns:
            Dictionary with verification results:
            {
                'verified': [id1, id2, ...],      # Successfully verified IDs
                'failed': [id3, id4, ...],        # Failed verification IDs
                'errors': {id3: "error msg", ...} # Error messages for failures
            }
        """
        verified = []
        failed = []
        errors = {}
        
        logger.info(f"🔍 Verifying {len(entry_ids)} Notion entries...")
        
        for entry_id in entry_ids:
            exists, error = self.verify_entry_exists(entry_id)
            if exists:
                verified.append(entry_id)
            else:
                failed.append(entry_id)
                if error:
                    errors[entry_id] = error
        
        logger.info(f"✅ Verified: {len(verified)}/{len(entry_ids)} entries")
        if failed:
            logger.warning(f"⚠️ Failed verification: {len(failed)} entries")
        
        return {
            'verified': verified,
            'failed': failed,
            'errors': errors
        }


# For testing purposes
if __name__ == "__main__":
    from core.logging_utils import configure_root_logger
    configure_root_logger("DEBUG")
    
    # Initialize Notion manager
    notion_manager = AdvancedNotionManager()
    
    # Initialize validator
    validator = NotionValidator(notion_manager)
    
    # Test with a fake ID (should fail)
    exists, error = validator.verify_entry_exists("fake-id-12345")
    print(f"Test 1 - Fake ID: exists={exists}, error={error}")
    
    # Test with empty ID (should fail)
    exists, error = validator.verify_entry_exists("")
    print(f"Test 2 - Empty ID: exists={exists}, error={error}")
    
    print("\n✅ NotionValidator module test complete")

