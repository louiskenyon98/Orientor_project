# import os
# import logging
# import numpy as np
# import random
# import networkx as nx
# from typing import List, Dict, Any, Optional
# from sqlalchemy.orm import Session
# from sqlalchemy import text
# import pinecone
# from pinecone import Pinecone
# from ..models import UserSkillTree
# from uuid import uuid4
# import torch
# import sys

# # Add the path to import the GNN model
# sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"))
# from GNN.GraphSage import GraphSAGE, CareerTreeModel

# # Configuration du logger
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Configuration Pinecone
# PINECONE_INDEX = "esco-368"

# class CompetenceTreeService:
#     """
#     Service pour générer des arbres de compétences personnalisés avec des défis dynamiques.
#     """
    
#     def __init__(self, index_name: str = "esco-368"):
#         """
#         Initialise le service d'arbre de compétences.
#         """
#         self.api_key = os.getenv("PINECONE_API_KEY")
#         if not self.api_key:
#             raise ValueError("La clé API Pinecone n'est pas définie. Utilisez le paramètre api_key ou définissez la variable d'environnement PINECONE_API_KEY.")
        
#         self.index_name = index_name
#         self.pc = Pinecone(api_key=self.api_key)
#         self.index = self.pc.Index(self.index_name)
#         self.embedding_model = None
#         self._initialize_pinecone()
#         self._initialize_embedding_model()
#         self._initialize_gnn_model()
        
#     def _initialize_embedding_model(self):
#         """
#         Initialise le modèle d'embedding pour la recherche vectorielle.
        
#         Returns:
#             bool: True si l'initialisation a réussi, False sinon
#         """
#         try:
#             from sentence_transformers import SentenceTransformer
#             self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#             logger.info("Modèle d'embedding initialisé avec succès")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de l'initialisation du modèle d'embedding: {str(e)}")
#             return False
    
#     def _initialize_pinecone(self) -> bool:
#         """
#         Initialise la connexion à Pinecone.
        
#         Returns:
#             bool: True si l'initialisation a réussi, False sinon
#         """
#         try:
#             api_key = os.getenv("PINECONE_API_KEY")
#             if not api_key:
#                 logger.error("Clé API Pinecone non définie dans les variables d'environnement")
#                 return False
            
#             self.pinecone_client = Pinecone(api_key=api_key)
#             self.index = self.pinecone_client.Index(PINECONE_INDEX)
#             logger.info(f"Connexion à l'index Pinecone '{PINECONE_INDEX}' établie avec succès")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
#             return False
    
#     def _initialize_gnn_model(self):
#         """Initialize the GNN model for graph traversal."""
#         try:
#             model_path = os.path.join(
#                 os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
#                 "services", "GNN", "best_model_20250520_022237.pt"
#             )
            
#             if not os.path.exists(model_path):
#                 logger.error(f"Le fichier du modèle n'existe pas: {model_path}")
#                 return
            
#             # Load the checkpoint
#             checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
            
#             # Initialize the model
#             self.gnn_model = CareerTreeModel(
#                 input_dim=384,  # Embedding dimension
#                 hidden_dim=128,
#                 output_dim=128,
#                 dropout=0.2
#             )
            
#             # Load model weights
#             if "model_state_dict" not in checkpoint:
#                 logger.error("Le checkpoint ne contient pas 'model_state_dict'")
#                 return
            
#             self.gnn_model.load_state_dict(checkpoint["model_state_dict"])
#             self.gnn_model.eval()  # Set to evaluation mode
            
#             logger.info("Modèle GraphSAGE chargé avec succès")
            
#         except Exception as e:
#             logger.error(f"Erreur lors de l'initialisation du modèle GNN: {str(e)}")
#             self.gnn_model = None
    
#     # Fonction supprimée car non nécessaire pour extraire les top 5
    
#     def get_user_embedding(self, db: Session, user_id: int, embedding_type: str = "esco_embedding_skill") -> Optional[np.ndarray]:
#         """
#         Récupère l'embedding de compétences d'un utilisateur depuis la base de données.
        
#         Args:
#             db: Session de base de données
#             user_id: ID de l'utilisateur
#             embedding_type: Type d'embedding à récupérer (par défaut: esco_embedding_skill)
            
