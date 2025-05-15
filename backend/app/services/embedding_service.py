import os
import pickle
import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
import joblib
import boto3
from pathlib import Path
from sklearn.decomposition import PCA
import threading
import ast
import uuid

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment detection
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development').lower() == 'production'
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "navigo-finetune-embedder-prod")

# Define model paths based on environment
if IS_PRODUCTION:
    # Production paths (AWS EB)
    MODELS_DIR = "/tmp/models"
    PCA_MODEL_PATH = os.path.join(MODELS_DIR, "pca256.pkl")
else:
    # Development paths (local)
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                             "data_n_notebook", "models")
    PCA_MODEL_PATH = os.path.join(MODELS_DIR, "pca256.pkl")

# Define the model name
MODEL_NAME = "intfloat/e5-base-v2"

class EmbeddingModel(nn.Module):
    def __init__(self, base_model, output_dim=768):
        super().__init__()
        self.base_model = base_model
        self.projection = nn.Linear(base_model.config.hidden_size, output_dim)
        
    def forward(self, **inputs):
        outputs = self.base_model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]  # Use [CLS] token
        return self.projection(embeddings)

def ensure_model_directory():
    """Ensure the model directory exists in production."""
    if IS_PRODUCTION:
        Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)

def download_from_s3(s3_key: str, local_path: str):
    """Download a file from S3 to local path."""
    try:
        s3 = boto3.client('s3')
        s3.download_file(S3_BUCKET, s3_key, local_path)
        logger.info(f"Downloaded {s3_key} to {local_path}")
    except Exception as e:
        logger.error(f"Error downloading {s3_key}: {str(e)}")
        raise

# Initialize model state
class ModelState:
    def __init__(self):
        self.embedding_model = None
        self.tokenizer = None
        self.pca_model = None
        self.models_loaded = False
        self.use_pca = False
        self._lock = threading.Lock()
    
    def load_models(self):
        """Load models with proper error handling and retry logic."""
        with self._lock:
            if self.models_loaded:
                return True
                
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Load llama-text-embed-v2 model and tokenizer
                    self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                    base_model = AutoModel.from_pretrained(MODEL_NAME)
                    self.embedding_model = EmbeddingModel(base_model, output_dim=768)
                    self.embedding_model.eval()  # Set to evaluation mode
                    logger.info(f"Embedding model {MODEL_NAME} loaded successfully with 768-dim output")
                    
                    # Try to load PCA model if it exists
                    try:
                        if IS_PRODUCTION:
                            ensure_model_directory()
                            download_from_s3("models/pca256.pkl", PCA_MODEL_PATH)
                        
                        self.pca_model = joblib.load(PCA_MODEL_PATH)
                        logger.info("PCA model loaded successfully")
                        self.use_pca = True
                    except Exception as e:
                        logger.warning(f"PCA model not found or could not be loaded: {str(e)}")
                        logger.info("Creating new PCA model for dimension reduction")
                        self.pca_model = PCA(n_components=256)
                        self.use_pca = False
                    
                    self.models_loaded = True
                    logger.info("Models loaded successfully")
                    return True
                    
                except Exception as e:
                    retry_count += 1
                    logger.error(f"Error loading models (attempt {retry_count}/{max_retries}): {str(e)}")
                    if retry_count < max_retries:
                        logger.info("Retrying model loading...")
                        continue
                    else:
                        logger.error("Failed to load models after maximum retries")
                        self.embedding_model = None
                        self.tokenizer = None
                        self.pca_model = None
                        self.models_loaded = False
                        self.use_pca = False
                        return False
    
    def ensure_models_loaded(self):
        """Ensure models are loaded, loading them if necessary."""
        if not self.models_loaded:
            return self.load_models()
        return True

# Create a single instance of ModelState
model_state = ModelState()

# --- Core Functions ---

