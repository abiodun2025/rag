#!/usr/bin/env python3
"""
Check Messages in PostgreSQL Database
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncpg
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

async def check_messages():
    """Check what messages are stored in the PostgreSQL database."""
    
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return
        
        print("💬 Checking PostgreSQL Database Messages")
        print("=" * 60)
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Check recent messages
        print("\n📨 RECENT MESSAGES:")
        print("-" * 30)
        
        messages = await conn.fetch("""
            SELECT 
                m.id,
                m.role,
                m.content,
                m.created_at,
                s.user_id,
                s.metadata as session_metadata
            FROM messages m
            JOIN sessions s ON m.session_id = s.id
            ORDER BY m.created_at DESC
            LIMIT 20
        """)
        
        if messages:
            print(f"✅ Found {len(messages)} recent messages:")
            print()
            
            for i, msg in enumerate(messages, 1):
                print(f"{i}. 💬 {msg['role'].upper()} Message")
                print(f"   🆔 ID: {msg['id']}")
                print(f"   👤 User ID: {msg['user_id'] or 'Unknown'}")
                print(f"   📅 Created: {msg['created_at']}")
                print(f"   📝 Content: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
                print()
        else:
            print("❌ No messages found in database")
        
        # Check sessions
        print("\n🔄 CONVERSATION SESSIONS:")
        print("-" * 30)
        
        sessions = await conn.fetch("""
            SELECT 
                s.id,
                s.user_id,
                s.created_at,
                s.updated_at,
                s.expires_at,
                COUNT(m.id) as message_count,
                s.metadata
            FROM sessions s
            LEFT JOIN messages m ON s.id = m.session_id
            GROUP BY s.id, s.user_id, s.created_at, s.updated_at, s.expires_at, s.metadata
            ORDER BY s.created_at DESC
            LIMIT 10
        """)
        
        if sessions:
            print(f"✅ Found {len(sessions)} recent sessions:")
            print()
            
            for i, session in enumerate(sessions, 1):
                session_id = str(session['id'])[:8]
                print(f"{i}. 🔄 Session {session_id}...")
                print(f"   👤 User ID: {session['user_id'] or 'Unknown'}")
                print(f"   📅 Created: {session['created_at']}")
                print(f"   🔄 Updated: {session['updated_at']}")
                print(f"   💬 Messages: {session['message_count']}")
                if session['expires_at']:
                    print(f"   ⏰ Expires: {session['expires_at']}")
                if session['metadata'] and session['metadata'] != {}:
                    print(f"   📋 Metadata: {json.dumps(session['metadata'], indent=2)}")
                print()
        else:
            print("❌ No sessions found in database")
        
        # Check message statistics
        print("\n📊 MESSAGE STATISTICS:")
        print("-" * 30)
        
        stats = await conn.fetch("""
            SELECT 
                role,
                COUNT(*) as count,
                AVG(LENGTH(content)) as avg_length,
                MIN(LENGTH(content)) as min_length,
                MAX(LENGTH(content)) as max_length
            FROM messages
            GROUP BY role
            ORDER BY count DESC
        """)
        
        if stats:
            print("✅ Message statistics by role:")
            print()
            
            for stat in stats:
                print(f"   {stat['role'].upper()}:")
                print(f"     📊 Count: {stat['count']}")
                print(f"     📏 Average length: {stat['avg_length']:.0f} characters")
                print(f"     📏 Length range: {stat['min_length']} - {stat['max_length']} characters")
                print()
        
        # Check recent conversation flow
        print("\n🔄 RECENT CONVERSATION FLOW:")
        print("-" * 40)
        
        recent_conv = await conn.fetch("""
            SELECT 
                m.role,
                m.content,
                m.created_at,
                s.user_id
            FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE s.id = (
                SELECT session_id 
                FROM messages 
                ORDER BY created_at DESC 
                LIMIT 1
            )
            ORDER BY m.created_at ASC
            LIMIT 10
        """)
        
        if recent_conv:
            print("✅ Most recent conversation:")
            print()
            
            for msg in recent_conv:
                timestamp = msg['created_at'].strftime("%H:%M:%S")
                role_icon = "👤" if msg['role'] == 'user' else "🤖"
                print(f"{timestamp} {role_icon} {msg['role'].upper()}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                print()
        
        await conn.close()
        
        print("=" * 60)
        print("✅ Message check complete!")
        
    except Exception as e:
        print(f"❌ Error checking messages: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_messages()) 