#         Returns:
#             np.ndarray: Embedding de l'utilisateur ou None en cas d'échec
#         """
#         try:
#             # Vérifier que le type d'embedding est valide
#             valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
#             if embedding_type not in valid_types:
#                 logger.error(f"Type d'embedding invalide: {embedding_type}")
#                 return None
            
#             # Récupérer l'embedding depuis la base de données
#             query = text(f"SELECT {embedding_type} FROM user_profiles WHERE user_id = :user_id")
#             result = db.execute(query, {"user_id": user_id}).fetchone()
            
#             if not result or not result[0]:
#                 logger.error(f"Aucun embedding {embedding_type} trouvé pour l'utilisateur {user_id}")
#                 return None
            
#             # Convertir la chaîne en tableau numpy
#             import ast
#             embedding = np.array(ast.literal_eval(result[0]), dtype=np.float32)
#             logger.info(f"Embedding {embedding_type} récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
#             return embedding
#         except Exception as e:
#             logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
#             return None
    
#     def extract_anchor_skills(self, db: Session, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
#         """
#         Extrait les compétences dominantes d'un utilisateur en utilisant son embedding vectoriel.
#         Retourne une liste de dicts contenant l'ID, score, metadata et vecteur de chaque compétence.
#         """
#         try:
#             user_embedding = self.get_user_embedding(db, user_id, "esco_embedding_skill")
#             if user_embedding is None:
#                 logger.error(f"Aucun embedding trouvé pour l'utilisateur {user_id}")
#                 return []

#             if self.index is None and not self._initialize_pinecone():
#                 logger.error("Impossible d'initialiser Pinecone")
#                 return []

#             vector = user_embedding.astype(np.float32).tolist()

#             logger.info(f"Recherche des compétences similaires dans Pinecone pour l'utilisateur {user_id}")
#             results = self.index.query(
#                 vector=vector,
#                 top_k=top_k,
#                 filter=None, # {"type": {"$eq": "skill"}},
#                 include_metadata=True,
#                 include_values=True
#             )

#             matches = []
#             for match in results.matches:
#                 similarity = 1 - match.score
#                 if similarity >= 0.1:
#                     matches.append({
#                         "id": match.id,
#                         "score": similarity,
#                         "metadata": match.metadata,
#                         "vector": match.values
#                     })

#             logger.info(f"Trouvé {len(matches)} nœuds d'ancrage avec un seuil de similarité ≥ 0.1")
#             return matches

#         except Exception as e:
#             logger.error(f"Erreur lors de l'extraction des compétences dominantes: {str(e)}")
#             return []

#     def traverse_skill_graph(self, anchor_skills: List[Dict[str, Any]], max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
#         """
#         Traverse le graphe de compétences à partir de compétences d'ancrage en utilisant le modèle GNN.
#         """
#         try:
#             graph = nx.DiGraph()
#             metadata_lookup = {}
#             current_level_nodes = []

#             # Initialisation des nœuds d'ancrage
#             for skill in anchor_skills:
#                 skill_id = skill["id"]
#                 metadata = skill["metadata"]
#                 vector = skill["vector"]
#                 label = metadata.get("preferredLabel", skill_id)

#                 graph.add_node(skill_id, label=label, type="skill", level=0, metadata=metadata)
#                 metadata_lookup[skill_id] = metadata
#                 current_level_nodes.append((skill_id, vector))

#             # Traversée niveau par niveau
#             for level in range(1, max_depth + 1):
#                 next_level_nodes = []

#                 for node_id, node_vector in current_level_nodes:
#                     try:
#                         # Rechercher des nœuds similaires dans Pinecone
#                         results = self.index.query(
#                             vector=node_vector,
#                             top_k=max_nodes_per_level * 2,  # Get more candidates for filtering
#                             include_metadata=True,
#                             filter={"type": {"$eq": "skill"}}
#                         )

#                         # Filtrer et trier les résultats en utilisant GraphSAGE
#                         filtered_matches = []
#                         for match in results.matches:
#                             if match.id not in graph:
#                                 # Convertir les vecteurs en tensors
#                                 node_tensor = torch.tensor(node_vector, dtype=torch.float32).unsqueeze(0)
#                                 match_tensor = torch.tensor(match.values, dtype=torch.float32).unsqueeze(0)
                                
