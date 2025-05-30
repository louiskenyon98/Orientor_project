import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import pinecone
from pinecone import Pinecone
import random
import networkx as nx
from uuid import uuid4
from app.models import UserSkillTree
import openai
import traceback
import json

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Pinecone
PINECONE_INDEX = "esco-368"

class CompetenceTreeService:
    """
    Service pour générer des arbres de compétences personnalisés avec des défis dynamiques.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CompetenceTreeService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialise le service de compétences.
        """
        if self._initialized:
            return
            
        self.pinecone_client = None
        self.index = None
        self.embedding_model = None
        self.gnn_model = None
        
        try:
            # Initialize core components
            if not self._initialize_pinecone():
                logger.error("Failed to initialize Pinecone")
                return
            logger.info("Pinecone initialized successfully")
            
            # Try to initialize optional components
            self._initialize_embedding_model()
            self._initialize_gnn_model()
            
            self._initialized = True
            logger.info("CompetenceTreeService initialized successfully")
        except Exception as e:
            logger.error(f"Error during service initialization: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _initialize_pinecone(self) -> bool:
        """
        Initialise la connexion à Pinecone.
        
        Returns:
            bool: True si l'initialisation a réussi, False sinon
        """
        try:
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                logger.error("Clé API Pinecone non définie dans les variables d'environnement")
                return False
            
            self.pinecone_client = Pinecone(api_key=api_key)
            self.index = self.pinecone_client.Index(PINECONE_INDEX)
            logger.info(f"Connexion à l'index Pinecone '{PINECONE_INDEX}' établie avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _initialize_embedding_model(self):
        """
        Initialise le modèle d'embedding pour la recherche vectorielle.
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Modèle d'embedding initialisé avec succès")
        except Exception as e:
            logger.warning(f"Failed to initialize embedding model: {str(e)}")
            logger.warning(traceback.format_exc())
    
    def _initialize_gnn_model(self):
        """
        Initialize the GNN model for graph traversal.
        """
        try:
            import torch
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "services", "GNN", "best_model_20250520_022237.pt"
            )
            
            if not os.path.exists(model_path):
                logger.warning(f"GNN model file not found: {model_path}")
                return
            
            # Load the checkpoint
            checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
            
            # Initialize the model
            from ..GNN.GraphSage import CareerTreeModel
            self.gnn_model = CareerTreeModel(
                input_dim=384,  # Embedding dimension
                hidden_dim=128,
                output_dim=128,
                dropout=0.2
            )
            
            # Load model weights
            if "model_state_dict" not in checkpoint:
                logger.warning("Checkpoint does not contain 'model_state_dict'")
                return
            
            self.gnn_model.load_state_dict(checkpoint["model_state_dict"])
            self.gnn_model.eval()  # Set to evaluation mode
            
            logger.info("GNN model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize GNN model: {str(e)}")
            logger.warning(traceback.format_exc())
            self.gnn_model = None
    
    def _convert_score_to_similarity(self, score: float) -> float:
        """
        Convertit un score de distance Pinecone en score de similarité.
        
        Args:
            score: Score de distance Pinecone
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        return 1.0 - score
    
    def get_user_embedding(self, db: Session, user_id: int) -> Optional[np.ndarray]:
        """
        Récupère l'embedding de compétences d'un utilisateur depuis la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            np.ndarray: Embedding de l'utilisateur ou None en cas d'échec
        """
        try:
            # Récupérer l'embedding depuis la base de données
            query = text("SELECT esco_embedding FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if not result or not result[0]:
                logger.error(f"Aucun embedding trouvé pour l'utilisateur {user_id}")
                return None
            
            # Convertir la chaîne en tableau numpy
            import ast
            embedding = np.array(ast.literal_eval(result[0]), dtype=np.float32)
            logger.info(f"Embedding récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
            return None
    
    def query_skill_recommendations(self, embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Interroge l'index Pinecone pour obtenir les recommandations de compétences.
        
        Args:
            embedding: Embedding de l'utilisateur
            top_k: Nombre de recommandations à retourner
            
        Returns:
            List[Dict[str, Any]]: Liste des recommandations de compétences
        """
        try:
            if self.index is None:
                logger.info("Index Pinecone non initialisé, tentative d'initialisation...")
                if not self._initialize_pinecone():
                    logger.error("Impossible d'initialiser Pinecone")
                    return []
                logger.info("Index Pinecone initialisé avec succès")
            
            vector = embedding.tolist()
            logger.info(f"Vecteur d'embedding préparé pour la requête Pinecone: {len(vector)} dimensions")
            
            # Interroger Pinecone pour les compétences uniquement
            logger.info("Envoi de la requête à Pinecone...")
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter={"type": {"$eq": "skill"}},
                include_metadata=True
            )
            logger.info(f"Réponse reçue de Pinecone: {len(results.matches)} résultats")
            
            recommendations = []
            for match in results.matches:
                try:
                    similarity = self._convert_score_to_similarity(match.score)
                    recommendation = {
                        "id": match.id,
                        "score": similarity,
                        "metadata": match.metadata
                    }
                    recommendations.append(recommendation)
                    logger.info(f"Recommandation ajoutée: {match.id} (score: {similarity:.2f})")
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du résultat Pinecone {match.id}: {str(e)}")
                    continue
            
            logger.info(f"Récupération de {len(recommendations)} recommandations de compétences réussie")
            return recommendations
        except Exception as e:
            logger.error(f"Erreur lors de la requête Pinecone: {str(e)}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            return []
    
    def _generate_challenge_with_llm(self, skill_label: str, difficulty: str, user_age: int) -> Dict[str, Any]:
        """
        Génère un défi pour une compétence en utilisant un LLM.
        
        Args:
            skill_label: Libellé de la compétence
            difficulty: Niveau de difficulté (débutant, intermédiaire, avancé)
            user_age: Âge de l'utilisateur
            
        Returns:
            Dict[str, Any]: Défi généré par le LLM
        """
        try:
            # Configure OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            if not os.getenv("OPENAI_API_KEY"):
                logger.error("Clé API OpenAI non définie")
                return None

            # Construire le prompt pour le LLM
            prompt = f"""
            Tu dois générer un défi pratique pour développer la compétence "{skill_label}" à un niveau {difficulty}.
            
            Contraintes:
            - Le défi doit être adapté à une personne de {user_age} ans
            - Le défi doit être réalisable en moins d'une semaine
            - Le défi doit être concret et actionnable
            - Le défi doit être mesurable (comment savoir qu'on a réussi)
            
            IMPORTANT: Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte supplémentaire.
            Format JSON requis:
            {{
                "title": "Titre court et accrocheur",
                "description": "Description détaillée en 3-4 phrases",
                "success_criteria": "Comment mesurer le succès",
                "estimated_duration": "Durée estimée en heures",
                "resources_needed": "Ressources nécessaires"
            }}
            """

            # Appeler l'API OpenAI avec le nouveau format
            response = client.chat.completions.create(
                model="gpt-4",  # ou "gpt-3.5-turbo" selon vos besoins
                messages=[
                    {"role": "system", "content": "Tu es un expert en développement de compétences et en création de défis d'apprentissage. Tu réponds UNIQUEMENT en JSON valide, sans aucun texte supplémentaire."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}  # Force JSON response
            )

            # Extraire la réponse
            if not response.choices:
                logger.error("LLM response has no choices")
                return None
                
            challenge_json = response.choices[0].message.content
            logger.debug(f"LLM raw output for {skill_label}: {challenge_json}")
            
            # Valider que la réponse n'est pas vide
            if not challenge_json or not challenge_json.strip():
                logger.error(f"Empty LLM response for skill {skill_label}")
                return None
            
            try:
                # Parser la réponse JSON
                challenge_data = json.loads(challenge_json)
                
                # Valider la structure de la réponse
                required_fields = ["title", "description", "success_criteria", "estimated_duration", "resources_needed"]
                missing_fields = [field for field in required_fields if field not in challenge_data]
                
                if missing_fields:
                    logger.error(f"LLM response missing required fields for skill {skill_label}: {missing_fields}")
                    return None
                
                return challenge_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response for skill {skill_label}: {str(e)}")
                logger.error(f"Raw response: {challenge_json}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la génération du défi avec LLM pour {skill_label}: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def generate_challenge(self, skill_label: str, user_age: int) -> Dict[str, Any]:
        """
        Génère un défi pour une compétence donnée en utilisant un LLM.
        
        Args:
            skill_label: Libellé de la compétence
            user_age: Âge de l'utilisateur
            
        Returns:
            Dict[str, Any]: Défi généré avec récompense XP
        """
        try:
            # Déterminer le niveau de difficulté en fonction de l'âge
            if user_age < 18:
                difficulty = "débutant"
                xp_reward = random.randint(10, 30)
            elif user_age < 25:
                difficulty = "intermédiaire"
                xp_reward = random.randint(20, 50)
            else:
                difficulty = "avancé"
                xp_reward = random.randint(40, 100)
            
            # Générer le défi avec le LLM
            llm_challenge = self._generate_challenge_with_llm(skill_label, difficulty, user_age)
            
            if not llm_challenge:
                # Fallback si le LLM échoue
                logger.warning(f"Utilisation du défi par défaut pour {skill_label}")
                llm_challenge = {
                    "title": f"Maîtrisez {skill_label}",
                    "description": f"Recherchez et suivez un tutoriel en ligne sur {skill_label}. Pratiquez les concepts appris pendant au moins 3 heures.",
                    "success_criteria": "Compléter le tutoriel et créer un petit projet démontrant la compréhension",
                    "estimated_duration": "3-5 heures",
                    "resources_needed": "Accès Internet, ordinateur"
                }
            
            # Construire la réponse finale
            challenge_data = {
                "skill_id": skill_label.replace(" ", "_").lower(),
                "skill_label": skill_label,
                "title": llm_challenge.get("title", f"Défi: {skill_label}"),
                "description": llm_challenge.get("description", f"Pratiquez {skill_label} pendant une semaine."),
                "success_criteria": llm_challenge.get("success_criteria", "Compléter le défi avec succès"),
                "estimated_duration": llm_challenge.get("estimated_duration", "3-5 heures"),
                "resources_needed": llm_challenge.get("resources_needed", "Accès Internet"),
                "xp_reward": xp_reward,
                "difficulty": difficulty
            }
            
            return challenge_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du défi: {str(e)}")
            return None

    def create_skill_tree(self, db: Session, user_id: int, max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """
        Crée un arbre de compétences pour un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            max_depth: Profondeur maximale de l'arbre
            max_nodes_per_level: Nombre maximum de nœuds par niveau
            
        Returns:
            Dict[str, Any]: Arbre de compétences généré
        """
        try:
            # Generate a single UUID for the entire tree
            graph_id = str(uuid4())
            logger.info(f"Generated new graph_id: {graph_id} for user {user_id}")
            
            # Récupérer l'âge de l'utilisateur
            query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            user_age = result[0] if result and result[0] else 25
            logger.info(f"Âge de l'utilisateur {user_id}: {user_age}")
            
            # Récupérer l'embedding de l'utilisateur
            embedding = self.get_user_embedding(db, user_id)
            if embedding is None:
                logger.error(f"Impossible de récupérer l'embedding pour l'utilisateur {user_id}")
                return {}
            logger.info(f"Embedding récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
            
            # Obtenir les recommandations de compétences initiales
            initial_recommendations = self.query_skill_recommendations(embedding, top_k=max_nodes_per_level)
            if not initial_recommendations:
                logger.error(f"Aucune recommandation trouvée pour l'utilisateur {user_id}")
                return {}
            logger.info(f"Recommandations initiales trouvées pour l'utilisateur {user_id}: {len(initial_recommendations)}")
            
            # Initialiser le service de traversée du graphe
            from competenceTree_development.graph_traversal_service import GraphTraversalService
            from competenceTree_development.visualisation.skill_tree_visualization import SkillTreeVisualization
            
            graph_service = GraphTraversalService()
            viz_service = SkillTreeVisualization()
            
            # Obtenir les IDs des compétences initiales
            initial_skill_ids = [rec["id"] for rec in initial_recommendations]
            
            # Traverser le graphe à partir des compétences initiales
            graph_data = graph_service.traverse_graph(
                anchor_node_ids=initial_skill_ids,
                max_depth=max_depth,
                min_similarity=0.7,
                max_nodes_per_level=max_nodes_per_level
            )
            
            if not graph_data.get("nodes"):
                logger.error(f"Aucun nœud trouvé lors de la traversée du graphe pour l'utilisateur {user_id}")
                return {}
            
            # Add graph_id to all nodes and generate challenges
            for node in graph_data["nodes"]:
                node["graph_id"] = graph_id
                
                # Generate challenge for each skill
                skill_label = node.get("label", node["id"])
                challenge_data = self.generate_challenge(skill_label, user_age)
                
                # Add challenge data to node
                node.update({
                    "challenge": challenge_data.get("description", ""),
                    "xp_reward": challenge_data.get("xp_reward", 25),
                    "visible": True if node.get("depth", 0) == 0 else False,
                    "revealed": True if node.get("depth", 0) == 0 else False,
                    "state": "active" if node.get("depth", 0) == 0 else "locked",
                    "notes": ""
                })
            
            # Add graph_id to the graph data
            graph_data["graph_id"] = graph_id
            
            # Generate visualizations
            try:
                # Create Plotly interactive visualization
                plotly_viz = viz_service.visualize_plotly(graph_data)
                
                # Create Matplotlib static visualization
                matplotlib_viz = viz_service.visualize_matplotlib(graph_data)
                
                # Create Streamlit visualization
                streamlit_viz = viz_service.create_streamlit_visualization(graph_data)
                
                # Add visualizations to graph
                graph_data["visualizations"] = {
                    "plotly": plotly_viz,
                    "matplotlib": matplotlib_viz,
                    "streamlit": streamlit_viz
                }
                
                logger.info("Visualisations de l'arbre de compétences générées avec succès")
            except Exception as viz_error:
                logger.error(f"Erreur lors de la génération des visualisations: {str(viz_error)}")
                # Continue even if visualization fails
            
            logger.info(f"Arbre de compétences créé avec succès pour l'utilisateur {user_id} avec graph_id {graph_id}")
            return graph_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'arbre de compétences: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
    
    def save_skill_tree(self, db: Session, user_id: int, tree_data: Dict[str, Any]) -> str:
        """
        Sauvegarde l'arbre de compétences dans la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            tree_data: Données de l'arbre de compétences
            
        Returns:
            str: ID du graphe sauvegardé (UUID)
        """
        try:
            import json
            import numpy as np
            
            # Classe personnalisée pour encoder les objets numpy en JSON
            class NumpyEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, np.ndarray):
                        return obj.tolist()
                    if isinstance(obj, np.integer):
                        return int(obj)
                    if isinstance(obj, np.floating):
                        return float(obj)
                    return super(NumpyEncoder, self).default(obj)
            
            # Nettoyer les données pour s'assurer qu'elles sont sérialisables
            def clean_for_json(data):
                if isinstance(data, dict):
                    return {k: clean_for_json(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [clean_for_json(item) for item in data]
                elif isinstance(data, np.ndarray):
                    return data.tolist()
                elif isinstance(data, (np.integer, np.floating)):
                    return float(data) if isinstance(data, np.floating) else int(data)
                else:
                    return data
            
            # Nettoyer les données avant la sérialisation
            clean_tree_data = clean_for_json(tree_data)
            
            # Get the graph_id from the tree data
            graph_id = tree_data.get("graph_id")
            if not graph_id:
                logger.error("No graph_id found in tree data")
                return None
            
            # Créer une nouvelle instance de UserSkillTree
            skill_tree = UserSkillTree(
                user_id=user_id,
                graph_id=graph_id,  # Use the UUID from tree_data
                tree_data=json.dumps(clean_tree_data, cls=NumpyEncoder)
            )
            
            # Sauvegarder dans la base de données
            db.add(skill_tree)
            db.commit()
            db.refresh(skill_tree)
            
            logger.info(f"Arbre de compétences sauvegardé avec succès pour l'utilisateur {user_id} avec graph_id {graph_id}")
            return graph_id  # Return the UUID
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'arbre de compétences: {str(e)}")
            db.rollback()
            return None 