def fetch_user_data(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Fetch user data from multiple tables to create a comprehensive profile.
    
    Args:
        db: Database session
        user_id: User ID to fetch data for
        
    Returns:
        Dictionary containing user data from multiple tables
    """
    try:
        # Fetch basic profile data
        profile_query = text("""
            SELECT * FROM user_profiles WHERE user_id = :user_id
        """)
        profile_result = db.execute(profile_query, {"user_id": user_id}).fetchone()
        
        if not profile_result:
            logger.error(f"No profile found for user {user_id}")
            return {}
        
        # Convert row to dict
        profile_data = {key: value for key, value in profile_result._mapping.items()}
        
        # Fetch skills data (direct columns with Likert scale ratings)
        skills_query = text("""
            SELECT creativity, leadership, digital_literacy, critical_thinking,
                   problem_solving, analytical_thinking, attention_to_detail,
                   collaboration, adaptability, independence, evaluation,
                   decision_making, stress_tolerance
            FROM users_skills WHERE user_id = :user_id
        """)
        skills_result = db.execute(skills_query, {"user_id": user_id}).fetchone()
        skills_data = {}
        if skills_result:
            skills_data = {key: value for key, value in skills_result._mapping.items()}
        
        # Fetch RIASEC personality scores
        riasec_query = text("""
            SELECT r_score, i_score, a_score, s_score, e_score, c_score, top_3_code
            FROM gca_results WHERE user_id = :user_id
        """)
        riasec_result = db.execute(riasec_query, {"user_id": user_id}).fetchone()
        riasec_data = {}
        if riasec_result:
            riasec_data = {key: value for key, value in riasec_result._mapping.items()}
            
            # Map score columns to full RIASEC names for better readability
            riasec_mapping = {
                'r_score': 'realistic',
                'i_score': 'investigative',
                'a_score': 'artistic',
                's_score': 'social',
                'e_score': 'enterprising',
                'c_score': 'conventional',
                'top_3_code': 'top_3_code'
            }
            
            # Create a mapped version with full names
            riasec_data_mapped = {riasec_mapping.get(key, key): value
                                 for key, value in riasec_data.items()
                                 if key in riasec_mapping}
            riasec_data.update(riasec_data_mapped)
        
        # Optionally fetch saved recommendations for behavioral signals
        recommendations_query = text("""
            SELECT label, all_fields FROM saved_recommendations WHERE user_id = :user_id
        """)
        recommendations_result = db.execute(recommendations_query, {"user_id": user_id}).fetchall()
        saved_recommendations = []
        if recommendations_result:
            saved_recommendations = [
                {"label": row.label, "fields": row.all_fields}
                for row in recommendations_result
            ]
        
        # Combine all data
        combined_data = {
            "profile": profile_data,
            "skills": skills_data,
            "riasec": riasec_data,
            "saved_recommendations": saved_recommendations
        }
        
        return combined_data
        
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        return {}

def preprocess_user_profile(db: Session, user_id: int, profile_data: Dict[str, Any] = None) -> Optional[str]:
    """
    Preprocess user profile data for embedding generation.
    Formats data according to the specified template combining multiple data sources.
    
    Args:
        db: Database session
        user_id: User ID to process
        profile_data: Optional pre-fetched profile data
        
    Returns:
        Formatted text string for embedding generation
    """
    try:
        # If profile_data is not provided, fetch it from the database
        if not profile_data:
            user_data = fetch_user_data(db, user_id)
            if not user_data:
                return None
        else:
            # If profile_data is provided directly (e.g., for new users), structure it
            user_data = {
                "profile": profile_data,
                "skills": {},  # Default empty skills
                "riasec": {},  # Default empty RIASEC
                "saved_recommendations": []
            }
            
            # Try to extract skills if they exist in the provided data
            if "skills" in profile_data:
                if isinstance(profile_data["skills"], dict):
                    user_data["skills"] = profile_data["skills"]
                elif isinstance(profile_data["skills"], list):
                    # Convert list to dict with default ratings
                    user_data["skills"] = {skill: 3 for skill in profile_data["skills"]}
            
            # Try to extract RIASEC if it exists
            if "riasec" in profile_data:
                user_data["riasec"] = profile_data["riasec"]
        
        # Extract profile data
        profile = user_data.get("profile", {})
        
        # Log pour déboguer les données disponibles
        logger.info(f"Données de profil disponibles pour user_id={user_id}:")
        important_fields = ["age", "education_level", "major", "career_goals",
                           "job_title", "industry", "years_experience", "skills",
                           "interests", "hobbies", "learning_style"]
        
        for field in important_fields:
            value = profile.get(field, "")
            if isinstance(value, list) and len(value) > 0:
                logger.info(f"  {field}: {value[:3]}... ({len(value)} éléments)")
            else:
                logger.info(f"  {field}: {value}")
        
        # Extract basic demographic info
        age = profile.get("age", "")
        education_level = profile.get("education_level", "")
        major = profile.get("major", "")
        career_goal = profile.get("career_goals", "")
        learning_style = profile.get("learning_style", "")
        hobbies = profile.get("hobbies", "")
        favorite_book = profile.get("favorite_book", "")
        favorite_celebrity = profile.get("favorite_celebrities", "")
        
        # Extract soft skills (top skills with high ratings)
        skills = user_data.get("skills", {})
        soft_skills = []
        
        # Map of important soft skills to check
        important_soft_skills = [
            "creativity", "leadership", "collaboration", "attention_to_detail",
            "problem_solving", "adaptability", "critical_thinking", "digital_literacy"
        ]
        
        # Add skills with their ratings
        for skill_name in important_soft_skills:
            if skill_name in skills and skills[skill_name] is not None:
                # Format skill name for display (replace underscores with spaces and capitalize)
                display_name = skill_name.replace('_', ' ').title()
                soft_skills.append(f"{display_name} level: {skills[skill_name]}")
        
        # Extract RIASEC profile (top 3 dimensions)
        riasec = user_data.get("riasec", {})
        riasec_items = []
        
        if riasec:
            # Get the main RIASEC scores
            riasec_scores = {
                'Realistic': riasec.get('realistic') or riasec.get('r_score'),
                'Investigative': riasec.get('investigative') or riasec.get('i_score'),
                'Artistic': riasec.get('artistic') or riasec.get('a_score'),
                'Social': riasec.get('social') or riasec.get('s_score'),
                'Enterprising': riasec.get('enterprising') or riasec.get('e_score'),
                'Conventional': riasec.get('conventional') or riasec.get('c_score')
            }
            
            # Filter out None values and sort by score
            sorted_riasec = sorted(
                [(dim, score) for dim, score in riasec_scores.items() if score is not None],
                key=lambda x: x[1],
                reverse=True
            )
            
            # If we have a top_3_code, use it to verify our sorting
            top_3_code = riasec.get('top_3_code')
            
            # Take top 3 dimensions
            for dim, score in sorted_riasec[:3]:
                riasec_items.append(f"{dim}: {score}")
        
        # Extract personal story
        story = profile.get("story", "")
        
        # Extract unique quality
        unique_quality = profile.get("unique_quality", "")
        
        # Format the text according to the specified template
        formatted_text = f"""User profile:
Age: {age}. Education level: {education_level}. Major: {major}.
Career goal: {career_goal}.
Learning style: {learning_style}.
Hobbies: {hobbies}.
Favorite book: {favorite_book}. Favorite celebrity: {favorite_celebrity}.

Soft Skills:
{". ".join(soft_skills)}.

RIASEC profile:
{". ".join(riasec_items)}.

Personal story:
"{story}"

Unique quality: {unique_quality}
"""
        
        logger.info(f"Preprocessed user profile for user {user_id}")
        return formatted_text
        
    except Exception as e:
        logger.error(f"Error preprocessing user profile: {str(e)}")
        return None

def generate_embedding(db: Session, user_id: int, profile_data: Dict[str, Any] = None) -> Optional[np.ndarray]:
    """
    Generate embedding for a user profile using llama-text-embed-v2.
    Returns a 768-dimensional embedding.
    
    Args:
        db: Database session
        user_id: User ID to generate embedding for
        profile_data: Optional pre-fetched profile data
        
    Returns:
        Numpy array containing the embedding vector
    """
    # Ensure models are loaded
    if not model_state.ensure_models_loaded():
        logger.error("Failed to load models, cannot generate embedding.")
        return None

    try:
        # Preprocess the user profile into the required format
        formatted_text = preprocess_user_profile(db, user_id, profile_data)
        if formatted_text is None:
            logger.error(f"Failed to preprocess profile for user {user_id}")
            return None
            
        # Tokenize and generate embeddings
        inputs = model_state.tokenizer(formatted_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            embedding = model_state.embedding_model(**inputs).numpy()
        
        logger.info(f"Generated embedding with shape {embedding.shape}")
        
        # Analyze embedding statistics
        embedding_stats = {
            "min": float(np.min(embedding)),
            "max": float(np.max(embedding)),
            "mean": float(np.mean(embedding)),
            "std": float(np.std(embedding)),
            "zeros": int(np.sum(embedding == 0)),
            "unique_values": len(np.unique(embedding))
        }
        logger.info(f"Embedding statistics: {embedding_stats}")
        
        return embedding[0]  # Return the first (and only) embedding

    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return None

def store_embedding(db: Session, user_id: int, embedding: np.ndarray) -> bool:
    """
    Store user embedding in the database.
    
    Args:
        db: Database session
        user_id: User ID to store embedding for
        embedding: Numpy array containing the embedding vector
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Convert numpy array to list for storage
        embedding_list = embedding.tolist()
        
        # Update the user's profile with the embedding
        db.execute(
            text("""
                UPDATE user_profiles
                SET embedding = :embedding
                WHERE user_id = :user_id
            """),
            {"embedding": embedding_list, "user_id": user_id}
        )
        db.commit()
        
        logger.info(f"Successfully stored embedding for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error storing embedding: {str(e)}")
        db.rollback()
        return False

def process_user_embedding(db: Session, user_id: int, profile_data: Dict[str, Any] = None) -> bool:
    """
    Process user embedding generation and storage.
    
    Args:
        db: Database session
        user_id: User ID to process
        profile_data: Optional pre-fetched profile data
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        embedding = generate_embedding(db, user_id, profile_data)
        if embedding is None:
            return False

        # Store the embedding in the database
        return store_embedding(db, user_id, embedding)
    except Exception as e:
        logger.error(f"Error processing user embedding: {str(e)}")
        return False

def get_user_embedding(db: Session, user_id: int, convert_to_uuid: bool = False) -> Optional[np.ndarray]:
    """
    Get the user's existing embedding from the database.
    
    Args:
        db: Database session
        user_id: User ID (integer)
        convert_to_uuid: Whether to convert the user_id to UUID format for querying
        
    Returns:
        Numpy array containing the embedding vector or None if not found
    """
    try:
        # Si conversion en UUID demandée, créer l'UUID
        query_id = user_id
        if convert_to_uuid:
            user_id_str = str(user_id)
            namespace_uuid = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # UUID namespace DNS
            query_id = str(uuid.uuid5(namespace_uuid, user_id_str))
            logger.info(f"ID utilisateur original: {user_id_str}, UUID généré pour requête: {query_id}")
        
        # Query the user_profiles table for the embedding
        query = text("""
            SELECT embedding
            FROM user_profiles
            WHERE user_id = :user_id
        """)
        result = db.execute(query, {"user_id": query_id}).fetchone()
        
        if not result or not result.embedding:
            logger.warning(f"No embedding found for user {user_id} (query_id: {query_id})")
            return None
            
        # Parse the embedding from the database
        embedding = parse_embedding(result.embedding)
        if embedding is None:
            logger.error(f"Failed to parse embedding for user {user_id} (query_id: {query_id})")
            return None
            
        logger.info(f"Successfully retrieved embedding for user {user_id} (query_id: {query_id})")
        return np.array(embedding)
        
    except Exception as e:
        logger.error(f"Error getting user embedding for user {user_id}: {str(e)}")
        return None

def parse_embedding(embedding_data: Any) -> Optional[np.ndarray]:
    """
    Parse embedding data into a numpy array.
    
    Args:
        embedding_data: Embedding data from the database
        
    Returns:
        Numpy array or None if parsing fails
    """
    try:
        if isinstance(embedding_data, (list, np.ndarray)):
            return np.array(embedding_data)
        elif isinstance(embedding_data, str):
            # Handle string representation of list
            embedding_data = embedding_data.strip()
            if embedding_data.startswith('[') and embedding_data.endswith(']'):
                return np.array([float(x) for x in embedding_data[1:-1].split(',')])
            else:
                # Try using ast.literal_eval for safer parsing
                return np.array(ast.literal_eval(embedding_data))
        else:
            logger.error(f"Unexpected embedding type: {type(embedding_data)}")
            return None
    except Exception as e:
        logger.error(f"Error parsing embedding: {str(e)}")
        return None

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score (between -1 and 1)
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))