#                                 # Créer un mini-graphe pour les deux nœuds
#                                 x = torch.cat([node_tensor, match_tensor], dim=0)
#                                 edge_index = torch.tensor([[0, 1], [1, 0]], dtype=torch.long)
                                
#                                 # Calculer la similarité avec GraphSAGE
#                                 with torch.no_grad():
#                                     node_embeddings = self.gnn_model.encoder(x, edge_index)
#                                     similarity = torch.cosine_similarity(
#                                         node_embeddings[0], 
#                                         node_embeddings[1], 
#                                         dim=0
#                                     ).item()
                                
#                                 # Normaliser la similarité entre 0 et 1
#                                 similarity = (similarity + 1) / 2
                                
#                                 if similarity >= 0.3:  # Seuil de similarité minimal
#                                     filtered_matches.append((match, similarity))

#                         # Trier par similarité décroissante et prendre les meilleurs
#                         filtered_matches.sort(key=lambda x: x[1], reverse=True)
#                         filtered_matches = filtered_matches[:max_nodes_per_level]

#                         # Ajouter les nœuds filtrés au graphe
#                         for match, similarity in filtered_matches:
#                             match_label = match.metadata.get("preferredLabel", match.id)
#                             graph.add_node(match.id, label=match_label, type="skill", level=level, metadata=match.metadata)
#                             graph.add_edge(node_id, match.id, weight=similarity)
#                             next_level_nodes.append((match.id, match.values))

#                     except Exception as e:
#                         logger.error(f"Erreur lors de la recherche de voisins pour {node_id}: {str(e)}")

#                 current_level_nodes = next_level_nodes[:max_nodes_per_level]
#                 if not current_level_nodes:
#                     break

#             # Construction du résultat final
#             nodes = [{
#                 "id": n,
#                 "label": d.get("label", n),
#                 "type": d.get("type", "skill"),
#                 "level": d.get("level", 0),
#                 "metadata": d.get("metadata", {})
#             } for n, d in graph.nodes(data=True)]

#             edges = [{
#                 "source": u,
#                 "target": v,
#                 "weight": d.get("weight", 1.0)
#             } for u, v, d in graph.edges(data=True)]

#             return {
#                 "nodes": {node["id"]: node for node in nodes},
#                 "edges": edges,
#                 "anchor_nodes": [s["id"] for s in anchor_skills]
#             }

#         except Exception as e:
#             logger.error(f"Erreur lors de la traversée du graphe de compétences: {str(e)}")
#             return {}

#     def mark_visibility(self, graph: nx.DiGraph, reveal_ratio: float = 0.60) -> Dict[str, bool]:
#         """
#         Marque la visibilité des nœuds dans le graphe.
        
#         Args:
#             graph: Graphe de compétences
#             reveal_ratio: Ratio de nœuds à révéler
            
#         Returns:
#             Dict[str, bool]: Dictionnaire {skill_id: is_revealed}
#         """
#         try:
#             # Calculer le nombre de nœuds à révéler
#             total_nodes = len(graph.nodes())
#             nodes_to_reveal = int(total_nodes * reveal_ratio)
            
#             # Récupérer les nœuds de niveau 0 (nœuds d'ancrage)
#             anchor_nodes = [node for node, data in graph.nodes(data=True) if data.get("level", 0) == 0]
            
#             # Tous les nœuds d'ancrage sont toujours révélés
#             visibility = {node: (node in anchor_nodes) for node in graph.nodes()}
            
#             # Calculer combien de nœuds supplémentaires doivent être révélés
#             already_revealed = len(anchor_nodes)
#             additional_reveals = max(0, nodes_to_reveal - already_revealed)
            
#             # Sélectionner des nœuds supplémentaires à révéler
#             non_anchor_nodes = [node for node in graph.nodes() if node not in anchor_nodes]
            
#             # Prioriser les nœuds connectés aux nœuds d'ancrage
#             connected_to_anchor = []
#             for node in non_anchor_nodes:
#                 for anchor in anchor_nodes:
#                     if graph.has_edge(anchor, node):
#                         connected_to_anchor.append(node)
#                         break
            
#             # Autres nœuds non connectés directement
#             other_nodes = [node for node in non_anchor_nodes if node not in connected_to_anchor]
            
