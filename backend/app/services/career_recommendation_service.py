import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import pickle
import random
from .peer_matching_service import parse_embedding
import pinecone
import re
from app.models.user_profile import UserProfile
from app.services.embedding_service import generate_embedding

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to ML models
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
CAREER_MODEL_PATH = os.path.join(MODEL_DIR, "career_recommender_model.pkl")

# Load models if they exist
try:
    with open(CAREER_MODEL_PATH, 'rb') as f:
        CAREER_MODEL = pickle.load(f)
    
    logger.info("Career recommendation model loaded successfully")
    MODEL_LOADED = True
except Exception as e:
    logger.error(f"Error loading career recommendation model: {str(e)}")
    MODEL_LOADED = False

# Extended list of career options with more diverse roles
# This list is for fallback only if Pinecone is unavailable
CAREER_OPTIONS = [
    {"id": 1, "title": "Software Engineer", "description": "Develops software solutions for various applications and systems. Works with programming languages to create, test, and maintain software."},
    {"id": 2, "title": "Data Scientist", "description": "Analyzes and interprets complex data to help guide business decisions. Uses statistical analysis, machine learning, and data visualization."},
    {"id": 3, "title": "UX Designer", "description": "Creates user-friendly interfaces and experiences for products. Conducts user research and testing to optimize digital experiences."},
    {"id": 4, "title": "Product Manager", "description": "Oversees product development from conception to launch. Coordinates teams, sets roadmaps, and ensures products meet user needs."},
    {"id": 5, "title": "Digital Marketing Manager", "description": "Develops and implements online marketing strategies. Uses SEO, social media, content marketing, and analytics to drive growth."},
    {"id": 6, "title": "Business Analyst", "description": "Analyzes business needs and helps implement solutions. Bridges the gap between business stakeholders and technology teams."},
    {"id": 7, "title": "DevOps Engineer", "description": "Manages the infrastructure and deployment pipelines. Automates processes and ensures smooth operation of tech systems."},
    {"id": 8, "title": "AI Engineer", "description": "Develops artificial intelligence systems and applications. Works on machine learning models, neural networks, and AI algorithms."},
    {"id": 9, "title": "Cybersecurity Specialist", "description": "Protects systems from threats and vulnerabilities. Conducts security assessments, monitors systems, and responds to incidents."},
    {"id": 10, "title": "Cloud Architect", "description": "Designs and implements cloud computing solutions. Creates robust, scalable, and secure cloud infrastructure."}
]

# Default user embeddings for various interests (to use when a user has no embedding)
# Using 384 dimensions which is the standard for all-MiniLM-L6-v2
DEFAULT_USER_EMBEDDINGS = {
    # These are simplified vectors - in a real system, these would be generated
    # from typical user profiles in each interest area
    "tech": [0.1] * 384,  # Technology focused 
    "creative": [0.2] * 384,  # Creative/design focused
    "business": [0.3] * 384,  # Business/management focused
    "science": [0.4] * 384,  # Science/research focused
    "healthcare": [0.5] * 384  # Healthcare focused
}

