import os
import logging
import numpy as np
import random
import networkx as nx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import pinecone
from pinecone import Pinecone

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Pinecone
PINECONE_INDEX = "esco-368"

class CompetenceTreeService:
    """
    Service pour générer des arbres de compétences personnalisés avec des défis dynamiques.
    """
    
    def __init__(self):
        """
        Initialise le service d'arbre de compétences.
        """
        self.pinecone_client = None
        self.index = None
        self._initialize_pinecone()
    
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
            return False
    
    def _convert_score_to_similarity(self, score: float) -> float:
        """
        Convertit un score de distance Pinecone en score de similarité.
        
        Args:
            score: Score de distance Pinecone
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Pinecone retourne une distance, nous la convertissons en similarité (1 - distance)
        return 1.0 - score
    
    def get_user_embedding(self, db: Session, user_id: int, embedding_type: str = "esco_embedding_skill") -> Optional[np.ndarray]:
        """
        Récupère l'embedding de compétences d'un utilisateur depuis la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            embedding_type: Type d'embedding à récupérer (par défaut: esco_embedding_skill)
            
        Returns:
            np.ndarray: Embedding de l'utilisateur ou None en cas d'échec
        """
        try:
            # Vérifier que le type d'embedding est valide
            valid_types = ["esco_embedding", "esco_embedding_occupation", "esco_embedding_skill", "esco_embedding_skillsgroup"]
            if embedding_type not in valid_types:
                logger.error(f"Type d'embedding invalide: {embedding_type}")
                return None
            
            # Récupérer l'embedding depuis la base de données
            query = text(f"SELECT {embedding_type} FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if not result or not result[0]:
                logger.error(f"Aucun embedding {embedding_type} trouvé pour l'utilisateur {user_id}")
                return None
            
            # Convertir la chaîne en tableau numpy
            import ast
            embedding = np.array(ast.literal_eval(result[0]), dtype=np.float32)
            logger.info(f"Embedding {embedding_type} récupéré avec succès pour l'utilisateur {user_id}: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'embedding: {str(e)}")
            return None
    def extract_anchor_skills(self, db: Session, user_id: int, top_k: int = 5) -> List[str]:
        """
        Extrait les compétences dominantes d'un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            top_k: Nombre de compétences à extraire
            
        Returns:
            List[str]: Liste des IDs de compétences dominantes
        """
        try:
            # Récupérer les compétences de l'utilisateur depuis la base de données
            query = text("""
                SELECT skill_id, proficiency_level
                FROM user_skills
                WHERE user_id = :user_id
                ORDER BY proficiency_level DESC
                LIMIT :top_k
            """)
            results = db.execute(query, {"user_id": user_id, "top_k": top_k}).fetchall()
            
            if not results:
                logger.warning(f"Aucune compétence trouvée pour l'utilisateur {user_id}")
                
                # Utiliser l'embedding de l'utilisateur pour trouver des compétences similaires
                embedding = self.get_user_embedding(db, user_id, "esco_embedding_skill")
                if embedding is None:
                    logger.error(f"Impossible de récupérer l'embedding pour l'utilisateur {user_id}")
                    return []
                
                # Interroger Pinecone pour les compétences similaires
                if self.index is None:
                    if not self._initialize_pinecone():
                        logger.error("Impossible d'initialiser Pinecone")
                        return []
                
                vector = embedding.tolist()
                results = self.index.query(
                    vector=vector,
                    top_k=top_k,
                    filter={"type": {"$eq": "skill"}},
                    include_metadata=True
                )
                
                # Extraire les IDs de compétences
                skill_ids = [match.id for match in results.matches]
                logger.info(f"Compétences extraites via embedding pour l'utilisateur {user_id}: {skill_ids}")
                return skill_ids
            
            # Extraire les IDs de compétences
            skill_ids = [result[0] for result in results]
            logger.info(f"Compétences dominantes extraites pour l'utilisateur {user_id}: {skill_ids}")
            return skill_ids
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des compétences dominantes: {str(e)}")
            return []
    def traverse_skill_graph(self, anchor_skill_ids: List[str], max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """
        Traverse le graphe de compétences à partir des compétences d'ancrage.
        
        Args:
            anchor_skill_ids: Liste des IDs de compétences d'ancrage
            max_depth: Profondeur maximale de traversée
            max_nodes_per_level: Nombre maximum de nœuds par niveau
            
        Returns:
            Dict[str, Any]: Données du graphe traversé
        """
        try:
            # Initialiser le graphe dirigé
            graph = nx.DiGraph()
            
            # Ajouter les nœuds d'ancrage
            for skill_id in anchor_skill_ids:
                # Récupérer les métadonnées de la compétence depuis Pinecone
                if self.index is None:
                    if not self._initialize_pinecone():
                        logger.error("Impossible d'initialiser Pinecone")
                        return {}
                
                # Récupérer les métadonnées de la compétence
                try:
                    skill_info = self.index.fetch(ids=[skill_id])
                    if skill_id in skill_info.vectors:
                        metadata = skill_info.vectors[skill_id].metadata
                        graph.add_node(skill_id,
                                      label=metadata.get("preferredLabel", "Compétence inconnue"),
                                      type="skill",
                                      level=0,
                                      metadata=metadata)
                    else:
                        logger.warning(f"Compétence {skill_id} non trouvée dans Pinecone")
                        graph.add_node(skill_id,
                                      label=f"Compétence {skill_id}",
                                      type="skill",
                                      level=0)
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des métadonnées pour {skill_id}: {str(e)}")
                    graph.add_node(skill_id,
                                  label=f"Compétence {skill_id}",
                                  type="skill",
                                  level=0)
            
            # Traverser le graphe niveau par niveau
            current_level_nodes = anchor_skill_ids
            
            for level in range(1, max_depth + 1):
                next_level_nodes = []
                
                for node_id in current_level_nodes:
                    # Récupérer l'embedding du nœud
                    try:
                        node_info = self.index.fetch(ids=[node_id])
                        if node_id not in node_info.vectors:
                            logger.warning(f"Nœud {node_id} non trouvé dans Pinecone")
                            continue
                        
                        node_vector = node_info.vectors[node_id].values
                        
                        # Rechercher des compétences similaires
                        results = self.index.query(
                            vector=node_vector,
                            top_k=max_nodes_per_level,
                            filter={"type": {"$eq": "skill"}},
                            include_metadata=True
                        )
                        
                        # Ajouter les nœuds et les arêtes au graphe
                        for match in results.matches:
                            # Éviter d'ajouter des nœuds déjà présents dans le graphe
                            if match.id not in graph:
                                similarity = self._convert_score_to_similarity(match.score)
                                
                                # Ajouter le nœud
                                graph.add_node(match.id,
                                              label=match.metadata.get("preferredLabel", f"Compétence {match.id}"),
                                              type="skill",
                                              level=level,
                                              metadata=match.metadata)
                                
                                # Ajouter l'arête
                                graph.add_edge(node_id, match.id, weight=similarity)
                                
                                # Ajouter à la liste des nœuds du niveau suivant
                                next_level_nodes.append(match.id)
                    except Exception as e:
                        logger.error(f"Erreur lors de la traversée pour le nœud {node_id}: {str(e)}")
                
                # Limiter le nombre de nœuds pour le niveau suivant
                if len(next_level_nodes) > max_nodes_per_level:
                    next_level_nodes = next_level_nodes[:max_nodes_per_level]
                
                # Mettre à jour les nœuds du niveau courant
                current_level_nodes = next_level_nodes
                
                # Si aucun nœud n'est trouvé pour le niveau suivant, arrêter la traversée
                if not current_level_nodes:
                    break
            
            # Préparer les données du graphe pour la réponse
            nodes = []
            for node_id in graph.nodes():
                node_data = graph.nodes[node_id]
                nodes.append({
                    "id": node_id,
                    "label": node_data.get("label", f"Compétence {node_id}"),
                    "type": node_data.get("type", "skill"),
                    "level": node_data.get("level", 0),
                    "metadata": node_data.get("metadata", {})
                })
            
            edges = []
            for source, target, data in graph.edges(data=True):
                edges.append({
                    "source": source,
                    "target": target,
                    "weight": data.get("weight", 0.5)
                })
            
            graph_data = {
                "nodes": nodes,
                "edges": edges,
                "anchor_nodes": anchor_skill_ids
            }
            
            logger.info(f"Graphe de compétences traversé avec succès: {len(nodes)} nœuds, {len(edges)} arêtes")
            return graph_data
        except Exception as e:
            logger.error(f"Erreur lors de la traversée du graphe de compétences: {str(e)}")
            return {}
    def mark_visibility(self, graph: nx.DiGraph, reveal_ratio: float = 0.60) -> Dict[str, bool]:
        """
        Marque la visibilité des nœuds dans le graphe.
        
        Args:
            graph: Graphe de compétences
            reveal_ratio: Ratio de nœuds à révéler
            
        Returns:
            Dict[str, bool]: Dictionnaire {skill_id: is_revealed}
        """
        try:
            # Calculer le nombre de nœuds à révéler
            total_nodes = len(graph.nodes())
            nodes_to_reveal = int(total_nodes * reveal_ratio)
            
            # Récupérer les nœuds de niveau 0 (nœuds d'ancrage)
            anchor_nodes = [node for node, data in graph.nodes(data=True) if data.get("level", 0) == 0]
            
            # Tous les nœuds d'ancrage sont toujours révélés
            visibility = {node: (node in anchor_nodes) for node in graph.nodes()}
            
            # Calculer combien de nœuds supplémentaires doivent être révélés
            already_revealed = len(anchor_nodes)
            additional_reveals = max(0, nodes_to_reveal - already_revealed)
            
            # Sélectionner des nœuds supplémentaires à révéler
            non_anchor_nodes = [node for node in graph.nodes() if node not in anchor_nodes]
            
            # Prioriser les nœuds connectés aux nœuds d'ancrage
            connected_to_anchor = []
            for node in non_anchor_nodes:
                for anchor in anchor_nodes:
                    if graph.has_edge(anchor, node):
                        connected_to_anchor.append(node)
                        break
            
            # Autres nœuds non connectés directement
            other_nodes = [node for node in non_anchor_nodes if node not in connected_to_anchor]
            
            # Mélanger les listes pour une sélection aléatoire
            random.shuffle(connected_to_anchor)
            random.shuffle(other_nodes)
            
            # Révéler d'abord les nœuds connectés aux ancres, puis les autres si nécessaire
            nodes_to_reveal_list = connected_to_anchor + other_nodes
            for node in nodes_to_reveal_list[:additional_reveals]:
                visibility[node] = True
            
            logger.info(f"Visibilité des nœuds marquée: {sum(visibility.values())}/{total_nodes} nœuds révélés")
            return visibility
        except Exception as e:
            logger.error(f"Erreur lors du marquage de la visibilité des nœuds: {str(e)}")
            return {}
    def generate_challenge(self, skill_label: str, user_age: int) -> Dict[str, Any]:
        """
        Génère un défi pour une compétence donnée.
        
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
            
            # Générer un prompt pour le LLM
            prompt = f"""
            Génère un défi pratique pour développer la compétence "{skill_label}" à un niveau {difficulty}.
            Le défi doit être:
            1. Concret et actionnable
            2. Réalisable en moins d'une semaine
            3. Adapté à une personne de {user_age} ans
            4. Mesurable (comment savoir qu'on a réussi)
            
            Format: Un titre court et une description détaillée en 3-4 phrases.
            """
            
            # Simuler une réponse LLM (à remplacer par un appel API réel)
            # Note: Dans une implémentation réelle, vous utiliseriez un appel à une API LLM
            
            # Exemples de défis prédéfinis par compétence (simulation)
            challenge_templates = {
                "communication": {
                    "débutant": {
                        "title": "Présentation Express",
                        "description": "Préparez et enregistrez une présentation de 2 minutes sur un sujet qui vous passionne. Partagez-la avec au moins deux personnes et demandez-leur un retour constructif. Concentrez-vous sur la clarté de votre message et votre langage corporel."
                    },
                    "intermédiaire": {
                        "title": "Débat Constructif",
                        "description": "Organisez un mini-débat avec des amis sur un sujet controversé. Votre mission est de défendre un point de vue opposé au vôtre pendant 10 minutes. Concentrez-vous sur l'écoute active et l'argumentation sans agressivité."
                    },
                    "avancé": {
                        "title": "Négociation Win-Win",
                        "description": "Identifiez une situation réelle nécessitant une négociation (achat, projet professionnel, etc.). Préparez une stratégie visant un résultat gagnant-gagnant, menez la négociation et documentez le processus et les résultats obtenus."
                    }
                },
                "programmation": {
                    "débutant": {
                        "title": "Application Todo List",
                        "description": "Créez une application simple de liste de tâches avec les fonctionnalités d'ajout, de suppression et de marquage comme terminé. Utilisez HTML, CSS et JavaScript de base. Testez votre application avec au moins 10 tâches différentes."
                    },
                    "intermédiaire": {
                        "title": "API Météo Interactive",
                        "description": "Développez une application web qui utilise une API météo pour afficher les prévisions d'une ville choisie par l'utilisateur. Implémentez une interface réactive qui change en fonction des conditions météorologiques et permettez la sauvegarde des villes favorites."
                    },
                    "avancé": {
                        "title": "Système de Recommandation",
                        "description": "Créez un algorithme de recommandation simple basé sur le contenu pour suggérer des produits/films/livres. Implémentez-le dans une application avec une base de données, testez-le avec des données réelles et mesurez sa précision avec des métriques appropriées."
                    }
                }
            }
            
            # Déterminer la catégorie de compétence (simplifiée)
            skill_category = "communication"  # Par défaut
            for category in challenge_templates.keys():
                if category.lower() in skill_label.lower():
                    skill_category = category
                    break
            
            # Si la catégorie n'existe pas, utiliser une catégorie par défaut
            if skill_category not in challenge_templates:
                skill_category = list(challenge_templates.keys())[0]
            
            # Récupérer le défi correspondant
            challenge = challenge_templates.get(skill_category, {}).get(difficulty, {})
            
            if not challenge:
                # Défi générique si aucun défi spécifique n'est trouvé
                challenge = {
                    "title": f"Maîtrisez {skill_label}",
                    "description": f"Recherchez et suivez un tutoriel en ligne sur {skill_label}. Pratiquez les concepts appris pendant au moins 3 heures réparties sur une semaine. Créez un petit projet démontrant votre compréhension et partagez-le avec un ami ou un collègue pour obtenir des commentaires."
                }
            
            # Construire la réponse
            challenge_data = {
                "skill_id": skill_label.replace(" ", "_").lower(),
                "skill_label": skill_label,
                "title": challenge.get("title", f"Défi: {skill_label}"),
                "description": challenge.get("description", f"Pratiquez {skill_label} pendant une semaine et documentez votre progression."),
                "difficulty": difficulty,
                "xp_reward": xp_reward,
                "duration_days": random.randint(3, 7)
            }
            
            logger.info(f"Défi généré pour la compétence '{skill_label}': {challenge_data['title']}")
            return challenge_data
        except Exception as e:
            logger.error(f"Erreur lors de la génération du défi: {str(e)}")
            return {
                "skill_label": skill_label,
                "title": f"Explorez {skill_label}",
                "description": f"Apprenez les bases de {skill_label} à travers des ressources en ligne et pratiquez régulièrement.",
                "difficulty": "intermédiaire",
                "xp_reward": 25,
                "duration_days": 5
            }
    def create_skill_tree(self, db: Session, user_id: int, max_depth: int = 3, max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """
        Crée un arbre de compétences complet pour un utilisateur.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            max_depth: Profondeur maximale de l'arbre
            max_nodes_per_level: Nombre maximum de nœuds par niveau
            
        Returns:
            Dict[str, Any]: Arbre de compétences complet
        """
        try:
            # Récupérer l'âge de l'utilisateur pour la génération de défis
            query = text("SELECT age FROM user_profiles WHERE user_id = :user_id")
            result = db.execute(query, {"user_id": user_id}).fetchone()
            user_age = result[0] if result and result[0] else 25  # Âge par défaut
            
            # Extraire les compétences d'ancrage
            anchor_skill_ids = self.extract_anchor_skills(db, user_id)
            if not anchor_skill_ids:
                logger.error(f"Aucune compétence d'ancrage trouvée pour l'utilisateur {user_id}")
                return {}
            
            # Traverser le graphe de compétences
            graph_data = self.traverse_skill_graph(anchor_skill_ids, max_depth, max_nodes_per_level)
            if not graph_data:
                logger.error(f"Échec de la traversée du graphe pour l'utilisateur {user_id}")
                return {}
            
            # Créer un graphe NetworkX à partir des données
            graph = nx.DiGraph()
            
            # Ajouter les nœuds
            for node in graph_data.get("nodes", []):
                graph.add_node(node["id"], **node)
            
            # Ajouter les arêtes
            for edge in graph_data.get("edges", []):
                graph.add_edge(edge["source"], edge["target"], weight=edge["weight"])
            
            # Marquer la visibilité des nœuds
            visibility = self.mark_visibility(graph)
            
            # Générer des défis pour chaque nœud visible
            challenges = {}
            for node_id, is_visible in visibility.items():
                if is_visible:
                    node_data = graph.nodes[node_id]
                    skill_label = node_data.get("label", f"Compétence {node_id}")
                    challenges[node_id] = self.generate_challenge(skill_label, user_age)
            
            # Construire la réponse finale
            skill_tree = {
                "user_id": user_id,
                "graph_data": graph_data,
                "visibility": visibility,
                "challenges": challenges,
                "metadata": {
                    "created_at": "2025-05-27T14:00:00Z",  # À remplacer par la date actuelle
                    "max_depth": max_depth,
                    "max_nodes_per_level": max_nodes_per_level,
                    "anchor_skills": anchor_skill_ids
                }
            }
            
            logger.info(f"Arbre de compétences créé avec succès pour l'utilisateur {user_id}")
            return skill_tree
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'arbre de compétences: {str(e)}")
            return {}
    def save_skill_tree(self, db: Session, user_id: int, tree_data: Dict[str, Any]) -> str:
        """
        Sauvegarde l'arbre de compétences dans la base de données.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            tree_data: Données de l'arbre de compétences
            
        Returns:
            str: ID du graphe sauvegardé
        """
        try:
            import json
            import uuid
            
            # Générer un ID unique pour le graphe
            graph_id = str(uuid.uuid4())
            
            # Convertir les données en JSON
            tree_json = json.dumps(tree_data)
            
            # Insérer dans la base de données
            query = text("""
                INSERT INTO user_skill_trees (user_id, graph_id, tree_data, created_at)
                VALUES (:user_id, :graph_id, :tree_data, NOW())
                RETURNING graph_id
            """)
            
            result = db.execute(query, {
                "user_id": user_id,
                "graph_id": graph_id,
                "tree_data": tree_json
            })
            
            db.commit()
            
            # Récupérer l'ID du graphe inséré
            inserted_id = result.fetchone()[0]
            
            logger.info(f"Arbre de compétences sauvegardé avec succès pour l'utilisateur {user_id}, ID: {inserted_id}")
            return inserted_id
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'arbre de compétences: {str(e)}")
            db.rollback()
            return ""
    
    def complete_challenge(self, db: Session, node_id: int, user_id: int) -> bool:
        """
        Marque un défi comme complété et accorde des XP.
        
        Args:
            db: Session de base de données
            node_id: ID du nœud
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si le défi a été complété avec succès
        """
        try:
            # Récupérer les informations du défi
            query = text("""
                SELECT tree_data 
                FROM user_skill_trees 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            if not result or not result[0]:
                logger.error(f"Aucun arbre de compétences trouvé pour l'utilisateur {user_id}")
                return False
            
            import json
            tree_data = json.loads(result[0])
            
            # Vérifier si le défi existe
            challenges = tree_data.get("challenges", {})
            if str(node_id) not in challenges:
                logger.error(f"Défi {node_id} non trouvé pour l'utilisateur {user_id}")
                return False
            
            challenge = challenges[str(node_id)]
            xp_reward = challenge.get("xp_reward", 25)
            skill_label = challenge.get("skill_label", "Compétence inconnue")
            
            # Mettre à jour les XP de l'utilisateur
            update_query = text("""
                UPDATE user_profiles 
                SET xp = xp + :xp_reward 
                WHERE user_id = :user_id
            """)
            
            db.execute(update_query, {"user_id": user_id, "xp_reward": xp_reward})
            
            # Enregistrer la complétion du défi
            completion_query = text("""
                INSERT INTO challenge_completions (user_id, node_id, challenge_title, xp_earned, completed_at)
                VALUES (:user_id, :node_id, :challenge_title, :xp_earned, NOW())
            """)
            
            db.execute(completion_query, {
                "user_id": user_id,
                "node_id": node_id,
                "challenge_title": challenge.get("title", f"Défi {node_id}"),
                "xp_earned": xp_reward
            })
            
            # Mettre à jour le niveau de compétence de l'utilisateur
            skill_update_query = text("""
                INSERT INTO user_skills (user_id, skill_id, skill_label, proficiency_level, last_updated)
                VALUES (:user_id, :skill_id, :skill_label, 1, NOW())
                ON CONFLICT (user_id, skill_id) 
                DO UPDATE SET proficiency_level = user_skills.proficiency_level + 1, last_updated = NOW()
            """)
            
            db.execute(skill_update_query, {
                "user_id": user_id,
                "skill_id": node_id,
                "skill_label": skill_label
            })
            
            db.commit()
            
            # Émettre un événement public
            domain = tree_data.get("metadata", {}).get("domain", "compétence")
            self.emit_public_event(db, user_id, domain)
            
            logger.info(f"Défi {node_id} complété avec succès pour l'utilisateur {user_id}, {xp_reward} XP gagnés")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la complétion du défi: {str(e)}")
            db.rollback()
    def emit_public_event(self, db: Session, user_id: int, domain: str) -> bool:
        """
        Émet un événement public dans le flux d'activité.
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            domain: Domaine de compétence
            
        Returns:
            bool: True si l'événement a été émis avec succès
        """
        try:
            # Récupérer les informations de l'utilisateur
            user_query = text("""
                SELECT username, first_name, last_name
                FROM users
                WHERE id = :user_id
            """)
            
            user_result = db.execute(user_query, {"user_id": user_id}).fetchone()
            if not user_result:
                logger.error(f"Utilisateur {user_id} non trouvé")
                return False
            
            username = user_result[0]
            full_name = f"{user_result[1]} {user_result[2]}" if user_result[1] and user_result[2] else username
            
            # Créer un message d'événement
            event_message = f"{full_name} a progressé dans le domaine de {domain}"
            
            # Insérer l'événement dans la base de données
            event_query = text("""
                INSERT INTO activity_feed (user_id, event_type, event_message, created_at)
                VALUES (:user_id, 'skill_progress', :event_message, NOW())
            """)
            
            db.execute(event_query, {
                "user_id": user_id,
                "event_message": event_message
            })
            
            db.commit()
            
            logger.info(f"Événement public émis pour l'utilisateur {user_id} dans le domaine {domain}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'émission de l'événement public: {str(e)}")
            db.rollback()
            return False
            return False