#             # Mélanger les listes pour une sélection aléatoire
#             random.shuffle(connected_to_anchor)
#             random.shuffle(other_nodes)
            
#             # Révéler d'abord les nœuds connectés aux ancres, puis les autres si nécessaire
#             nodes_to_reveal_list = connected_to_anchor + other_nodes
#             for node in nodes_to_reveal_list[:additional_reveals]:
#                 visibility[node] = True
            
#             logger.info(f"Visibilité des nœuds marquée: {sum(visibility.values())}/{total_nodes} nœuds révélés")
#             return visibility
#         except Exception as e:
#             logger.error(f"Erreur lors du marquage de la visibilité des nœuds: {str(e)}")
#             return {}
#     def generate_challenge(self, skill_label: str, user_age: int) -> Dict[str, Any]:
#         """
#         Génère un défi pour une compétence donnée.
        
#         Args:
#             skill_label: Libellé de la compétence
#             user_age: Âge de l'utilisateur
            
#         Returns:
#             Dict[str, Any]: Défi généré avec récompense XP
#         """
#         try:
#             # Déterminer le niveau de difficulté en fonction de l'âge
#             if user_age < 18:
#                 difficulty = "débutant"
#                 xp_reward = random.randint(10, 30)
#             elif user_age < 25:
#                 difficulty = "intermédiaire"
#                 xp_reward = random.randint(20, 50)
#             else:
#                 difficulty = "avancé"
#                 xp_reward = random.randint(40, 100)
            
#             # Générer un prompt pour le LLM
#             prompt = f"""
#             Génère un défi pratique pour développer la compétence "{skill_label}" à un niveau {difficulty}.
#             Le défi doit être:
#             1. Concret et actionnable
#             2. Réalisable en moins d'une semaine
#             3. Adapté à une personne de {user_age} ans
#             4. Mesurable (comment savoir qu'on a réussi)
            
#             Format: Un titre court et une description détaillée en 3-4 phrases.
#             """
            
#             # Simuler une réponse LLM (à remplacer par un appel API réel)
#             # Note: Dans une implémentation réelle, vous utiliseriez un appel à une API LLM
            
#             # Exemples de défis prédéfinis par compétence (simulation)
#             challenge_templates = {
#                 "communication": {
#                     "débutant": {
#                         "title": "Présentation Express",
#                         "description": "Préparez et enregistrez une présentation de 2 minutes sur un sujet qui vous passionne. Partagez-la avec au moins deux personnes et demandez-leur un retour constructif. Concentrez-vous sur la clarté de votre message et votre langage corporel."
#                     },
#                     "intermédiaire": {
#                         "title": "Débat Constructif",
#                         "description": "Organisez un mini-débat avec des amis sur un sujet controversé. Votre mission est de défendre un point de vue opposé au vôtre pendant 10 minutes. Concentrez-vous sur l'écoute active et l'argumentation sans agressivité."
#                     },
#                     "avancé": {
#                         "title": "Négociation Win-Win",
#                         "description": "Identifiez une situation réelle nécessitant une négociation (achat, projet professionnel, etc.). Préparez une stratégie visant un résultat gagnant-gagnant, menez la négociation et documentez le processus et les résultats obtenus."
#                     }
#                 },
#                 "programmation": {
#                     "débutant": {
#                         "title": "Application Todo List",
#                         "description": "Créez une application simple de liste de tâches avec les fonctionnalités d'ajout, de suppression et de marquage comme terminé. Utilisez HTML, CSS et JavaScript de base. Testez votre application avec au moins 10 tâches différentes."
#                     },
#                     "intermédiaire": {
#                         "title": "API Météo Interactive",
#                         "description": "Développez une application web qui utilise une API météo pour afficher les prévisions d'une ville choisie par l'utilisateur. Implémentez une interface réactive qui change en fonction des conditions météorologiques et permettez la sauvegarde des villes favorites."
#                     },
#                     "avancé": {
#                         "title": "Système de Recommandation",
#                         "description": "Créez un algorithme de recommandation simple basé sur le contenu pour suggérer des produits/films/livres. Implémentez-le dans une application avec une base de données, testez-le avec des données réelles et mesurez sa précision avec des métriques appropriées."
#                     }
#                 }
#             }
            
