import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MessageStorage:
    """Handles saving messages to a directory with metadata."""
    
    def __init__(self, base_dir: str = "messages"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        logger.info(f"Message storage initialized at: {self.base_dir.absolute()}")
    
    def save_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        message_type: str = "user_message",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a message to the storage directory.
        
        Args:
            message: The message content to save
            user_id: Optional user identifier
            session_id: Optional session identifier
            message_type: Type of message (user_message, agent_response, etc.)
            metadata: Additional metadata to store
            
        Returns:
            Dictionary with save status and file path
        """
        try:
            # Generate unique message ID
            message_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Create filename with timestamp and message type
            filename = f"{timestamp}_{message_type}_{message_id[:8]}.json"
            
            # Create directory structure: messages/YYYY/MM/DD/
            date_path = self.base_dir / datetime.now().strftime("%Y/%m/%d")
            date_path.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            file_path = date_path / filename
            
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
            
            logger.info(f"Message saved: {file_path}")
            
            return {
                "status": "saved",
                "message_id": message_id,
                "file_path": str(file_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def save_conversation(
        self,
        user_message: str,
        agent_response: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a complete conversation (user message + agent response).
        
        Args:
            user_message: The user's message
            agent_response: The agent's response
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Additional metadata
            
        Returns:
            Dictionary with save status and file path
        """
        try:
            # Generate conversation ID
            conversation_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Create filename
            filename = f"{timestamp}_conversation_{conversation_id[:8]}.json"
            
            # Create directory structure
            date_path = self.base_dir / datetime.now().strftime("%Y/%m/%d")
            date_path.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            file_path = date_path / filename
            
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
            
            logger.info(f"Conversation saved: {file_path}")
            
            return {
                "status": "saved",
                "conversation_id": conversation_id,
                "file_path": str(file_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_messages(
        self,
        user_id: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        List saved messages with optional filtering.
        
        Args:
            user_id: Filter by user ID
            message_type: Filter by message type
            limit: Maximum number of results
            
        Returns:
            Dictionary with list of messages
        """
        try:
            messages = []
            count = 0
            
            # Walk through all JSON files in the messages directory
            for file_path in self.base_dir.rglob("*.json"):
                if count >= limit:
                    break
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Apply filters
                    if user_id and data.get("user_id") != user_id:
                        continue
                    if message_type and data.get("message_type") != message_type:
                        continue
                    
                    messages.append({
                        "file_path": str(file_path),
                        "message_id": data.get("message_id"),
                        "timestamp": data.get("timestamp"),
                        "message_type": data.get("message_type"),
                        "content": data.get("content", data.get("user_message", "")),
                        "user_id": data.get("user_id"),
                        "session_id": data.get("session_id")
                    })
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to read message file {file_path}: {e}")
                    continue
            
            return {
                "status": "success",
                "messages": messages,
                "count": len(messages),
                "total_found": count
            }
            
        except Exception as e:
            logger.error(f"Failed to list messages: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Global message storage instance
message_storage = MessageStorage() 