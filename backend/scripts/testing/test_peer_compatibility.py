#!/usr/bin/env python3
"""
Test script to generate peer compatibility data and verify the system works.
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('.')
sys.path.append('./backend')

from app.utils.database import get_db
from app.models.user_profile import UserProfile
from app.services.peer_matching_service import generate_enhanced_peer_suggestions
from contextlib import contextmanager

@contextmanager
def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

async def test_peer_compatibility():
    """Test peer compatibility feature end-to-end."""
    print("🧪 Testing Peer Compatibility System...")
    
    # 1. Check database connectivity and user profiles
    with get_db_session() as db:
        profiles = db.query(UserProfile).limit(10).all()
        if not profiles:
            print("❌ No user profiles found in database")
            return
        
        print(f"✅ Found {len(profiles)} user profiles")
        
        # 2. Test compatibility generation for first few users
        test_users = profiles[:3]  # Test with first 3 users
        
        for profile in test_users:
            print(f"\n🔄 Testing compatibility for User {profile.user_id} ({profile.name or 'Anonymous'})")
            
            try:
                # Generate enhanced peer suggestions
                success = await generate_enhanced_peer_suggestions(db, profile.user_id, top_n=3)
                
                if success:
                    print(f"✅ Successfully generated peer suggestions for User {profile.user_id}")
                    
                    # Check if suggestions were created
                    from sqlalchemy import text
                    result = db.execute(text("""
                        SELECT suggested_id, similarity 
                        FROM suggested_peers 
                        WHERE user_id = :user_id 
                        ORDER BY similarity DESC
                    """), {"user_id": profile.user_id})
                    
                    suggestions = result.fetchall()
                    if suggestions:
                        print(f"  📊 Generated {len(suggestions)} peer suggestions:")
                        for suggestion in suggestions:
                            print(f"    - User {suggestion.suggested_id}: {suggestion.similarity:.2f} compatibility")
                    else:
                        print(f"  ⚠️  No suggestions found in database")
                        
                else:
                    print(f"❌ Failed to generate peer suggestions for User {profile.user_id}")
                    
            except Exception as e:
                print(f"❌ Error processing User {profile.user_id}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n🎯 Testing Complete!")
    print("\nNext steps:")
    print("1. Start your backend: cd backend && python run.py")
    print("2. Start your frontend: cd frontend && npm run dev")
    print("3. Navigate to homepage and check 'Suggested Allies' section")
    print("4. Go to /peers page to see compatibility matches")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_peer_compatibility())