def get_user_embedding(db: Session, user_id: int) -> Optional[List[float]]:
    """
    Get the embedding for a user by first trying to use the stored embedding,
    then falling back to generating it on-the-fly
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        User embedding or None if not found
    """
    try:
        # First try to get the stored embedding from the database
        query = text("""
            SELECT embedding, name, job_title, industry, skills, interests
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        result = db.execute(query, {"user_id": user_id}).fetchone()
        
        if result:
            logger.info(f"Found user profile for user {user_id}:")
            logger.info(f"Name: {result.name}")
            logger.info(f"Job Title: {result.job_title}")
            logger.info(f"Industry: {result.industry}")
            logger.info(f"Skills: {result.skills}")
            logger.info(f"Interests: {result.interests}")
            
            if result.embedding:
                logger.info(f"Found stored embedding for user {user_id}")
                # Parse the embedding from the database
                if isinstance(result.embedding, str):
                    try:
                        # Handle string representation of list
                        embedding = [float(x) for x in result.embedding.strip('[]').split(',')]
                        logger.info(f"Successfully parsed stored embedding for user {user_id}")
                        logger.info(f"Embedding size: {len(embedding)}")
                        logger.info(f"First 5 values: {embedding[:5]}")
                        return embedding
                    except Exception as e:
                        logger.error(f"Error parsing stored embedding: {str(e)}")
                elif isinstance(result.embedding, list):
                    logger.info(f"Using stored embedding list for user {user_id}")
                    logger.info(f"Embedding size: {len(result.embedding)}")
                    logger.info(f"First 5 values: {result.embedding[:5]}")
                    return result.embedding
            else:
                logger.warning(f"No stored embedding found for user {user_id}")
        else:
            logger.warning(f"No user profile found for user {user_id}")
        
        logger.info(f"Generating new embedding for user {user_id}")
        
        # If no stored embedding, get user profile and generate new embedding
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            logger.warning(f"No profile found for user {user_id}")
            return None
            
        # Clean and format skills and interests
        def clean_array(arr):
            if not arr:
                return []
            if isinstance(arr, str):
                # Split by comma and clean each item
                return [item.strip() for item in arr.split(',') if item.strip()]
            if isinstance(arr, list):
                # Clean each item without splitting characters
                return [item.strip() for item in arr if item and isinstance(item, str)]
            return []

        # Generate embedding from profile data
        profile_data = {
            "name": profile.name,
            "age": profile.age,
            "sex": profile.sex,
            "major": profile.major,
            "year": profile.year,
            "gpa": profile.gpa,
            "hobbies": clean_array(profile.hobbies),
            "country": profile.country,
            "state_province": profile.state_province,
            "unique_quality": profile.unique_quality,
            "story": profile.story,
            "favorite_movie": profile.favorite_movie,
            "favorite_book": profile.favorite_book,
            "favorite_celebrities": profile.favorite_celebrities,
            "learning_style": profile.learning_style,
            "interests": clean_array(profile.interests),
            "job_title": profile.job_title,
            "industry": profile.industry,
            "years_experience": profile.years_experience,
            "education_level": profile.education_level,
            "career_goals": profile.career_goals,
            "skills": clean_array(profile.skills)
        }
        
        # Add debug logging
        logger.info(f"Generating new embedding for user {user_id} with profile data:")
        logger.info(f"Job Title: {profile_data['job_title']}")
        logger.info(f"Industry: {profile_data['industry']}")
        logger.info(f"Skills: {profile_data['skills']}")
        logger.info(f"Interests: {profile_data['interests']}")
        
        embedding = generate_embedding(profile_data)
        if embedding is not None:
            logger.info(f"Generated new embedding for user {user_id}")
            logger.info(f"Embedding size: {len(embedding)}")
            logger.info(f"First 5 values: {embedding[:5]}")
            return embedding.tolist()
            
        # If embedding generation fails, try to get a pre-generated embedding
        try:
            embedding_path = os.path.join(MODEL_DIR, f"user_{user_id}_embedding.pkl")
            if os.path.exists(embedding_path):
                with open(embedding_path, 'rb') as f:
                    user_embedding = pickle.load(f)
                logger.info(f"Loaded pre-generated embedding for user {user_id}")
                return user_embedding
        except Exception as e:
            logger.warning(f"Could not load pre-generated embedding: {str(e)}")
        
        # If all else fails, use a default embedding based on interests
        if profile_data['interests']:
            interests = " ".join(profile_data['interests']).lower()
            logger.info(f"Using interests-based default embedding: {interests}")
            if any(term in interests for term in ["tech", "software", "programming"]):
                return DEFAULT_USER_EMBEDDINGS["tech"]
            elif any(term in interests for term in ["art", "design", "creative"]):
                return DEFAULT_USER_EMBEDDINGS["creative"]
            elif any(term in interests for term in ["business", "management", "finance"]):
                return DEFAULT_USER_EMBEDDINGS["business"]
            elif any(term in interests for term in ["science", "research"]):
                return DEFAULT_USER_EMBEDDINGS["science"]
            elif any(term in interests for term in ["health", "medical"]):
                return DEFAULT_USER_EMBEDDINGS["healthcare"]
        
        # If no profile or no matching interests, use a random default embedding
        embedding = random.choice(list(DEFAULT_USER_EMBEDDINGS.values()))
        logger.info(f"Using random default embedding for user {user_id}")
        return embedding
        
    except Exception as e:
        logger.error(f"Error getting user embedding: {str(e)}")
        return None

def extract_fields_from_text(text: str) -> Dict[str, str]:
    """
    Extract fields from text metadata in Pinecone records
    
    Args:
        text: Raw text metadata from Pinecone
        
    Returns:
        Dictionary of extracted fields
    """
    parsed_fields = {}
    field_pattern = re.compile(r'([\w\s\-:]+):\s+([^.:|]+(?:\|[^.:]+)*)')
    matches = field_pattern.findall(text)
    
    for key, value in matches:
        key_clean = (
            key.strip()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("__", "_")
            .lower()
        )
        parsed_fields[key_clean] = value.strip()
    
    return parsed_fields

def get_pinecone_career_recommendations(embedding: List[float], limit: int = 30) -> List[Dict[str, Any]]:
    """
    Get career recommendations using Pinecone vector search
    
    Args:
        embedding: User embedding
        limit: Maximum number of recommendations
        
    Returns:
        List of career recommendations
    """
    try:
        # Initialize Pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        
        if not pinecone_api_key or not pinecone_environment:
            logger.error("Pinecone API key or environment not set")
            return []
        
        # Initialize Pinecone client
        pc = pinecone.Pinecone(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
        
        # Get the index
        index = pc.Index("oasis-minilm-index")
        
        # Ensure embedding is the right format and size - handle numpy arrays
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        # Log the embedding size and first few values for debugging
        logger.info(f"Query embedding size: {len(embedding)}")
        logger.info(f"First 30 embedding values: {embedding[:30]}")
        
        # Query Pinecone with explicit limit
        try:
            logger.info(f"Querying Pinecone with limit={limit}")
            query_results = index.query(
                namespace="",
                vector=embedding,
                top_k=limit,  # Explicitly set to requested limit
                include_metadata=True
            )
            logger.info(f"Received query results from Pinecone: {type(query_results)}")
            
            # Log the raw response for debugging
            logger.info(f"Raw Pinecone response: {query_results}")
            
            # Check if we got the expected number of results
            matches = []
            if isinstance(query_results, dict):
                matches = query_results.get('matches', [])
            elif hasattr(query_results, 'matches'):
                matches = query_results.matches
            elif hasattr(query_results, 'result') and hasattr(query_results.result, 'matches'):
                matches = query_results.result.matches
            
            logger.info(f"Found {len(matches)} matches from Pinecone")
            if len(matches) < limit:
                logger.warning(f"Got fewer matches ({len(matches)}) than requested ({limit})")
            
            # Log each match for debugging
            for i, match in enumerate(matches):
                match_id = match.get('id', None) if isinstance(match, dict) else getattr(match, 'id', None)
                match_score = match.get('score', 0.0) if isinstance(match, dict) else getattr(match, 'score', 0.0)
                logger.info(f"Match {i+1}: ID={match_id}, Score={match_score}")
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {str(e)}")
            return []
        
        if not matches:
            logger.warning("No matches found in Pinecone response")
            return []
        
        # Extract results
        recommendations = []
        for i, match in enumerate(matches):
            # Handle different match formats - dictionary or object
            match_id = match.get('id', None) if isinstance(match, dict) else getattr(match, 'id', None)
            match_score = match.get('score', 0.0) if isinstance(match, dict) else getattr(match, 'score', 0.0)
            
            if not match_id:
                logger.warning(f"Match at index {i} has no ID, skipping")
                continue
                
            # Extract OASIS code from the ID
            if '-' in match_id:
                oasis_code = match_id.split('-')[1]
            else:
                oasis_code = match_id
                
            # Skip entries without oasis_code
            if not oasis_code:
                logger.warning(f"Could not extract OASIS code from match ID: {match_id}")
                continue
            
            # Get metadata, handling different formats
            metadata = {}
            if isinstance(match, dict):
                metadata = match.get('metadata', {})
            elif hasattr(match, 'metadata'):
                metadata = match.metadata
            
            # Parse text for additional fields
            text = metadata.get('text', '') if isinstance(metadata, dict) else getattr(metadata, 'text', '')
            parsed_fields = extract_fields_from_text(text)
            
            # Create result object with fallbacks for missing fields
            title = parsed_fields.get("oasis_label__final_x", "") or parsed_fields.get("label", "") or f"Job {oasis_code}"
            description = parsed_fields.get("lead_statement", "") or parsed_fields.get("description", "") or "No description available"
            
            recommendation = {
                "id": i + 1,  # Use sequential IDs for the swipe interface
                "oasis_code": oasis_code,
                "title": title,
                "description": description,
                "score": float(match_score),
                "main_duties": parsed_fields.get("main_duties", ""),
                "metadata": parsed_fields
            }
            recommendations.append(recommendation)
            logger.info(f"Added recommendation {i+1}: {title} (score: {match_score})")
        
        logger.info(f"Prepared {len(recommendations)} career recommendations")
        return recommendations
    except Exception as e:
        logger.error(f"Error getting Pinecone career recommendations: {str(e)}")
        return []

def get_career_recommendations_fallback(limit: int = 30) -> List[Dict[str, Any]]:
    """
    Get random career recommendations as a fallback
    
    Args:
        limit: Maximum number of recommendations
        
    Returns:
        List of career recommendations
    """
    try:
        # Select random careers
        selected_careers = random.sample(CAREER_OPTIONS, min(limit, len(CAREER_OPTIONS)))
        
        # Add random scores
        recommendations = []
        for career in selected_careers:
            career_copy = career.copy()
            career_copy["score"] = round(random.uniform(0.5, 0.95), 2)
            recommendations.append(career_copy)
        
        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    except Exception as e:
        logger.error(f"Error getting fallback career recommendations: {str(e)}")
        return []

def get_career_recommendations(db: Session, user_id: int, limit: int = 30) -> List[Dict[str, Any]]:
    """
    Get personalized career recommendations for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of recommendations
        
    Returns:
        List of career recommendations
    """
    try:
        # Get user embedding
        embedding = get_user_embedding(db, user_id)
        
        if not embedding:
            logger.warning(f"No embedding found for user {user_id}, using fallback recommendations")
            return get_career_recommendations_fallback(limit)
        
        # Try to get Pinecone recommendations
        recommendations = get_pinecone_career_recommendations(embedding, limit)
        
        # Fall back to random recommendations if Pinecone fails
        if not recommendations:
            logger.warning(f"Pinecone recommendations failed for user {user_id}, using fallback")
            recommendations = get_career_recommendations_fallback(limit)
        
        return recommendations
    except Exception as e:
        logger.error(f"Error getting career recommendations: {str(e)}")
        return get_career_recommendations_fallback(limit)

def save_career_recommendation(db: Session, user_id: int, career_id: int) -> bool:
    """
    Save a career recommendation for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        career_id: ID of the career
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Try to get the career details from Pinecone first
        # This is needed because career_id in swipe interface might not match the real ID
        # We need to look it up in the recommendations first
        recommendations = get_career_recommendations(db, user_id, 30)
        
        career_details = next((c for c in recommendations if c["id"] == career_id), None)
        
        if not career_details:
            logger.error(f"Career ID {career_id} not found in recommendations for user {user_id}")
            return False
        
        # Generate an oasis code from the Pinecone result
        oasis_code = career_details.get("oasis_code", f"career_{career_id}")
        if not oasis_code.startswith("career_"):
            oasis_code = f"career_{oasis_code}"
        
        # Check if already saved
        query = text("""
            SELECT 1
            FROM saved_recommendations
            WHERE user_id = :user_id AND oasis_code = :oasis_code
        """)
        
        exists = db.execute(query, {"user_id": user_id, "oasis_code": oasis_code}).fetchone()
        
        if exists:
            logger.info(f"Career {oasis_code} already saved for user {user_id}")
            return True
        
        # Insert new saved recommendation with required fields
        query = text("""
            INSERT INTO saved_recommendations 
            (user_id, oasis_code, label, description)
            VALUES (:user_id, :oasis_code, :label, :description)
        """)
        
        db.execute(query, {
            "user_id": user_id,
            "oasis_code": oasis_code,
            "label": career_details["title"],
            "description": career_details["description"]
        })
        db.commit()
        
        logger.info(f"Saved career {oasis_code} for user {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving career recommendation: {str(e)}")
        return False

def get_saved_careers(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Get saved career recommendations for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List of saved career recommendations
    """
    try:
        # Get all saved recommendations for the user
        query = text("""
            SELECT 
                sr.id as id,
                sr.oasis_code as oasis_code,
                sr.label as title,
                sr.description as description,
                sr.saved_at as saved_at
            FROM saved_recommendations sr
            WHERE sr.user_id = :user_id
            ORDER BY sr.saved_at DESC
        """)
        
        result = db.execute(query, {"user_id": user_id}).fetchall()
        
        saved_careers = []
        for row in result:
            # Check if this is from the "Find Your Way" tab
            if row.oasis_code and row.oasis_code.startswith("career_"):
                try:
                    # Extract career_id from oasis_code
                    career_id = row.oasis_code.split("_")[1]
                    
                    saved_careers.append({
                        "id": row.id,
                        "oasis_code": row.oasis_code,
                        "title": row.title,
                        "description": row.description,
                        "saved_at": row.saved_at,
                        "source": "find_your_way"
                    })
                except (ValueError, IndexError):
                    # Not a valid career ID, treat as regular recommendation
                    saved_careers.append({
                        "id": row.id,
                        "oasis_code": row.oasis_code,
                        "title": row.title,
                        "description": row.description,
                        "saved_at": row.saved_at,
                        "source": "recommendation"
                    })
            else:
                # Regular recommendation
                saved_careers.append({
                    "id": row.id,
                    "oasis_code": row.oasis_code,
                    "title": row.title,
                    "description": row.description,
                    "saved_at": row.saved_at,
                    "source": "recommendation"
                })
        
        logger.info(f"Retrieved {len(saved_careers)} saved careers for user {user_id}")
        return saved_careers
    except Exception as e:
        logger.error(f"Error getting saved careers: {str(e)}")
        return [] 