#             # Déterminer la catégorie de compétence (simplifiée)
#             skill_category = "communication"  # Par défaut
#             for category in challenge_templates.keys():
#                 if category.lower() in skill_label.lower():
#                     skill_category = category
#                     break
            
#             # Si la catégorie n'existe pas, utiliser une catégorie par défaut
#             if skill_category not in challenge_templates:
#                 skill_category = list(challenge_templates.keys())[0]
            
#             # Récupérer le défi correspondant
#             challenge = challenge_templates.get(skill_category, {}).get(difficulty, {})
            
#             if not challenge:
#                 # Défi générique si aucun défi spécifique n'est trouvé
#                 challenge = {
#                     "title": f"Maîtrisez {skill_label}",
#                     "description": f"Recherchez et suivez un tutoriel en ligne sur {skill_label}. Pratiquez les concepts appris pendant au moins 3 heures réparties sur une semaine. Créez un petit projet démontrant votre compréhension et partagez-le avec un ami ou un collègue pour obtenir des commentaires."
#                 }
            
#             # Construire la réponse
#             challenge_data = {
#                 "skill_id": skill_label.replace(" ", "_").lower(),
#                 "skill_label": skill_label,
#                 "title": challenge.get("title", f"Défi: {skill_label}"),
#                 "description": challenge.get("description", f"Pratiquez {skill_label} pendant une semaine et documentez votre progression."),
#                 "difficulty": difficulty,
#                 "xp_reward": xp_reward,
#                 "duration_days": random.randint(3, 7)
#             }
            
#             logger.info(f"Défi généré pour la compétence '{skill_label}': {challenge_data['title']}")
#             return challenge_data
#         except Exception as e:
#             logger.error(f"Erreur lors de la génération du défi: {str(e)}")
#             return {
#                 "skill_label": skill_label,
#                 "title": f"Explorez {skill_label}",
#                 "description": f"Apprenez les bases de {skill_label} à travers des ressources en ligne et pratiquez régulièrement.",
#                 "difficulty": "intermédiaire",
#                 "xp_reward": 25,
#                 "duration_days": 5
#             }
#     def create_skill_tree(self, db: Session, user_id: int, max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
#         """
#         Crée un arbre de compétences complet pour un utilisateur.
#         """
#         try:
#             # Récupérer l'âge de l'utilisateur
#             query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
#             result = db.execute(query, {"user_id": user_id}).fetchone()
#             user_age = result[0] if result and result[0] else 25
            
#             # Extraire les compétences d'ancrage
#             anchor_skills = self.extract_anchor_skills(db, user_id)
#             if not anchor_skills:
#                 logger.error(f"Aucune compétence d'ancrage trouvée pour l'utilisateur {user_id}")
#                 return {}
            
#             # Créer un graphe pour chaque compétence d'ancrage
#             all_nodes = []
#             all_edges = []
            
#             for anchor_skill in anchor_skills:
#                 # Créer un graphe pour cette compétence
#                 graph_data = self.traverse_skill_graph([anchor_skill], max_depth, max_nodes_per_level)
                
#                 # Convertir les nœuds et les arêtes au format attendu par le frontend
#                 nodes = []
#                 for node_id, node_data in graph_data.get("nodes", {}).items():
#                     # Marquer la visibilité des nœuds
#                     is_visible = node_id in graph_data.get("anchor_nodes", [])
                    
#                     # Générer un défi pour les nœuds visibles
#                     challenge_data = {}
#                     if is_visible:
#                         skill_label = node_data.get("label", f"Compétence {node_id}")
#                         challenge_data = self.generate_challenge(skill_label, user_age)
                    
#                     competence_node = {
#                         "id": node_id,
#                         "skill_id": node_id,
#                         "skill_label": node_data.get("label", f"Compétence {node_id}"),
#                         "challenge": challenge_data.get("description", ""),
#                         "xp_reward": challenge_data.get("xp_reward", 25),
#                         "visible": is_visible,
#                         "revealed": is_visible,
#                         "state": "locked",
#                         "notes": "",
#                         "graph_id": str(uuid4())  # Unique graph ID for each anchor skill's tree
#                     }
#                     nodes.append(competence_node)
                
#                 # Ajouter les nœuds et les arêtes à la liste principale
#                 all_nodes.extend(nodes)
#                 all_edges.extend(graph_data.get("edges", []))
            
