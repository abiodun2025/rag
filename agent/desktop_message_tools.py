import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DesktopMessageStorage:
    """Message storage that saves to the user's Desktop directory."""
    
    def __init__(self, base_dir: str = "/Users/ola/Desktop/save_message"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Desktop message storage initialized at: {self.base_dir}")
    
    def _get_date_path(self) -> Path:
        """Get the path for today's date."""
        today = datetime.now()
        date_path = self.base_dir / str(today.year) / f"{today.month:02d}"
        date_path.mkdir(parents=True, exist_ok=True)
        return date_path
    
    def save_message(self, message: str, message_type: str = "user_message", 
                    user_id: Optional[str] = None, session_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save a single message to the Desktop directory."""
        try:
            message_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Create filename with timestamp and message ID
            filename = f"{timestamp}_{message_type}_{message_id}.json"
            file_path = self._get_date_path() / filename
            
            # Prepare message data
            message_data = {
                "message_id": message_id,
                "timestamp": timestamp,
                "message_type": message_type,
                "content": message,
                "user_id": user_id,
                "session_id": session_id,
                "metadata": metadata or {}
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(message_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Desktop message saved: {file_path}")
            
            return {
                "status": "saved",
                "message_id": message_id,
                "file_path": str(file_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error saving desktop message: {e}")
            return {"status": "error", "error": str(e)}
    
    def save_conversation(self, user_message: str, agent_response: str,
                         user_id: Optional[str] = None, session_id: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save a conversation to the Desktop directory."""
        try:
            conversation_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Create filename
            filename = f"{timestamp}_conversation_{conversation_id}.json"
            file_path = self._get_date_path() / filename
            
            # Prepare conversation data
            conversation_data = {
                "conversation_id": conversation_id,
                "timestamp": timestamp,
                "user_id": user_id,
                "session_id": session_id,
                "user_message": user_message,
                "agent_response": agent_response,
                "metadata": metadata or {}
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Desktop conversation saved: {file_path}")
            
            return {
                "status": "saved",
                "conversation_id": conversation_id,
                "file_path": str(file_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error saving desktop conversation: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_messages(self, limit: int = 10, message_type: Optional[str] = None,
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        """List saved messages from the Desktop directory."""
        try:
            messages = []
            total_found = 0
            
            # Search through all date directories
            for year_dir in self.base_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                    
                for month_dir in year_dir.iterdir():
                    if not month_dir.is_dir():
                        continue
                        
                    for file_path in month_dir.glob("*.json"):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Apply filters
                            if message_type and data.get("message_type") != message_type:
                                continue
                            if user_id and data.get("user_id") != user_id:
                                continue
                            
                            total_found += 1
                            
                            if len(messages) < limit:
                                messages.append({
                                    "file_path": str(file_path),
                                    "message_id": data.get("message_id"),
                                    "timestamp": data.get("timestamp"),
                                    "message_type": data.get("message_type"),
                                    "content": data.get("content", data.get("user_message", "")),
                                    "user_id": data.get("user_id"),
                                    "session_id": data.get("session_id")
                                })
                                
                        except Exception as e:
                            logger.warning(f"Error reading file {file_path}: {e}")
                            continue
            
            # Sort by timestamp (newest first)
            messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return {
                "status": "success",
                "messages": messages,
                "count": len(messages),
                "total_found": total_found
            }
            
        except Exception as e:
            logger.error(f"Error listing desktop messages: {e}")
            return {"status": "error", "error": str(e)}

# Global instance
desktop_storage = DesktopMessageStorage() 