#             # Construire la réponse finale
#             skill_tree = {
#                 "nodes": all_nodes,
#                 "edges": all_edges,
#                 "graph_id": str(uuid4())
#             }
            
#             logger.info(f"Arbre de compétences créé avec succès pour l'utilisateur {user_id}")
#             return skill_tree
            
#         except Exception as e:
#             logger.error(f"Erreur lors de la création de l'arbre de compétences: {str(e)}")
#             return {}
#     def save_skill_tree(self, db: Session, user_id: int, tree_data: Dict[str, Any]) -> str:
#         """
#         Sauvegarde l'arbre de compétences dans la base de données.
        
#         Args:
#             db: Session de base de données
#             user_id: ID de l'utilisateur
#             tree_data: Données de l'arbre de compétences
            
#         Returns:
#             str: ID du graphe sauvegardé
#         """
#         try:
#             import json
#             import numpy as np
            
#             # Classe personnalisée pour encoder les objets numpy en JSON
#             class NumpyEncoder(json.JSONEncoder):
#                 def default(self, obj):
#                     if isinstance(obj, np.ndarray):
#                         return obj.tolist()
#                     if isinstance(obj, np.integer):
#                         return int(obj)
#                     if isinstance(obj, np.floating):
#                         return float(obj)
#                     return super(NumpyEncoder, self).default(obj)
            
#             # Nettoyer les données pour s'assurer qu'elles sont sérialisables
#             def clean_for_json(data):
#                 if isinstance(data, dict):
#                     return {k: clean_for_json(v) for k, v in data.items()}
#                 elif isinstance(data, list):
#                     return [clean_for_json(item) for item in data]
#                 elif isinstance(data, np.ndarray):
#                     return data.tolist()
#                 elif isinstance(data, (np.integer, np.floating)):
#                     return float(data) if isinstance(data, np.floating) else int(data)
#                 else:
#                     return data
            
#             # Nettoyer les données avant la sérialisation
#             clean_tree_data = clean_for_json(tree_data)
            
#             # Créer une nouvelle instance de UserSkillTree
#             skill_tree = UserSkillTree(
#                 user_id=user_id,
#                 tree_data=clean_tree_data  # JSONB will handle the serialization
#             )
            
#             # Ajouter et sauvegarder dans la base de données
#             db.add(skill_tree)
#             db.commit()
#             db.refresh(skill_tree)
            
#             logger.info(f"Arbre de compétences sauvegardé avec succès pour l'utilisateur {user_id}, ID: {skill_tree.graph_id}")
#             return skill_tree.graph_id
#         except Exception as e:
#             logger.error(f"Erreur lors de la sauvegarde de l'arbre de compétences: {str(e)}")
#             db.rollback()
#             return ""
    
#     def complete_challenge(self, db: Session, node_id: int, user_id: int) -> bool:
#         """
#         Marque un défi comme complété et accorde des XP.
        
#         Args:
#             db: Session de base de données
#             node_id: ID du nœud
#             user_id: ID de l'utilisateur
            
#         Returns:
#             bool: True si le défi a été complété avec succès
#         """
#         try:
#             # Récupérer les informations du défi
#             query = text("""
#                 SELECT tree_data 
#                 FROM user_skill_trees 
#                 WHERE user_id = :user_id 
#                 ORDER BY created_at DESC 
#                 LIMIT 1
#             """)
            
#             result = db.execute(query, {"user_id": user_id}).fetchone()
#             if not result or not result[0]:
#                 logger.error(f"Aucun arbre de compétences trouvé pour l'utilisateur {user_id}")
#                 return False
            
#             import json
#             import numpy as np
            
#             # Classe personnalisée pour encoder les objets numpy en JSON
#             class NumpyEncoder(json.JSONEncoder):
#                 def default(self, obj):
#                     if isinstance(obj, np.ndarray):
#                         return obj.tolist()
#                     if isinstance(obj, np.integer):
#                         return int(obj)
#                     if isinstance(obj, np.floating):
#                         return float(obj)
#                     return super(NumpyEncoder, self).default(obj)
            
#             # Nettoyer les données pour s'assurer qu'elles sont sérialisables
#             def clean_for_json(data):
#                 if isinstance(data, dict):
#                     return {k: clean_for_json(v) for k, v in data.items()}
#                 elif isinstance(data, list):
#                     return [clean_for_json(item) for item in data]
#                 elif isinstance(data, np.ndarray):
#                     return data.tolist()
#                 elif isinstance(data, (np.integer, np.floating)):
#                     return float(data) if isinstance(data, np.floating) else int(data)
#                 else:
#                     return data
            
#             tree_data = json.loads(result[0])
            
#             # Vérifier si le défi existe
#             challenges = tree_data.get("challenges", {})
#             if str(node_id) not in challenges:
#                 logger.error(f"Défi {node_id} non trouvé pour l'utilisateur {user_id}")
#                 return False
            
#             challenge = challenges[str(node_id)]
#             xp_reward = challenge.get("xp_reward", 25)
#             skill_label = challenge.get("skill_label", "Compétence inconnue")
            
#             # Mettre à jour les XP de l'utilisateur
#             update_query = text("""
#                 UPDATE user_profiles 
#                 SET xp = xp + :xp_reward 
#                 WHERE user_id = :user_id
#             """)
            
#             db.execute(update_query, {"user_id": user_id, "xp_reward": xp_reward})
            
#             # Enregistrer la complétion du défi
#             completion_query = text("""
#                 INSERT INTO challenge_completions (user_id, node_id, challenge_title, xp_earned, completed_at)
#                 VALUES (:user_id, :node_id, :challenge_title, :xp_earned, NOW())
#             """)
            
#             db.execute(completion_query, {
#                 "user_id": user_id,
#                 "node_id": node_id,
#                 "challenge_title": challenge.get("title", f"Défi {node_id}"),
#                 "xp_earned": xp_reward
#             })
            
#             # Mettre à jour le niveau de compétence de l'utilisateur
#             skill_update_query = text("""
#                 INSERT INTO user_skills (user_id, skill_id, skill_label, proficiency_level, last_updated)
#                 VALUES (:user_id, :skill_id, :skill_label, 1, NOW())
#                 ON CONFLICT (user_id, skill_id) 
#                 DO UPDATE SET proficiency_level = user_skills.proficiency_level + 1, last_updated = NOW()
#             """)
            
#             db.execute(skill_update_query, {
#                 "user_id": user_id,
#                 "skill_id": node_id,
#                 "skill_label": skill_label
#             })
            
#             db.commit()
            
#             # Émettre un événement public
#             domain = tree_data.get("metadata", {}).get("domain", "compétence")
#             self.emit_public_event(db, user_id, domain)
            
#             logger.info(f"Défi {node_id} complété avec succès pour l'utilisateur {user_id}, {xp_reward} XP gagnés")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de la complétion du défi: {str(e)}")
#             db.rollback()
#     def emit_public_event(self, db: Session, user_id: int, domain: str) -> bool:
#         """
#         Émet un événement public dans le flux d'activité.
        
#         Args:
#             db: Session de base de données
#             user_id: ID de l'utilisateur
#             domain: Domaine de compétence
            
#         Returns:
#             bool: True si l'événement a été émis avec succès
#         """
#         try:
#             # Récupérer les informations de l'utilisateur
#             user_query = text("""
#                 SELECT username, first_name, last_name
#                 FROM users
#                 WHERE id = :user_id
#             """)
            
#             user_result = db.execute(user_query, {"user_id": user_id}).fetchone()
#             if not user_result:
#                 logger.error(f"Utilisateur {user_id} non trouvé")
#                 return False
            
#             username = user_result[0]
#             full_name = f"{user_result[1]} {user_result[2]}" if user_result[1] and user_result[2] else username
            
#             # Créer un message d'événement
#             event_message = f"{full_name} a progressé dans le domaine de {domain}"
            
#             # Insérer l'événement dans la base de données
#             event_query = text("""
#                 INSERT INTO activity_feed (user_id, event_type, event_message, created_at)
#                 VALUES (:user_id, 'skill_progress', :event_message, NOW())
#             """)
            
#             db.execute(event_query, {
#                 "user_id": user_id,
#                 "event_message": event_message
#             })
            
#             db.commit()
            
#             logger.info(f"Événement public émis pour l'utilisateur {user_id} dans le domaine {domain}")
#             return True
#         except Exception as e:
#             logger.error(f"Erreur lors de l'émission de l'événement public: {str(e)}")
#             db.rollback()
#             return False

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