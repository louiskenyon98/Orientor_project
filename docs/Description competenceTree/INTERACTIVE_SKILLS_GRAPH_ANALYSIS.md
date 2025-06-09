# Analyse Complète : Graphique de Compétences Interactif ESCO avec GraphSAGE et LLM

## Vue d'Ensemble de la Fonctionnalité

Cette analyse documente tous les composants nécessaires pour implémenter un **graphique de compétences interactif** où :

- **5 compétences personnalisées** agissent comme nœuds d'ancrage (points d'entrée)
- Un **algorithme de traversée basé sur GraphSAGE** étend dynamiquement le graphe en forme d'arbre
- Des **actions/défis générés par LLM** doivent être complétés pour débloquer les nœuds suivants
- **~70% des nœuds sont cachés** initialement pour stimuler la curiosité et la découverte

## Architecture Technique Existante

### 1. Fondation ESCO Graph

#### Composants Existants
```python
# data_n_notebook/esco/loader.py
def load_esco(DATA_DIR: Path, limit: int = None):
    """Charge les données ESCO depuis les fichiers CSV"""
    # Charge 21,169 nœuds et 153,951 arêtes étiquetées
    
# data_n_notebook/esco/builder.py  
def build_graph(esco_data):
    """Construit le graphe ESCO complet avec NetworkX"""
    # Types de nœuds: occupations, skills, skillgroups, isco_groups
    # Types de relations: skill_to_skill, occupation_to_skill, hierarchies
```

#### Structure des Données ESCO
```python
ESCO_NODE_TYPES = {
    "occupation": "Métiers (ex: Data Scientist)",
    "skill": "Compétences techniques et transversales", 
    "skillgroup": "Groupes de compétences",
    "iscogroup": "Groupes ISCO"
}

ESCO_RELATION_TYPES = {
    "requires": "Compétence requise",
    "optional": "Compétence optionnelle", 
    "is_parent_of": "Relation hiérarchique",
    "related_to": "Relation connexe"
}
```

### 2. Moteur de Traversée GraphSAGE

#### Service Principal
```python
# backend/competenceTree_dev/graph_traversal_service.py
class GraphTraversalService:
    def __init__(self, model_path: str, graph_data_path: str):
        self.model = self._load_model()  # Modèle GraphSAGE préentraîné
        self.graph = self._create_networkx_graph()  # Graphe ESCO NetworkX
        self.node_features = {}  # Features des nœuds
        self.node_metadata = {}  # Métadonnées des nœuds
    
    def traverse_graph(self, anchor_node_ids: List[str], 
                      max_depth: int = 6, 
                      min_similarity: float = 0.3,
                      max_nodes_per_level: int = 5) -> Dict[str, Any]:
        """Traverse le graphe à partir des nœuds d'ancrage"""
```

#### Modèle GraphSAGE
```python
# backend/app/services/GNN/GraphSage.py
class GraphSAGE(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.2):
        self.convs = torch.nn.ModuleList()
        self.convs.append(SAGEConv(input_dim, hidden_dim))
        self.convs.append(SAGEConv(hidden_dim, output_dim))
        
    def forward(self, x, edge_index):
        # Calcule les embeddings des nœuds
        for conv in self.convs[:-1]:
            x = conv(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, training=self.training)
        x = self.convs[-1](x, edge_index)
        return x

class CareerTreeModel(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.2):
        self.encoder = GraphSAGE(input_dim, hidden_dim, output_dim, dropout)
        self.edge_reg = EdgeRegHead(output_dim)
```

### 3. Intégration LLM pour Génération de Défis

#### Service de Génération de Défis
```python
# backend/app/services/competenceTree.py
class CompetenceTreeService:
    def generate_challenge(self, skill_label: str, user_age: int) -> Dict[str, Any]:
        """Génère un défi personnalisé pour une compétence"""
        
    def _generate_challenge_with_llm(self, skill_label: str, 
                                   difficulty: str, user_age: int) -> Dict[str, Any]:
        """Utilise OpenAI pour générer des défis personnalisés"""
        prompt = f"""
        Tu dois générer un défi pratique pour développer la compétence "{skill_label}" 
        à un niveau {difficulty}.
        
        Le défi doit être:
        - Pratique et réalisable
        - Adapté à une personne de {user_age} ans
        - Mesurable avec des critères de succès clairs
        
        Réponds UNIQUEMENT en JSON avec cette structure:
        {{
            "title": "Titre du défi",
            "description": "Description détaillée",
            "success_criteria": "Critères de réussite",
            "estimated_duration": "Durée estimée",
            "resources_needed": "Ressources nécessaires"
        }}
        """
```

#### Templates de Prompts LLM
```python
# scripts/format_user_profile_esco_style.py
ESCO_SKILL_TEMPLATE = """
Tu convertis une compétence utilisateur en format ESCO structuré.

COMPÉTENCE: {skill_name}
NIVEAU: {skill_score}/5
CONTEXTE UTILISATEUR: {user_context}

Génère une description ESCO formelle incluant:
- PREFERREDLABEL: Nom standardisé de la compétence
- DESCRIPTION: Description complète et professionnelle
- APPLICATIONS: 3-5 applications concrètes
- PROGRESSION: Étapes pour améliorer cette compétence
"""
```

### 4. Interface React Flow

#### Composant Principal
```typescript
// frontend/src/components/jobs/JobSkillsTree.tsx
const JobSkillsTree: React.FC<JobSkillsTreeProps> = ({ jobId }) => {
    const [skillTreeData, setSkillTreeData] = useState<SkillTreeData | null>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    
    const convertToReactFlowFormat = useCallback((data: SkillTreeData) => {
        // Convertit les données ESCO en format React Flow
        const flowNodes: FlowNode[] = [];
        const flowEdges: FlowEdge[] = [];
        
        // Logique de conversion et positionnement
    }, []);
}
```

#### Composants de Nœuds Personnalisés
```typescript
// frontend/src/components/tree/CustomNodes.tsx
export const SkillNode = ({ data }: { data: any }) => {
    const [isCompleted, setIsCompleted] = useState(data.completed || false);
    const [showChallenge, setShowChallenge] = useState(false);
    
    return (
        <motion.div className={`skill-node ${isCompleted ? 'completed' : 'locked'}`}>
            <div className="node-header">
                <h4>{data.label}</h4>
                {data.xp_reward && <span className="xp-badge">{data.xp_reward} XP</span>}
            </div>
            
            {showChallenge && (
                <ChallengeCard 
                    challenge={data.challenge}
                    onComplete={() => handleChallengeComplete(data.id)}
                />
            )}
        </motion.div>
    );
};
```

### 5. Système de Gamification

#### Modèles de Données
```python
# backend/app/models/user_progress.py
class UserProgress(Base):
    __tablename__ = "user_progress"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    last_completed_node = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# backend/app/models/user_skill_tree.py  
class UserSkillTree(Base):
    __tablename__ = "user_skill_trees"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    graph_id = Column(String, nullable=False, unique=True)
    tree_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### API de Progression
```python
# backend/app/routers/user_progress.py
@router.post("/update", response_model=UserProgressResponse)
def update_user_progress(
    update: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Met à jour la progression XP de l'utilisateur"""
    
@router.patch("/node/{node_id}/complete")
def complete_challenge(node_id: int, db: Session = Depends(get_db)):
    """Marque un défi comme complété et attribue les XP"""
```

## Composants Nécessaires pour l'Implémentation

### 1. Backend - Services Core

#### A. Service de Découverte d'Ancres
```python
# backend/app/services/anchor_discovery_service.py
class AnchorDiscoveryService:
    def __init__(self, pinecone_index: str = "esco-368"):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(pinecone_index)
    
    def find_personalized_anchors(self, db: Session, user_id: int, 
                                 count: int = 5) -> List[Dict[str, Any]]:
        """
        Trouve 5 compétences d'ancrage personnalisées basées sur le profil utilisateur
        """
        # 1. Récupérer l'embedding utilisateur (ESCO ou OaSIS)
        user_embedding = self._get_user_embedding(db, user_id)
        
        # 2. Recherche vectorielle dans Pinecone
        results = self.index.query(
            vector=user_embedding.tolist(),
            top_k=count * 3,  # Plus de candidats pour diversification
            filter={"type": "skill"},  # Seulement les compétences
            include_metadata=True
        )
        
        # 3. Diversification des résultats
        anchors = self._diversify_anchors(results.matches, count)
        
        return anchors
    
    def _diversify_anchors(self, matches: List, target_count: int) -> List[Dict]:
        """Assure la diversité des compétences d'ancrage"""
        # Algorithme de diversification par clustering ou domaines
        pass
```

#### B. Service de Traversée Gamifiée
```python
# backend/app/services/gamified_traversal_service.py
class GamifiedTraversalService:
    def __init__(self):
        self.graph_service = GraphTraversalService()
        self.challenge_service = CompetenceTreeService()
    
    def create_interactive_skill_graph(self, db: Session, user_id: int,
                                     anchor_skills: List[str],
                                     max_depth: int = 6) -> Dict[str, Any]:
        """
        Crée un graphe de compétences interactif avec gamification
        """
        # 1. Traversée du graphe ESCO
        graph_data = self.graph_service.traverse_graph(
            anchor_node_ids=anchor_skills,
            max_depth=max_depth,
            max_nodes_per_level=5
        )
        
        # 2. Génération des défis LLM pour chaque nœud
        for node_id, node_data in graph_data["nodes"].items():
            if node_data["type"] == "skill":
                challenge = self.challenge_service.generate_challenge(
                    skill_label=node_data["label"],
                    user_age=self._get_user_age(db, user_id)
                )
                node_data["challenge"] = challenge
        
        # 3. Application de la logique de visibilité (70% cachés)
        self._apply_visibility_rules(graph_data, reveal_ratio=0.3)
        
        # 4. Sauvegarde dans la base de données
        graph_id = self._save_interactive_graph(db, user_id, graph_data)
        
        return {
            "graph_id": graph_id,
            "nodes": graph_data["nodes"],
            "edges": graph_data["edges"],
            "anchor_nodes": anchor_skills,
            "total_nodes": len(graph_data["nodes"]),
            "visible_nodes": len([n for n in graph_data["nodes"].values() if n.get("visible", False)])
        }
    
    def _apply_visibility_rules(self, graph_data: Dict, reveal_ratio: float = 0.3):
        """Applique les règles de visibilité (70% cachés)"""
        nodes = list(graph_data["nodes"].values())
        total_nodes = len(nodes)
        visible_count = int(total_nodes * reveal_ratio)
        
        # 1. Tous les nœuds d'ancrage sont visibles
        anchor_nodes = [n for n in nodes if n.get("depth", 0) == 0]
        for node in anchor_nodes:
            node["visible"] = True
            node["state"] = "available"
        
        # 2. Sélection intelligente des nœuds à révéler
        remaining_visible = visible_count - len(anchor_nodes)
        candidates = [n for n in nodes if n.get("depth", 0) > 0]
        
        # Prioriser les nœuds connectés aux ancres
        visible_candidates = self._select_strategic_nodes(candidates, remaining_visible)
        
        for node in visible_candidates:
            node["visible"] = True
            node["state"] = "locked"  # Visible mais verrouillé
        
        # 3. Cacher le reste
        for node in nodes:
            if not node.get("visible", False):
                node["visible"] = False
                node["state"] = "hidden"
```

#### C. Service de Gestion des Défis
```python
# backend/app/services/challenge_management_service.py
class ChallengeManagementService:
    def complete_challenge(self, db: Session, user_id: int, 
                          node_id: str, graph_id: str) -> Dict[str, Any]:
        """
        Gère la complétion d'un défi et le déblocage de nouveaux nœuds
        """
        # 1. Valider la complétion du défi
        challenge_data = self._get_challenge_data(db, graph_id, node_id)
        
        # 2. Attribuer les XP
        xp_earned = challenge_data.get("xp_reward", 25)
        self._award_xp(db, user_id, xp_earned, node_id)
        
        # 3. Marquer le nœud comme complété
        self._mark_node_completed(db, graph_id, node_id)
        
        # 4. Débloquer les nœuds suivants
        unlocked_nodes = self._unlock_connected_nodes(db, graph_id, node_id)
        
        # 5. Vérifier les achievements
        achievements = self._check_achievements(db, user_id, graph_id)
        
        return {
            "xp_earned": xp_earned,
            "unlocked_nodes": unlocked_nodes,
            "achievements": achievements,
            "node_completed": node_id
        }
    
    def _unlock_connected_nodes(self, db: Session, graph_id: str, 
                               completed_node_id: str) -> List[str]:
        """Débloque les nœuds connectés selon les règles de progression"""
        # Logique de déblocage basée sur les dépendances du graphe
        pass
```

### 2. Backend - API Endpoints

#### A. Router Principal
```python
# backend/app/routers/interactive_skills_graph.py
router = APIRouter(prefix="/api/v1/interactive-skills", tags=["interactive-skills"])

@router.post("/generate", response_model=InteractiveGraphResponse)
async def generate_interactive_skills_graph(
    request: InteractiveGraphRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Génère un nouveau graphe de compétences interactif"""
    
@router.get("/{graph_id}", response_model=InteractiveGraphResponse)
async def get_interactive_graph(
    graph_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Récupère un graphe existant"""

@router.post("/{graph_id}/complete-challenge")
async def complete_challenge(
    graph_id: str,
    request: ChallengeCompletionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Complète un défi et débloque de nouveaux nœuds"""

@router.get("/{graph_id}/anchors/suggest")
async def suggest_anchor_skills(
    graph_id: str,
    count: int = Query(5, description="Nombre de compétences d'ancrage"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Suggère des compétences d'ancrage personnalisées"""
```

#### B. Schémas Pydantic
```python
# backend/app/schemas/interactive_skills.py
class InteractiveGraphRequest(BaseModel):
    anchor_skills: Optional[List[str]] = None  # Si None, génération automatique
    max_depth: int = Field(6, ge=1, le=10)
    difficulty_level: str = Field("intermediate", regex="^(beginner|intermediate|advanced)$")
    focus_areas: Optional[List[str]] = None

class InteractiveGraphResponse(BaseModel):
    graph_id: str
    nodes: Dict[str, InteractiveNode]
    edges: List[InteractiveEdge]
    anchor_nodes: List[str]
    total_nodes: int
    visible_nodes: int
    user_progress: UserProgressSummary

class InteractiveNode(BaseModel):
    id: str
    label: str
    type: str  # skill, occupation, skillgroup
    depth: int
    visible: bool
    state: str  # available, locked, completed, hidden
    challenge: Optional[ChallengeData] = None
    xp_reward: int
    prerequisites: List[str]
    unlocks: List[str]

class ChallengeData(BaseModel):
    title: str
    description: str
    success_criteria: str
    estimated_duration: str
    resources_needed: str
    difficulty: str
    xp_reward: int

class ChallengeCompletionRequest(BaseModel):
    node_id: str
    completion_evidence: Optional[str] = None
    self_assessment: Optional[int] = Field(None, ge=1, le=5)
```

### 3. Frontend - Composants React

#### A. Composant Principal
```typescript
// frontend/src/components/interactive-skills/InteractiveSkillsGraph.tsx
interface InteractiveSkillsGraphProps {
    userId?: number;
    initialAnchors?: string[];
    onNodeComplete?: (nodeId: string, xpEarned: number) => void;
}

export const InteractiveSkillsGraph: React.FC<InteractiveSkillsGraphProps> = ({
    userId,
    initialAnchors,
    onNodeComplete
}) => {
    const [graphData, setGraphData] = useState<InteractiveGraphData | null>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const [showChallengeModal, setShowChallengeModal] = useState(false);
    
    // Conversion des données en format React Flow
    const convertToReactFlow = useCallback((data: InteractiveGraphData) => {
        const flowNodes: Node[] = Object.values(data.nodes).map(node => ({
            id: node.id,
            type: getNodeType(node),
            position: calculateNodePosition(node, data),
            data: {
                ...node,
                onNodeClick: handleNodeClick,
                onChallengeComplete: handleChallengeComplete
            }
        }));
        
        const flowEdges: Edge[] = data.edges.map(edge => ({
            id: `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            type: 'smoothstep',
            animated: edge.unlocked,
            style: getEdgeStyle(edge)
        }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);
    }, []);
    
    const handleNodeClick = useCallback((nodeId: string) => {
        const node = graphData?.nodes[nodeId];
        if (!node) return;
        
        if (node.state === 'available' && node.challenge) {
            setSelectedNode(nodeId);
            setShowChallengeModal(true);
        } else if (node.state === 'locked') {
            // Afficher les prérequis
            showPrerequisites(node.prerequisites);
        }
    }, [graphData]);
    
    const handleChallengeComplete = useCallback(async (nodeId: string) => {
        try {
            const response = await interactiveSkillsService.completeChallenge(
                graphData!.graph_id,
                nodeId
            );
            
            // Mettre à jour l'état local
            updateNodeState(nodeId, 'completed');
            unlockConnectedNodes(response.unlocked_nodes);
            
            // Callback parent
            onNodeComplete?.(nodeId, response.xp_earned);
            
            // Animation de succès
            triggerSuccessAnimation(nodeId);
            
        } catch (error) {
            console.error('Erreur lors de la complétion du défi:', error);
        }
    }, [graphData, onNodeComplete]);
    
    return (
        <div className="interactive-skills-graph">
            <div className="graph-header">
                <h2>Votre Parcours de Compétences Interactif</h2>
                <ProgressIndicator 
                    totalNodes={graphData?.total_nodes || 0}
                    completedNodes={getCompletedNodesCount()}
                    currentXP={userProgress?.total_xp || 0}
                />
            </div>
            
            <div className="graph-container">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    nodeTypes={nodeTypes}
                    edgeTypes={edgeTypes}
                    fitView
                    attributionPosition="bottom-left"
                >
                    <Background />
                    <Controls />
                    <MiniMap />
                </ReactFlow>
            </div>
            
            {showChallengeModal && selectedNode && (
                <ChallengeModal
                    node={graphData!.nodes[selectedNode]}
                    onComplete={() => handleChallengeComplete(selectedNode)}
                    onClose={() => setShowChallengeModal(false)}
                />
            )}
        </div>
    );
};
```

#### B. Types de Nœuds Personnalisés
```typescript
// frontend/src/components/interactive-skills/nodes/SkillNode.tsx
export const InteractiveSkillNode: React.FC<NodeProps> = ({ data }) => {
    const [isHovered, setIsHovered] = useState(false);
    const [showPreview, setShowPreview] = useState(false);
    
    const getNodeStyle = () => {
        const baseStyle = "interactive-skill-node";
        const stateStyle = `node-${data.state}`;
        const typeStyle = `node-${data.type}`;
        
        return `${baseStyle} ${stateStyle} ${typeStyle}`;
    };
    
    const handleClick = () => {
        if (data.state === 'available') {
            data.onNodeClick?.(data.id);
        } else if (data.state === 'locked') {
            setShowPreview(true);
        }
    };
    
    return (
        <motion.div
            className={getNodeStyle()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            onClick={handleClick}
        >
            <Handle type="target" position={Position.Top} />
            
            <div className="node-header">
                <div className="node-icon">
                    {getNodeIcon(data.type, data.state)}
                </div>
                <h4 className="node-title">{data.label}</h4>
            </div>
            
            <div className="node-content">
                {data.state === 'available' && (
                    <div className="challenge-preview">
                        <p className="challenge-title">{data.challenge?.title}</p>
                        <div className="xp-reward">
                            <Star className="xp-icon" />
                            <span>{data.xp_reward} XP</span>
                        </div>
                    </div>
                )}
                
                {data.state === 'locked' && (
                    <div className="locked-info">
                        <Lock className="lock-icon" />
                        <p>Complétez les prérequis</p>
                    </div>
                )}
                
                {data.state === 'completed' && (
                    <div className="completed-info">
                        <CheckCircle className="check-icon" />
                        <p>Complété!</p>
                    </div>
                )}
                
                {data.state === 'hidden' && (
                    <div className="hidden-info">
                        <Eye className="eye-icon" />
                        <p>À découvrir...</p>
                    </div>
                )}
            </div>
            
            <Handle type="source" position={Position.Bottom} />
            
            {isHovered && data.state !== 'hidden' && (
                <NodeTooltip node={data} />
            )}
            
            {showPreview && (
                <NodePreviewModal 
                    node={data}
                    onClose={() => setShowPreview(false)}
                />
            )}
        </motion.div>
    );
};
```

#### C. Modal de Défi
```typescript
// frontend/src/components/interactive-skills/ChallengeModal.tsx
interface ChallengeModalProps {
    node: InteractiveNode;
    onComplete: () => void;
    onClose: () => void;
}

export const ChallengeModal: React.FC<ChallengeModalProps> = ({
    node,
    onComplete,
    onClose
}) => {
    const [isCompleting, setIsCompleting] = useState(false);
    const [completionEvidence, setCompletionEvidence] = useState('');
    const [selfAssessment, setSelfAssessment] = useState<number>(3);
    
    const handleComplete = async () => {
        setIsCompleting(true);
        try {
            await onComplete();
            onClose();
        } catch (error) {
            console.error('Erreur lors de la complétion:', error);
        } finally {
            setIsCompleting(false);
        }
    };
    
    return (
        <AnimatePresence>
            <motion.div
                className="challenge-modal-overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
            >
                <motion.div
                    className="challenge-modal"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.8, opacity: 0 }}
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="modal-header">
                        <h2>{node.challenge?.title}</h2>
                        <button onClick={onClose} className="close-button">
                            <X />
                        </button>
                    </div>
                    
                    <div className="modal-content">
                        <div className="challenge-info">
                            <div className="info-item">
                                <Clock className="info-icon" />
                                <span>Durée estimée: {node.challenge?.estimated_duration}</span>
                            </div>
                            <div className="info-item">
                                <Target className="info-icon" />
                                <span>Difficulté: {node.challenge?.difficulty}</span>
                            </div>
                            <div className="info-item">
                                <Star className="info-icon" />
                                <span>Récompense: {node.xp_reward} XP</span>
                            </div>
                        </div>
                        
                        <div className="challenge-description">
                            <h3>Description du défi</h3>
                            <p>{node.challenge?.description}</p>
                        </div>
                        
                        <div className="success-criteria">
                            <h3>Critères de réussite</h3>
                            <p>{node.challenge?.success_criteria}</p>
                        </div>
                        
                        <div className="resources">
                            <h3>Ressources nécessaires</h3>
                            <p>{node.challenge?.resources_needed}</p>
                        </div>
                        
                        <div className="completion-form">
                            <h3>Complétion du défi</h3>
                            
                            <div className="form-group">
                                <label>Preuve de complétion (optionnel)</label>
                                <textarea
value={completionEvidence}
                                    onChange={(e) => setCompletionEvidence(e.target.value)}
                                    placeholder="Décrivez comment vous avez complété ce défi..."
                                    rows={4}
                                />
                            </div>
                            
                            <div className="form-group">
                                <label>Auto-évaluation (1-5)</label>
                                <div className="rating-selector">
                                    {[1, 2, 3, 4, 5].map(rating => (
                                        <button
                                            key={rating}
                                            type="button"
                                            className={`rating-button ${selfAssessment === rating ? 'selected' : ''}`}
                                            onClick={() => setSelfAssessment(rating)}
                                        >
                                            {rating}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div className="modal-footer">
                        <button onClick={onClose} className="cancel-button">
                            Annuler
                        </button>
                        <button 
                            onClick={handleComplete}
                            disabled={isCompleting}
                            className="complete-button"
                        >
                            {isCompleting ? 'Complétion...' : 'Marquer comme complété'}
                        </button>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};
```

### 4. Services Frontend

#### A. Service API
```typescript
// frontend/src/services/interactiveSkillsService.ts
class InteractiveSkillsService {
    private baseUrl = '/api/v1/interactive-skills';
    
    async generateGraph(request: InteractiveGraphRequest): Promise<InteractiveGraphResponse> {
        const response = await fetch(`${this.baseUrl}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify(request)
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la génération du graphe');
        }
        
        return response.json();
    }
    
    async getGraph(graphId: string): Promise<InteractiveGraphResponse> {
        const response = await fetch(`${this.baseUrl}/${graphId}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération du graphe');
        }
        
        return response.json();
    }
    
    async completeChallenge(graphId: string, nodeId: string, 
                           evidence?: string, selfAssessment?: number): Promise<ChallengeCompletionResponse> {
        const response = await fetch(`${this.baseUrl}/${graphId}/complete-challenge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({
                node_id: nodeId,
                completion_evidence: evidence,
                self_assessment: selfAssessment
            })
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la complétion du défi');
        }
        
        return response.json();
    }
    
    async suggestAnchors(count: number = 5): Promise<AnchorSuggestion[]> {
        const response = await fetch(`${this.baseUrl}/anchors/suggest?count=${count}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la suggestion d\'ancres');
        }
        
        return response.json();
    }
}

export const interactiveSkillsService = new InteractiveSkillsService();
```

#### B. Hooks React
```typescript
// frontend/src/hooks/useInteractiveSkillsGraph.ts
export const useInteractiveSkillsGraph = (userId?: number, initialAnchors?: string[]) => {
    const [graphData, setGraphData] = useState<InteractiveGraphData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    const generateGraph = useCallback(async (options?: InteractiveGraphRequest) => {
        setLoading(true);
        setError(null);
        
        try {
            const request: InteractiveGraphRequest = {
                anchor_skills: initialAnchors,
                max_depth: 6,
                difficulty_level: 'intermediate',
                ...options
            };
            
            const response = await interactiveSkillsService.generateGraph(request);
            setGraphData(response);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erreur inconnue');
        } finally {
            setLoading(false);
        }
    }, [initialAnchors]);
    
    const completeChallenge = useCallback(async (nodeId: string, evidence?: string, selfAssessment?: number) => {
        if (!graphData) return;
        
        try {
            const response = await interactiveSkillsService.completeChallenge(
                graphData.graph_id,
                nodeId,
                evidence,
                selfAssessment
            );
            
            // Mettre à jour l'état local
            setGraphData(prev => {
                if (!prev) return prev;
                
                const updatedNodes = { ...prev.nodes };
                
                // Marquer le nœud comme complété
                if (updatedNodes[nodeId]) {
                    updatedNodes[nodeId] = {
                        ...updatedNodes[nodeId],
                        state: 'completed'
                    };
                }
                
                // Débloquer les nœuds connectés
                response.unlocked_nodes.forEach(unlockedNodeId => {
                    if (updatedNodes[unlockedNodeId]) {
                        updatedNodes[unlockedNodeId] = {
                            ...updatedNodes[unlockedNodeId],
                            state: 'available',
                            visible: true
                        };
                    }
                });
                
                return {
                    ...prev,
                    nodes: updatedNodes
                };
            });
            
            return response;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erreur lors de la complétion');
            throw err;
        }
    }, [graphData]);
    
    return {
        graphData,
        loading,
        error,
        generateGraph,
        completeChallenge
    };
};
```

## Algorithmes et Logiques Métier

### 1. Algorithme de Sélection des Ancres

```python
# backend/app/algorithms/anchor_selection.py
class AnchorSelectionAlgorithm:
    def __init__(self, esco_graph: nx.Graph, user_embeddings: Dict[str, np.ndarray]):
        self.graph = esco_graph
        self.user_embeddings = user_embeddings
        
    def select_personalized_anchors(self, user_id: str, count: int = 5) -> List[str]:
        """
        Sélectionne 5 compétences d'ancrage personnalisées
        
        Critères de sélection:
        1. Similarité avec le profil utilisateur (40%)
        2. Diversité des domaines (30%)
        3. Potentiel de progression (20%)
        4. Popularité/importance dans ESCO (10%)
        """
        
        # 1. Candidats basés sur la similarité
        similarity_candidates = self._get_similarity_candidates(user_id, count * 3)
        
        # 2. Diversification par domaines
        diversified_candidates = self._diversify_by_domains(similarity_candidates, count * 2)
        
        # 3. Scoring final avec tous les critères
        final_scores = self._calculate_final_scores(diversified_candidates, user_id)
        
        # 4. Sélection des top 5
        selected_anchors = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:count]
        
        return [anchor_id for anchor_id, score in selected_anchors]
    
    def _calculate_final_scores(self, candidates: List[str], user_id: str) -> Dict[str, float]:
        """Calcule le score final pour chaque candidat"""
        scores = {}
        user_embedding = self.user_embeddings[user_id]
        
        for node_id in candidates:
            node_data = self.graph.nodes[node_id]
            node_embedding = node_data.get('embedding', np.zeros_like(user_embedding))
            
            # Similarité (40%)
            similarity_score = cosine_similarity([user_embedding], [node_embedding])[0][0]
            
            # Diversité (30%) - calculée par rapport aux autres candidats sélectionnés
            diversity_score = self._calculate_diversity_score(node_id, candidates)
            
            # Potentiel de progression (20%)
            progression_score = self._calculate_progression_potential(node_id)
            
            # Popularité (10%)
            popularity_score = self._calculate_popularity_score(node_id)
            
            final_score = (
                0.4 * similarity_score +
                0.3 * diversity_score +
                0.2 * progression_score +
                0.1 * popularity_score
            )
            
            scores[node_id] = final_score
            
        return scores
```

### 2. Algorithme de Traversée GraphSAGE

```python
# backend/app/algorithms/graphsage_traversal.py
class GraphSAGETraversalAlgorithm:
    def __init__(self, model: GraphSAGE, graph: nx.Graph):
        self.model = model
        self.graph = graph
        
    def traverse_from_anchors(self, anchor_nodes: List[str], 
                            max_depth: int = 6,
                            max_nodes_per_level: int = 5,
                            min_similarity: float = 0.3) -> Dict[str, Any]:
        """
        Traverse le graphe ESCO à partir des nœuds d'ancrage
        en utilisant GraphSAGE pour scorer les chemins
        """
        
        # Structure de données pour le résultat
        traversal_result = {
            "nodes": {},
            "edges": [],
            "levels": {},
            "paths": []
        }
        
        # Initialisation avec les nœuds d'ancrage
        current_level = anchor_nodes
        for anchor in anchor_nodes:
            traversal_result["nodes"][anchor] = {
                "id": anchor,
                "label": self.graph.nodes[anchor].get("label", anchor),
                "type": self.graph.nodes[anchor].get("type", "skill"),
                "depth": 0,
                "score": 1.0,
                "anchor": True
            }
        
        traversal_result["levels"][0] = anchor_nodes
        
        # Traversée niveau par niveau
        for depth in range(1, max_depth + 1):
            next_level_candidates = []
            
            # Pour chaque nœud du niveau actuel
            for current_node in current_level:
                # Obtenir les voisins
                neighbors = list(self.graph.neighbors(current_node))
                
                # Scorer les voisins avec GraphSAGE
                neighbor_scores = self._score_neighbors_with_graphsage(
                    current_node, neighbors, depth
                )
                
                # Filtrer par similarité minimale
                valid_neighbors = [
                    (neighbor, score) for neighbor, score in neighbor_scores.items()
                    if score >= min_similarity and neighbor not in traversal_result["nodes"]
                ]
                
                next_level_candidates.extend(valid_neighbors)
            
            # Sélectionner les meilleurs candidats pour ce niveau
            next_level_candidates.sort(key=lambda x: x[1], reverse=True)
            selected_nodes = next_level_candidates[:max_nodes_per_level]
            
            # Ajouter les nœuds sélectionnés
            current_level = []
            for node_id, score in selected_nodes:
                traversal_result["nodes"][node_id] = {
                    "id": node_id,
                    "label": self.graph.nodes[node_id].get("label", node_id),
                    "type": self.graph.nodes[node_id].get("type", "skill"),
                    "depth": depth,
                    "score": score,
                    "anchor": False
                }
                current_level.append(node_id)
            
            traversal_result["levels"][depth] = current_level
            
            # Arrêter si aucun nouveau nœud trouvé
            if not current_level:
                break
        
        # Construire les arêtes
        self._build_edges(traversal_result)
        
        return traversal_result
    
    def _score_neighbors_with_graphsage(self, source_node: str, 
                                      neighbors: List[str], depth: int) -> Dict[str, float]:
        """Utilise GraphSAGE pour scorer les voisins"""
        
        # Préparer les données pour GraphSAGE
        node_features = self._prepare_node_features([source_node] + neighbors)
        edge_index = self._prepare_edge_index(source_node, neighbors)
        
        # Prédiction avec le modèle
        with torch.no_grad():
            embeddings = self.model(node_features, edge_index)
            source_embedding = embeddings[0]  # Premier nœud = source
            neighbor_embeddings = embeddings[1:]  # Reste = voisins
            
            # Calcul de similarité
            similarities = torch.cosine_similarity(
                source_embedding.unsqueeze(0), 
                neighbor_embeddings, 
                dim=1
            )
        
        # Ajustement du score basé sur la profondeur
        depth_penalty = 0.9 ** depth  # Pénalité pour les nœuds plus profonds
        
        scores = {}
        for i, neighbor in enumerate(neighbors):
            base_score = similarities[i].item()
            adjusted_score = base_score * depth_penalty
            scores[neighbor] = adjusted_score
            
        return scores
```

### 3. Algorithme de Génération de Défis LLM

```python
# backend/app/algorithms/challenge_generation.py
class ChallengeGenerationAlgorithm:
    def __init__(self, openai_client):
        self.client = openai_client
        self.challenge_templates = self._load_challenge_templates()
        
    def generate_personalized_challenge(self, skill_node: Dict[str, Any], 
                                      user_profile: Dict[str, Any],
                                      difficulty: str = "intermediate") -> Dict[str, Any]:
        """
        Génère un défi personnalisé pour une compétence donnée
        """
        
        # 1. Analyser le contexte de la compétence
        skill_context = self._analyze_skill_context(skill_node)
        
        # 2. Adapter au profil utilisateur
        user_context = self._extract_user_context(user_profile)
        
        # 3. Construire le prompt LLM
        prompt = self._build_challenge_prompt(skill_node, skill_context, user_context, difficulty)
        
        # 4. Générer avec LLM
        llm_response = self._call_llm_for_challenge(prompt)
        
        # 5. Post-traitement et validation
        challenge_data = self._process_llm_response(llm_response, skill_node, difficulty)
        
        return challenge_data
    
    def _build_challenge_prompt(self, skill_node: Dict, skill_context: Dict, 
                               user_context: Dict, difficulty: str) -> str:
        """Construit un prompt contextualisé pour la génération de défi"""
        
        prompt = f"""
Tu es un expert en développement de compétences qui crée des défis pratiques et engageants.

COMPÉTENCE CIBLE:
- Nom: {skill_node['label']}
- Type: {skill_node['type']}
- Domaine: {skill_context.get('domain', 'Général')}
- Niveau de complexité: {skill_context.get('complexity_level', 'Moyen')}

CONTEXTE UTILISATEUR:
- Âge: {user_context.get('age', 'Non spécifié')}
- Niveau d'éducation: {user_context.get('education_level', 'Non spécifié')}
- Expérience professionnelle: {user_context.get('experience', 'Non spécifiée')}
- Intérêts: {', '.join(user_context.get('interests', []))}

NIVEAU DE DIFFICULTÉ: {difficulty}

INSTRUCTIONS:
Crée un défi pratique qui:
1. Développe concrètement la compétence "{skill_node['label']}"
2. Est adapté au niveau {difficulty}
3. Peut être réalisé par l'utilisateur dans son contexte
4. Inclut des critères de réussite mesurables
5. Propose des ressources d'apprentissage spécifiques

CONTRAINTES:
- Durée: Entre 2 et 8 heures selon la difficulté
- Réalisable sans équipement spécialisé coûteux
- Résultats vérifiables par auto-évaluation

Réponds UNIQUEMENT en JSON avec cette structure exacte:
{{
    "title": "Titre accrocheur du défi (max 60 caractères)",
    "description": "Description détaillée du défi et des étapes à suivre",
    "success_criteria": "Critères spécifiques pour valider la réussite",
    "estimated_duration": "Durée estimée (ex: '4-6 heures')",
    "resources_needed": "Liste des ressources et outils nécessaires",
    "learning_resources": [
        "Ressource 1 (lien ou description)",
        "Ressource 2 (lien ou description)"
    ],
    "difficulty_justification": "Pourquoi ce défi correspond au niveau {difficulty}"
}}
"""
        
        return prompt
    
    def _analyze_skill_context(self, skill_node: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le contexte d'une compétence dans ESCO"""
        
        # Extraction des métadonnées ESCO
        skill_type = skill_node.get('type', 'skill')
        skill_label = skill_node.get('label', '')
        
        # Classification par domaine
        domain = self._classify_skill_domain(skill_label)
        
        # Niveau de complexité basé sur les connexions
        complexity_level = self._assess_complexity_level(skill_node)
        
        return {
            "domain": domain,
            "complexity_level": complexity_level,
            "skill_type": skill_type,
            "related_occupations": skill_node.get('related_occupations', []),
            "prerequisite_skills": skill_node.get('prerequisites', [])
        }
    
    def _classify_skill_domain(self, skill_label: str) -> str:
        """Classifie une compétence par domaine"""
        
        domain_keywords = {
            "Technologie": ["programming", "software", "data", "digital", "computer", "IT"],
            "Communication": ["communication", "presentation", "writing", "speaking", "language"],
            "Management": ["leadership", "management", "project", "team", "planning"],
            "Créativité": ["design", "creative", "art", "innovation", "visual"],
            "Analytique": ["analysis", "research", "problem", "critical", "thinking"],
            "Commercial": ["sales", "marketing", "business", "customer", "negotiation"]
        }
        
        skill_lower = skill_label.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in skill_lower for keyword in keywords):
                return domain
                
        return "Général"
```

### 4. Algorithme de Visibilité et Déblocage

```python
# backend/app/algorithms/visibility_algorithm.py
class VisibilityAlgorithm:
    def __init__(self, graph_data: Dict[str, Any]):
        self.graph_data = graph_data
        self.nodes = graph_data["nodes"]
        self.edges = graph_data["edges"]
        
    def apply_visibility_rules(self, reveal_ratio: float = 0.3) -> Dict[str, Any]:
        """
        Applique les règles de visibilité pour cacher ~70% des nœuds
        """
        
        # 1. Identifier les nœuds d'ancrage (toujours visibles)
        anchor_nodes = [node_id for node_id, node in self.nodes.items() 
                       if node.get("anchor", False) or node.get("depth", 0) == 0]
        
        # 2. Calculer le nombre de nœuds à révéler
        total_nodes = len(self.nodes)
        target_visible = int(total_nodes * reveal_ratio)
        remaining_to_reveal = max(0, target_visible - len(anchor_nodes))
        
        # 3. Sélectionner stratégiquement les nœuds à révéler
        strategic_nodes = self._select_strategic_nodes(anchor_nodes, remaining_to_reveal)
        
        # 4. Appliquer les états de visibilité
        self._apply_node_states(anchor_nodes, strategic_nodes)
        
        # 5. Configurer les règles de déblocage
        self._configure_unlock_rules()
        
        return self.graph_data
    
    def _select_strategic_nodes(self, anchor_nodes: List[str], count: int) -> List[str]:
        """Sélectionne stratégiquement les nœuds à révéler"""
        
        candidates = [node_id for node_id in self.nodes.keys() 
                     if node_id not in anchor_nodes]
        
        # Scoring des candidats
        scored_candidates = []
        
        for node_id in candidates:
            node = self.nodes[node_id]
            score = self._calculate_reveal_score(node_id, node, anchor_nodes)
            scored_candidates.append((node_id, score))
        
        # Trier par score et sélectionner les meilleurs
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        selected = [node_id for node_id, score in scored_candidates[:count]]
        
        return selected
    
    def _calculate_reveal_score(self, node_id: str, node: Dict, anchor_nodes: List[str]) -> float:
        """Calcule le score de révélation pour un nœud"""
        
        score = 0.0
        
        # 1. Proximité aux ancres (40%)
        min_distance_to_anchor = self._min_distance_to_anchors(node_id, anchor_nodes)
        proximity_score = 1.0 / (1.0 + min_distance_to_anchor)
        score += 0.4 * proximity_score
        
        # 2. Importance dans le graphe (30%)
        importance_score = self._calculate_node_importance(node_id)
        score += 0.3 * importance_score
        
        # 3. Diversité (20%)
        diversity_score = self._calculate_diversity_contribution(node_id, anchor_nodes)
        score += 0.2 * diversity_score
        
        # 4. Potentiel pédagogique (10%)
        pedagogical_score = self._calculate_pedagogical_value(node)
        score += 0.1 * pedagogical_score
        
        return score
    
    def unlock_connected_nodes(self, completed_node_id: str) -> List[str]:
        """Débloque les nœuds connectés après complétion d'un défi"""
        
        unlocked_nodes = []
        completed_node = self.nodes[completed_node_id]
        
        # Marquer le nœud comme complété
        completed_node["state"] = "completed"
        
        # Trouver les nœuds connectés
        connected_nodes = self._find_connected_nodes(completed_node_id)
        
        for connected_id in connected_nodes:
            connected_node = self.nodes[connected_id]
            
            # Vérifier les conditions de déblocage
            if self._can_unlock_node(connected_id, completed_node_id):
                # Révéler et débloquer le nœud
                connected_node["visible"] = True
                connected_node["state"] = "available"
                unlocked_nodes.append(connected_id)
                
                # Effet de cascade : révéler quelques nœuds cachés supplémentaires
                cascade_nodes = self._trigger_cascade_reveal(connected_id)
                unlocked_nodes.extend(cascade_nodes)
        
        return unlocked_nodes
    
    def _can_unlock_node(self, node_id: str, completed_node_id: str) -> bool:
        """Vérifie si un nœud peut être débloqué"""
        
        node = self.nodes[node_id]
        
        # Ne pas débloquer les nœuds déjà visibles/complétés
        if node.get("visible", False) and node.get("state") != "hidden":
            return False
        
        # Vérifier les prérequis
        prerequisites = node.get("prerequisites", [])
        if prerequisites:
            completed_prerequisites = [
                prereq for prereq in prerequisites
                if self.nodes.get(prereq, {}).get("state") == "completed"
            ]
            
            # Tous les prérequis doivent être complétés
            if len(completed_prerequisites) < len(prerequisites):
                return False
        
        # Vérifier la distance maximale depuis les ancres
        max_unlock_distance = 3  # Ne pas débloquer trop loin
        min_distance = self._min_distance_to_completed_nodes(node_id)
        
        return min_distance <= max_unlock_distance
```

## Plan d'Implémentation Détaillé

### Phase 1: Infrastructure Backend (2-3 semaines)

#### Semaine 1: Services Core
1. **Service de Découverte d'Ancres** ([`anchor_discovery_service.py`](backend/app/services/anchor_discovery_service.py))
   - Intégration avec Pinecone pour recherche vectorielle
   - Algorithme de diversification des ancres
   - Tests unitaires

2. **Service de Traversée Gamifiée** ([`gamified_traversal_service.py`](backend/app/services/gamified_traversal_service.py))
   - Extension du service GraphSAGE existant
   - Logique de visibilité (70% cachés)
   - Intégration avec génération de défis

#### Semaine 2: Génération de Défis LLM
1. **Extension du Service de Compétences** ([`competenceTree.py`](backend/app/services/competenceTree.py))
   - Amélioration de [`generate_challenge()`](backend/app/services/competenceTree.py:1095)
   - Templates de prompts contextualisés
   - Validation et post-traitement des réponses LLM

2. **Service de Gestion des Défis** ([`challenge_management_service.py`](backend/app/services/challenge_management_service.py))
   - Logique de complétion et déblocage
   - Système de récompenses XP
   - Gestion des achievements

#### Semaine 3: API et Base de Données
1. **Nouveaux Endpoints** ([`interactive_skills_graph.py`](backend/app/routers/interactive_skills_graph.py))
   - Routes de génération et récupération
   - Endpoints de complétion de défis
   - Suggestion d'ancres personnalisées

2. **Modèles de Données** 
   - Extension de [`user_skill_tree.py`](backend/app/models/user_skill_tree.py)
   - Nouveaux schémas Pydantic ([`interactive_skills.py`](backend/app/schemas/interactive_skills.py))
   - Migrations Alembic

### Phase 2: Interface Frontend (2-3 semaines)

#### Semaine 1: Composants Core
1. **Composant Principal** ([`InteractiveSkillsGraph.tsx`](frontend/src/components/interactive-skills/InteractiveSkillsGraph.tsx))
   - Intégration React Flow
   - Gestion d'état avec hooks
   - Conversion des données ESCO

2. **Nœuds Personnalisés** ([`InteractiveSkillNode.tsx`](frontend/src/components/interactive-skills/nodes/InteractiveSkillNode.tsx))
   - États visuels (available, locked, completed, hidden)
   - Animations et interactions
   - Tooltips informatifs

#### Semaine 2: Modals et Interactions
1. **Modal de Défi** ([`ChallengeModal.tsx`](frontend/src/components/interactive-skills/ChallengeModal.tsx))
   - Interface de complétion
   - Formulaires d'auto-évaluation
   - Animations de succès

2. **Composants de Progression**
   - Indicateurs XP et niveau
   - Barres de progression
   - Notifications d'achievements

#### Semaine 3: Services et Hooks
1. **Service API** ([`interactiveSkillsService.ts`](frontend/src/services/interactiveSkillsService.ts))
   - Appels API typés
   - Gestion d'erreurs
   - Cache et optimisations

2. **Hooks Personnalisés** ([`useInteractiveSkillsGraph.ts`](frontend/src/hooks/useInteractiveSkillsGraph.ts))
   - Gestion d'état complexe
   - Logique de mise à jour
   - Optimisations de performance

### Phase 3: Intégration et Tests (1-2 semaines)

#### Semaine 1: Tests et Optimisations
1. **Tests Backend**
   - Tests unitaires des algorithmes
   - Tests d'intégration API
   - Tests de performance GraphSAGE

2. **Tests Frontend**
   - Tests de composants React
   - Tests d'intégration E2E
   - Tests de performance React Flow

#### Semaine 2: Déploiement et Monitoring
1. **Déploiement**
   - Configuration production
   - Monitoring des performances
   - Métriques d'utilisation

2. **Documentation**
   - Documentation API
   - Guide d'utilisation
   - Exemples d'intégration

## Métriques et KPIs

###
## Métriques et KPIs

### 1. Métriques d'Engagement
```python
# backend/app/analytics/engagement_metrics.py
class EngagementMetrics:
    def calculate_discovery_rate(self, user_id: int, graph_id: str) -> float:
        """Pourcentage de nœuds découverts par rapport au total"""
        
    def calculate_completion_rate(self, user_id: int, graph_id: str) -> float:
        """Pourcentage de défis complétés par rapport aux nœuds visibles"""
        
    def calculate_session_duration(self, user_id: int) -> Dict[str, float]:
        """Durée moyenne des sessions d'exploration"""
        
    def calculate_return_frequency(self, user_id: int) -> float:
        """Fréquence de retour sur la plateforme"""
```

### 2. Métriques de Performance
- **Temps de génération de graphe**: < 3 secondes
- **Temps de réponse LLM**: < 2 secondes pour génération de défi
- **Temps de traversée GraphSAGE**: < 1 seconde pour 100 nœuds
- **Utilisation mémoire**: < 500MB par session utilisateur

### 3. Métriques Pédagogiques
- **Taux de complétion des défis**: Objectif 70%
- **Progression moyenne**: 5-10 nœuds par session
- **Satisfaction utilisateur**: Score NPS > 8
- **Temps d'apprentissage par compétence**: 2-6 heures

## Considérations Techniques

### 1. Scalabilité
```python
# Configuration pour la montée en charge
GRAPHSAGE_CONFIG = {
    "batch_size": 1024,
    "max_concurrent_users": 100,
    "cache_ttl": 3600,  # 1 heure
    "model_optimization": "tensorrt"  # Pour GPU
}

PINECONE_CONFIG = {
    "index_type": "performance",  # vs accuracy
    "replicas": 3,
    "shards": 2
}
```

### 2. Optimisations Performance
- **Cache Redis** pour graphes fréquemment accédés
- **Pagination** pour grandes traversées
- **Lazy loading** des nœuds distants
- **Compression** des données ESCO

### 3. Sécurité et Privacy
- **Chiffrement** des données utilisateur
- **Anonymisation** des métriques d'usage
- **Rate limiting** sur les appels LLM
- **Validation** stricte des inputs

## Intégrations Existantes

### 1. Avec le Système de Recommandations
```python
# backend/app/integrations/recommendation_integration.py
class RecommendationIntegration:
    def enrich_graph_with_career_paths(self, graph_data: Dict, user_id: int):
        """Enrichit le graphe avec des chemins de carrière recommandés"""
        
        # Utilise le service existant
        career_recommendations = self.career_service.get_recommendations(user_id)
        
        # Ajoute des nœuds "occupation" connectés aux compétences
        for recommendation in career_recommendations:
            self._add_career_node_to_graph(graph_data, recommendation)
```

### 2. Avec le Système Holland/RIASEC
```python
# backend/app/integrations/holland_integration.py
class HollandIntegration:
    def personalize_anchors_with_riasec(self, user_id: int, 
                                       candidate_anchors: List[str]) -> List[str]:
        """Personnalise les ancres basé sur le profil RIASEC"""
        
        riasec_scores = self.holland_service.get_user_riasec_scores(user_id)
        
        # Filtre et pondère les ancres selon le profil RIASEC
        personalized_anchors = self._weight_anchors_by_riasec(
            candidate_anchors, riasec_scores
        )
        
        return personalized_anchors
```

### 3. Avec le Système de Profils
```python
# backend/app/integrations/profile_integration.py
class ProfileIntegration:
    def adapt_challenges_to_profile(self, challenge_data: Dict, 
                                   user_profile: Dict) -> Dict:
        """Adapte les défis au profil utilisateur"""
        
        # Ajuste la difficulté selon l'expérience
        if user_profile.get("years_experience", 0) > 5:
            challenge_data["difficulty"] = "advanced"
            challenge_data["xp_reward"] *= 1.5
        
        # Adapte le contexte selon l'industrie
        industry = user_profile.get("industry")
        if industry:
            challenge_data["context"] = f"Dans le contexte {industry}"
        
        return challenge_data
```

## Templates de Prompts LLM Avancés

### 1. Prompt de Génération de Défi Contextualisé
```python
CONTEXTUAL_CHALLENGE_PROMPT = """
Tu es un expert en développement de compétences qui crée des défis pratiques et engageants.

CONTEXTE ESCO:
- Compétence: {skill_label}
- URI ESCO: {skill_uri}
- Description ESCO: {skill_description}
- Compétences liées: {related_skills}
- Occupations utilisant cette compétence: {related_occupations}

PROFIL UTILISATEUR:
- Âge: {user_age}
- Niveau d'éducation: {education_level}
- Expérience: {years_experience} ans en {industry}
- Compétences existantes: {existing_skills}
- Objectifs de carrière: {career_goals}
- Style d'apprentissage: {learning_style}

CONTEXTE DU GRAPHE:
- Nœuds précédemment complétés: {completed_nodes}
- Prochaines compétences à débloquer: {next_skills}
- Progression actuelle: {completion_percentage}% du graphe exploré

NIVEAU DE DIFFICULTÉ: {difficulty}
- Débutant: 2-4h, concepts de base, auto-évaluation simple
- Intermédiaire: 4-6h, application pratique, projet concret
- Avancé: 6-8h, résolution de problèmes complexes, innovation

INSTRUCTIONS SPÉCIALISÉES:
1. Le défi doit être DIRECTEMENT applicable dans le contexte professionnel de l'utilisateur
2. Inclure des éléments qui préparent aux compétences suivantes: {next_skills}
3. Référencer les compétences déjà acquises: {completed_nodes}
4. Adapter le vocabulaire au niveau d'éducation: {education_level}
5. Proposer des variantes selon le style d'apprentissage: {learning_style}

CONTRAINTES TECHNIQUES:
- Réalisable avec les outils standards de l'industrie {industry}
- Résultats mesurables et vérifiables
- Ressources d'apprentissage accessibles gratuitement
- Applicable dans un environnement de travail réel

Réponds UNIQUEMENT en JSON avec cette structure:
{{
    "title": "Titre accrocheur (max 60 caractères)",
    "description": "Description détaillée avec étapes spécifiques",
    "success_criteria": "Critères mesurables de réussite",
    "estimated_duration": "Durée réaliste",
    "resources_needed": "Outils et ressources spécifiques",
    "learning_resources": [
        "Ressource 1 avec lien si possible",
        "Ressource 2 avec lien si possible",
        "Ressource 3 avec lien si possible"
    ],
    "industry_context": "Application spécifique dans {industry}",
    "skill_connections": "Comment ce défi prépare aux compétences suivantes",
    "assessment_method": "Méthode d'auto-évaluation détaillée",
    "variations": {{
        "visual_learner": "Adaptation pour apprenant visuel",
        "kinesthetic_learner": "Adaptation pour apprenant kinesthésique",
        "auditory_learner": "Adaptation pour apprenant auditif"
    }},
    "difficulty_justification": "Justification du niveau {difficulty}"
}}
"""
```

### 2. Prompt d'Enrichissement de Nœuds
```python
NODE_ENRICHMENT_PROMPT = """
Tu enrichis les métadonnées d'un nœud de compétence ESCO pour l'affichage interactif.

NŒUD ESCO:
- ID: {node_id}
- Label: {node_label}
- Type: {node_type}
- Description: {node_description}

CONTEXTE DANS LE GRAPHE:
- Profondeur: {depth}
- Nœuds parents: {parent_nodes}
- Nœuds enfants: {child_nodes}
- Score de pertinence: {relevance_score}

PROFIL UTILISATEUR:
- Domaines d'intérêt: {user_interests}
- Niveau d'expérience: {experience_level}
- Objectifs: {career_objectives}

Génère un enrichissement JSON:
{{
    "display_title": "Titre attractif pour l'interface",
    "short_description": "Description courte (max 100 caractères)",
    "motivation_text": "Pourquoi cette compétence est importante pour l'utilisateur",
    "career_impact": "Impact sur les objectifs de carrière",
    "difficulty_indicator": "Estimation de difficulté (1-5)",
    "time_investment": "Temps typique pour maîtriser",
    "prerequisites_explanation": "Explication des prérequis",
    "unlock_benefits": "Bénéfices du déblocage de cette compétence",
    "related_tools": ["Outil 1", "Outil 2", "Outil 3"],
    "industry_relevance": "Pertinence dans l'industrie de l'utilisateur",
    "trending_score": "Score de tendance (1-10)",
    "learning_path_suggestions": "Suggestions de parcours d'apprentissage"
}}
"""
```

## Algorithmes d'Optimisation

### 1. Optimisation de la Génération de Graphe
```python
# backend/app/optimizations/graph_generation_optimizer.py
class GraphGenerationOptimizer:
    def __init__(self):
        self.cache = Redis()
        self.model_cache = {}
        
    def optimize_traversal_for_user(self, user_profile: Dict, 
                                   anchor_skills: List[str]) -> Dict[str, Any]:
        """
        Optimise la traversée GraphSAGE basée sur le profil utilisateur
        """
        
        # 1. Cache intelligent basé sur des profils similaires
        similar_profiles = self._find_similar_user_profiles(user_profile)
        cached_result = self._check_similar_graph_cache(similar_profiles, anchor_skills)
        
        if cached_result:
            return self._adapt_cached_graph(cached_result, user_profile)
        
        # 2. Optimisation des paramètres GraphSAGE
        optimized_params = self._optimize_graphsage_params(user_profile)
        
        # 3. Pré-calcul des embeddings fréquents
        precomputed_embeddings = self._get_precomputed_embeddings(anchor_skills)
        
        # 4. Traversée optimisée
        graph_result = self._perform_optimized_traversal(
            anchor_skills, optimized_params, precomputed_embeddings
        )
        
        # 5. Cache du résultat
        self._cache_graph_result(user_profile, anchor_skills, graph_result)
        
        return graph_result
    
    def _optimize_graphsage_params(self, user_profile: Dict) -> Dict[str, Any]:
        """Optimise les paramètres GraphSAGE selon le profil"""
        
        base_params = {
            "max_depth": 6,
            "max_nodes_per_level": 5,
            "min_similarity": 0.3
        }
        
        # Ajustements basés sur l'expérience
        experience_level = user_profile.get("years_experience", 0)
        
        if experience_level < 2:
            # Débutants: graphe plus simple et focalisé
            base_params.update({
                "max_depth": 4,
                "max_nodes_per_level": 3,
                "min_similarity": 0.4
            })
        elif experience_level > 10:
            # Experts: graphe plus complexe et diversifié
            base_params.update({
                "max_depth": 8,
                "max_nodes_per_level": 7,
                "min_similarity": 0.25
            })
        
        return base_params
```

### 2. Optimisation des Appels LLM
```python
# backend/app/optimizations/llm_optimizer.py
class LLMOptimizer:
    def __init__(self):
        self.prompt_cache = {}
        self.response_cache = Redis()
        
    def optimize_challenge_generation(self, skill_nodes: List[Dict], 
                                    user_profile: Dict) -> List[Dict]:
        """
        Optimise la génération de défis en batch
        """
        
        # 1. Groupement des compétences similaires
        skill_groups = self._group_similar_skills(skill_nodes)
        
        # 2. Génération en batch pour chaque groupe
        all_challenges = []
        
        for group in skill_groups:
            # Cache check
            cache_key = self._generate_cache_key(group, user_profile)
            cached_challenges = self._get_cached_challenges(cache_key)
            
            if cached_challenges:
                all_challenges.extend(cached_challenges)
            else:
                # Génération batch
                batch_challenges = self._generate_batch_challenges(group, user_profile)
                all_challenges.extend(batch_challenges)
                
                # Cache des résultats
                self._cache_challenges(cache_key, batch_challenges)
        
        return all_challenges
    
    def _generate_batch_challenges(self, skill_group: List[Dict], 
                                 user_profile: Dict) -> List[Dict]:
        """Génère des défis en batch pour un groupe de compétences"""
        
        # Prompt optimisé pour génération multiple
        batch_prompt = self._build_batch_prompt(skill_group, user_profile)
        
        # Appel LLM unique pour tout le groupe
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu génères des défis en batch pour plusieurs compétences."},
                {"role": "user", "content": batch_prompt}
            ],
            temperature=0.7
        )
        
        # Parse et valide les réponses
        challenges = self._parse_batch_response(response.choices[0].message.content)
        
        return challenges
```

## Monitoring et Analytics

### 1. Dashboard de Performance
```python
# backend/app/monitoring/performance_dashboard.py
class PerformanceDashboard:
    def get_system_metrics(self) -> Dict[str, Any]:
        """Métriques système en temps réel"""
        return {
            "graphsage_performance": {
                "avg_inference_time": self._get_avg_inference_time(),
                "model_memory_usage": self._get_model_memory_usage(),
                "cache_hit_rate": self._get_cache_hit_rate()
            },
            "llm_performance": {
                "avg_response_time": self._get_llm_response_time(),
                "token_usage": self._get_token_usage(),
                "error_rate": self._get_llm_error_rate()
            },
            "user_engagement": {
                "active_sessions": self._get_active_sessions(),
                "avg_session_duration": self._get_avg_session_duration(),
                "completion_rates": self._get_completion_rates()
            }
        }
    
    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Analytics spécifiques à un utilisateur"""
        return {
            "learning_progress": {
                "skills_discovered": self._count_discovered_skills(user_id),
                "challenges_completed": self._count_completed_challenges(user_id),
                "xp_earned": self._get_total_xp(user_id),
                "learning_velocity": self._calculate_learning_velocity(user_id)
            },
            "engagement_patterns": {
                "preferred_session_times": self._get_session_patterns(user_id),
                "skill_preferences": self._get_skill_preferences(user_id),
                "difficulty_progression": self._get_difficulty_progression(user_id)
            }
        }
```

### 2. A/B Testing Framework
```python
# backend/app/experiments/ab_testing.py
class ABTestingFramework:
    def __init__(self):
        self.experiments = {}
        
    def create_experiment(self, experiment_name: str, variants: Dict[str, Any]):
        """Crée une nouvelle expérience A/B"""
        self.experiments[experiment_name] = {
            "variants": variants,
            "user_assignments": {},
            "metrics": {}
        }
    
    def assign_user_to_variant(self, user_id: int, experiment_name: str) -> str:
        """Assigne un utilisateur à une variante"""
        if experiment_name not in self.experiments:
            return "control"
        
        # Hash stable basé sur user_id
        hash_value = hash(f"{user_id}_{experiment_name}") % 100
        
        # Distribution 50/50 par défaut
        variant = "treatment" if hash_value < 50 else "control"
        
        self.experiments[experiment_name]["user_assignments"][user_id] = variant
        return variant
    
    def track_metric(self, user_id: int, experiment_name: str, 
                    metric_name: str, value: float):
        """Enregistre une métrique pour l'expérience"""
        if experiment_name not in self.experiments:
            return
        
        variant = self.experiments[experiment_name]["user_assignments"].get(user_id)
        if not variant:
            return
        
        if experiment_name not in self.experiments:
            self.experiments[experiment_name]["metrics"] = {}
        
        if variant not in self.experiments[experiment_name]["metrics"]:
            self.experiments[experiment_name]["metrics"][variant] = {}
        
        if metric_name not in self.experiments[experiment_name]["metrics"][variant]:
            self.experiments[experiment_name]["metrics"][variant][metric_name] = []
        
        self.experiments[experiment_name]["metrics"][variant][metric_name].append(value)
```

## Conclusion et Prochaines Étapes

### Résumé de l'Architecture

Cette analyse complète documente tous les composants nécessaires pour implémenter le **graphique de compétences interactif ESCO avec GraphSAGE et LLM**. L'architecture s'appuie sur :

1. **Fondation ESCO solide** : 21,169 nœuds et 153,951 arêtes déjà chargées
2. **Moteur GraphSAGE existant** : Modèles pré-entraînés pour la traversée intelligente
3. **Intégration LLM avancée** : Génération de défis contextualisés et personnalisés
4. **Interface React Flow moderne** : Visualisation interactive et engageante
5. **Système de gamification complet** : XP, déblocages, progression

### Composants Clés à Développer

#### Backend (Priorité Haute)
- [`anchor_discovery_service.py`](backend/app/services/anchor_discovery_service.py) - Découverte d'ancres personnalisées
- [`gamified_traversal_service.py`](backend/app/services/gamified_traversal_service.py) - Traversée avec gamification
- [`challenge_management_service.py`](backend/app/services/challenge_management_service.py) - Gestion des défis et déblocages
- [`interactive_skills_graph.py`](backend/app/routers/interactive_skills_graph.py) - API endpoints

#### Frontend (Priorité Haute)
- [`InteractiveSkillsGraph.tsx`](frontend/src/components/interactive-skills/InteractiveSkillsGraph.tsx) - Composant principal
- [`InteractiveSkillNode.tsx`](frontend/src/components/interactive-skills/nodes/InteractiveSkillNode.tsx) - Nœuds personnalisés
- [`ChallengeModal.tsx`](frontend/src/components/interactive-skills/ChallengeModal.tsx) - Interface de défis
- [`interactiveSkillsService.ts`](frontend/src/services/interactiveSkillsService.ts) - Service API

### Intégrations Existantes

La fonctionnalité s'intègre parfaitement avec :
- **Service de recommandations** ([`Swipe_career_recommendation_service.py`](backend/app/services/Swipe_career_recommendation_service.py))
- **Système Holland/RIASEC** ([`LLMholland_service.py`](backend/app/services/LLMholland_service.py))
- **Profils utilisateur** ([`user_profile.py`](backend/app/models/user_profile.py))
- **Système de progression** ([`user_progress.py`](backend/app/models/user_progress.py))

### Estimation de Développement

**Total estimé : 6-8 semaines**
- Phase 1 (Backend) : 2-3 semaines
- Phase 2 (Frontend) : 2-3 semaines  
- Phase 3 (Tests/Intégration) : 1-2 semaines

### Métriques de Succès

- **Engagement** : 70% de taux de complétion des défis
- **Performance** : < 3s génération de graphe, < 2s réponse LLM
- **Découverte** : 5-10 nœuds explorés par session
- **Rétention** : Retour utilisateur dans les 7 jours

Cette architecture garantit une expérience d'apprentissage **personnalisée**, **engageante** et **évolutive** qui transforme l'exploration des compétences ESCO en un parcours gamifié et découverte progressive.
## Détails d'Implémentation Spécifiques

### 1. Pipeline d'Extraction LLM des 5 Compétences Principales

#### Service d'Extraction Automatique
```python
# backend/app/services/llm_skill_extractor.py
class LLMSkillExtractorService:
    """
    Service pour extraire automatiquement les 5 compétences principales
    basé sur le profil utilisateur complet
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.esco_alignment_service = ESCOAlignmentService()
        
    def extract_top_skills_from_profile(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Extrait les 5 compétences principales du profil utilisateur complet
        """
        # 1. Récupérer toutes les données utilisateur
        user_profile = self._get_comprehensive_user_profile(db, user_id)
        
        # 2. Construire le prompt contextualisé
        extraction_prompt = self._build_skill_extraction_prompt(user_profile)
        
        # 3. Appel LLM pour extraction
        extracted_skills = self._call_llm_for_extraction(extraction_prompt)
        
        # 4. Alignement sémantique avec ESCO
        aligned_skills = self.esco_alignment_service.align_skills_with_esco(extracted_skills)
        
        # 5. Validation et scoring
        validated_skills = self._validate_and_score_skills(aligned_skills, user_profile)
        
        return validated_skills[:5]  # Top 5
    
    def _get_comprehensive_user_profile(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Récupère le profil utilisateur complet"""
        
        # Profil de base
        user_query = text("""
            SELECT u.*, up.* FROM users u 
            LEFT JOIN user_profiles up ON u.id = up.user_id 
            WHERE u.id = :user_id
        """)
        user_data = db.execute(user_query, {"user_id": user_id}).fetchone()
        
        # Tests de personnalité HEXACO
        hexaco_query = text("""
            SELECT * FROM hexaco_results 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC LIMIT 1
        """)
        hexaco_data = db.execute(hexaco_query, {"user_id": user_id}).fetchone()
        
        # Tests Holland/RIASEC
        holland_query = text("""
            SELECT * FROM holland_results 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC LIMIT 1
        """)
        holland_data = db.execute(holland_query, {"user_id": user_id}).fetchone()
        
        # Historique d'interactions
        interactions_query = text("""
            SELECT action_type, metadata, created_at 
            FROM user_interactions 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC LIMIT 50
        """)
        interactions = db.execute(interactions_query, {"user_id": user_id}).fetchall()
        
        return {
            "basic_profile": dict(user_data) if user_data else {},
            "hexaco_traits": dict(hexaco_data) if hexaco_data else {},
            "holland_codes": dict(holland_data) if holland_data else {},
            "recent_interactions": [dict(i) for i in interactions]
        }
    
    def _build_skill_extraction_prompt(self, user_profile: Dict[str, Any]) -> str:
        """Construit le prompt pour l'extraction LLM"""
        
        return f"""
        Tu es un expert en analyse de profils professionnels et en extraction de compétences.
        
        MISSION: Extraire les 5 compétences principales les plus pertinentes pour ce profil utilisateur.
        
        PROFIL UTILISATEUR COMPLET:
        
        INFORMATIONS DE BASE:
        - Âge: {user_profile['basic_profile'].get('age', 'Non spécifié')}
        - Niveau d'éducation: {user_profile['basic_profile'].get('education_level', 'Non spécifié')}
        - Industrie: {user_profile['basic_profile'].get('industry', 'Non spécifié')}
        - Années d'expérience: {user_profile['basic_profile'].get('years_experience', 0)}
        - Objectifs de carrière: {user_profile['basic_profile'].get('career_goals', 'Non spécifié')}
        
        TRAITS HEXACO (Big Five + Honnêteté):
        - Honnêteté-Humilité: {user_profile['hexaco_traits'].get('honesty_humility', 'N/A')}
        - Émotionalité: {user_profile['hexaco_traits'].get('emotionality', 'N/A')}
        - Extraversion: {user_profile['hexaco_traits'].get('extraversion', 'N/A')}
        - Agréabilité: {user_profile['hexaco_traits'].get('agreeableness', 'N/A')}
        - Conscienciosité: {user_profile['hexaco_traits'].get('conscientiousness', 'N/A')}
        - Ouverture: {user_profile['hexaco_traits'].get('openness', 'N/A')}
        
        CODES HOLLAND/RIASEC:
        - Réaliste: {user_profile['holland_codes'].get('realistic', 'N/A')}
        - Investigateur: {user_profile['holland_codes'].get('investigative', 'N/A')}
        - Artistique: {user_profile['holland_codes'].get('artistic', 'N/A')}
        - Social: {user_profile['holland_codes'].get('social', 'N/A')}
        - Entreprenant: {user_profile['holland_codes'].get('enterprising', 'N/A')}
        - Conventionnel: {user_profile['holland_codes'].get('conventional', 'N/A')}
        
        INTERACTIONS RÉCENTES:
        {self._format_interactions(user_profile['recent_interactions'])}
        
        CRITÈRES D'EXTRACTION:
        1. Les compétences doivent être CONCRÈTES et MESURABLES
        2. Elles doivent refléter les FORCES naturelles du profil HEXACO/Holland
        3. Elles doivent être PERTINENTES pour les objectifs de carrière
        4. Elles doivent avoir un POTENTIEL DE DÉVELOPPEMENT élevé
        5. Elles doivent être ALIGNÉES avec l'expérience existante
        
        IMPORTANT: Réponds UNIQUEMENT en JSON avec cette structure exacte:
        {{
            "extracted_skills": [
                {{
                    "skill_name": "Nom de la compétence",
                    "description": "Description détaillée",
                    "relevance_score": 0.95,
                    "development_potential": 0.88,
                    "alignment_reasoning": "Pourquoi cette compétence est pertinente",
                    "hexaco_connection": "Lien avec les traits HEXACO",
                    "holland_connection": "Lien avec les codes Holland"
                }}
            ]
        }}
        """
```

#### Service d'Alignement ESCO
```python
# backend/app/services/esco_alignment_service.py
class ESCOAlignmentService:
    """
    Service pour aligner les compétences extraites avec la taxonomie ESCO
    """
    
    def __init__(self):
        self.pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pinecone_client.Index("esco-368")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def align_skills_with_esco(self, extracted_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aligne les compétences extraites avec la taxonomie ESCO
        """
        aligned_skills = []
        
        for skill in extracted_skills:
            # 1. Recherche sémantique dans ESCO
            esco_matches = self._semantic_search_esco(skill['skill_name'], skill['description'])
            
            # 2. Sélection du meilleur match
            best_match = self._select_best_esco_match(skill, esco_matches)
            
            # 3. Enrichissement avec métadonnées ESCO
            enriched_skill = self._enrich_with_esco_metadata(skill, best_match)
            
            aligned_skills.append(enriched_skill)
        
        return aligned_skills
    
    def _semantic_search_esco(self, skill_name: str, description: str) -> List[Dict]:
        """Recherche sémantique dans l'index ESCO"""
        
        # Créer l'embedding de recherche
        search_text = f"{skill_name} {description}"
        search_embedding = self.embedding_model.encode(search_text).tolist()
        
        # Recherche dans Pinecone
        results = self.index.query(
            vector=search_embedding,
            top_k=10,
            filter={"type": {"$eq": "skill"}},
            include_metadata=True
        )
        
        return [
            {
                "esco_id": match.id,
                "esco_label": match.metadata.get("preferredLabel", ""),
                "esco_description": match.metadata.get("description", ""),
                "similarity_score": 1 - match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
```

### 2. Intégration Page d'Accueil

#### Composant Aperçu des Compétences
```typescript
// frontend/src/components/home/SkillsPreview.tsx
interface SkillsPreviewProps {
  userId: number;
  onViewFullTree: () => void;
}

export const SkillsPreview: React.FC<SkillsPreviewProps> = ({ 
  userId, 
  onViewFullTree 
}) => {
  const [skills, setSkills] = useState<ExtractedSkill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadUserSkills = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/v1/interactive-skills/user/${userId}/top-skills`);
        if (!response.ok) throw new Error('Erreur lors du chargement');
        
        const data = await response.json();
        setSkills(data.skills);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur inconnue');
      } finally {
        setLoading(false);
      }
    };

    loadUserSkills();
  }, [userId]);

  if (loading) {
    return (
      <div className="skills-preview-loading">
        <div className="loading-spinner" />
        <p>Analyse de votre profil en cours...</p>
      </div>
    );
  }

  return (
    <motion.div 
      className="skills-preview-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="preview-header">
        <h2>Vos Compétences Principales</h2>
        <p>Découvertes automatiquement à partir de votre profil</p>
      </div>

      <div className="skills-grid">
        {skills.map((skill, index) => (
          <motion.div
            key={skill.esco_id}
            className="skill-preview-card"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1, duration: 0.4 }}
            whileHover={{ scale: 1.02, y: -2 }}
          >
            <div className="skill-content">
              <h3>{skill.skill_name}</h3>
              <p className="skill-description">{skill.description}</p>
              
              <div className="skill-metrics">
                <div className="metric">
                  <span className="metric-label">Pertinence</span>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill"
                      style={{ width: `${skill.relevance_score * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="preview-actions">
        <motion.button
          className="explore-tree-button"
          onClick={onViewFullTree}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Explorer l'Arbre Interactif
        </motion.button>
      </div>
    </motion.div>
  );
};
```

### 3. Intégration Système XP Existant

#### Extension du Service XP
```python
# backend/app/services/skills_xp_service.py
class SkillsXPService:
    """
    Service pour gérer l'XP spécifique aux compétences
    """
    
    def award_skill_challenge_xp(self, db: Session, user_id: int, 
                                skill_id: str, challenge_id: str, 
                                base_xp: int) -> Dict[str, Any]:
        """
        Attribue l'XP pour un défi de compétence complété
        """
        
        # 1. Calculer l'XP avec bonus
        final_xp = self._calculate_xp_with_bonuses(
            db, user_id, skill_id, base_xp
        )
        
        # 2. Mettre à jour la progression générale
        self._update_general_progress(db, user_id, final_xp)
        
        # 3. Enregistrer l'XP spécifique aux compétences
        self._record_skill_xp(db, user_id, skill_id, final_xp, challenge_id)
        
        # 4. Vérifier les achievements
        achievements = self._check_skill_achievements(db, user_id, skill_id)
        
        return {
            "xp_awarded": final_xp,
            "total_xp": self._get_user_total_xp(db, user_id),
            "skill_xp": self._get_skill_total_xp(db, user_id, skill_id),
            "achievements": achievements,
            "level_up": self._check_level_up(db, user_id)
        }
    
    def _calculate_xp_with_bonuses(self, db: Session, user_id: int, 
                                  skill_id: str, base_xp: int) -> int:
        """Calcule l'XP avec les bonus applicables"""
        
        multiplier = 1.0
        
        # Bonus streak (défis complétés consécutivement)
        streak = self._get_user_streak(db, user_id)
        if streak >= 7:
            multiplier += 0.5  # +50% pour 7 jours consécutifs
        elif streak >= 3:
            multiplier += 0.25  # +25% pour 3 jours consécutifs
        
        # Bonus première fois
        if self._is_first_skill_completion(db, user_id, skill_id):
            multiplier += 0.3  # +30% pour première compétence
        
        return int(base_xp * multiplier)
```

### 4. Nouveaux Endpoints API

#### Router pour l'Extraction de Compétences
```python
# backend/app/routers/skill_extraction.py
@router.post("/extract-user-skills", response_model=ExtractedSkillsResponse)
async def extract_user_skills(
    user_id: int = Query(..., description="ID de l'utilisateur"),
    force_refresh: bool = Query(False, description="Forcer une nouvelle extraction"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Extrait les 5 compétences principales d'un utilisateur
    """
    try:
        # Vérifier les permissions
        if current_user.id != user_id and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé"
            )
        
        # Vérifier le cache si pas de refresh forcé
        if not force_refresh:
            cached_skills = skill_cache.get(f"user_skills_{user_id}")
            if cached_skills:
                return ExtractedSkillsResponse(
                    skills=cached_skills,
                    extraction_date=datetime.now(),
                    cache_hit=True
                )
        
        # Extraction via LLM
        extractor_service = LLMSkillExtractorService()
        extracted_skills = extractor_service.extract_top_skills_from_profile(db, user_id)
        
        # Cache des résultats (24h)
        skill_cache.set(f"user_skills_{user_id}", extracted_skills, ttl=86400)
        
        return ExtractedSkillsResponse(
            skills=extracted_skills,
            extraction_date=datetime.now(),
            cache_hit=False
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des compétences pour l'utilisateur {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'extraction des compétences: {str(e)}"
        )

@router.get("/user/{user_id}/top-skills", response_model=TopSkillsResponse)
async def get_user_top_skills(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Récupère les compétences principales pour l'aperçu page d'accueil
    """
    try:
        # Récupérer depuis le cache ou la base
        cached_skills = skill_cache.get(f"user_skills_{user_id}")
        
        if not cached_skills:
            # Déclencher l'extraction si pas en cache
            extractor_service = LLMSkillExtractorService()
            cached_skills = extractor_service.extract_top_skills_from_profile(db, user_id)
            skill_cache.set(f"user_skills_{user_id}", cached_skills, ttl=86400)
        
        return TopSkillsResponse(
            skills=cached_skills,
            user_id=user_id,
            last_updated=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des compétences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des compétences"
        )
```

### 5. Schémas de Base de Données Étendus

#### Nouvelles Tables pour l'Extraction de Compétences
```sql
-- Table pour stocker les extractions de compétences
CREATE TABLE user_skill_extractions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    extraction_method VARCHAR(50) DEFAULT 'llm_auto',
    extracted_skills JSONB NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    extraction_metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table pour l'historique des compétences extraites
CREATE TABLE skill_extraction_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    skill_esco_id VARCHAR(255) NOT NULL,
    skill_name VARCHAR(500) NOT NULL,
    relevance_score FLOAT NOT NULL,
    development_potential FLOAT NOT NULL,
    extraction_reasoning TEXT,
    source_data JSONB,
    extracted_at TIMESTAMP DEFAULT NOW()
);

-- Table pour l'XP des compétences
CREATE TABLE user_skills_xp (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    skill_esco_id VARCHAR(255) NOT NULL,
    skill_name VARCHAR(500) NOT NULL,
    total_xp INTEGER DEFAULT 0,
    challenges_completed INTEGER DEFAULT 0,
    first_completion_at TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, skill_esco_id)
);

-- Index pour les performances
CREATE INDEX idx_user_skill_extractions_user_id ON user_skill_extractions(user_id);
CREATE INDEX idx_skill_extraction_history_user_skill ON skill_extraction_history(user_id, skill_esco_id);
CREATE INDEX idx_user_skills_xp_user_id ON user_skills_xp(user_id);
CREATE INDEX idx_user_skills_xp_skill_id ON user_skills_xp(skill_esco_id);
```

### 6. Configuration et Optimisations

#### Configuration Redis pour Cache
```python
# backend/app/core/cache_config.py
class SkillsCacheConfig:
    """Configuration du cache pour les compétences"""
    
    # TTL par type de données
    USER_SKILLS_TTL = 86400  # 24h pour les compétences extraites
    ESCO_ALIGNMENT_TTL = 604800  # 7 jours pour l'alignement ESCO
    LLM_RESPONSES_TTL = 3600  # 1h pour les réponses LLM
    
    # Clés de cache
    USER_SKILLS_KEY = "user_skills_{user_id}"
    ESCO_ALIGNMENT_KEY = "esco_align_{skill_hash}"
    LLM_EXTRACTION_KEY = "llm_extract_{profile_hash}"
    
    @staticmethod
    def get_cache_key(key_type: str, **kwargs) -> str:
        """Génère une clé de cache formatée"""
        if key_type == "user_skills":
            return SkillsCacheConfig.USER_SKILLS_KEY.format(**kwargs)
        elif key_type == "esco_alignment":
            return SkillsCacheConfig.ESCO_ALIGNMENT_KEY.format(**kwargs)
        elif key_type == "llm_extraction":
            return SkillsCacheConfig.LLM_EXTRACTION_KEY.format(**kwargs)
        else:
            raise ValueError(f"Type de clé de cache inconnu: {key_type}")
```

#### Monitoring et Métriques
```python
# backend/app/monitoring/skills_metrics.py
class SkillsMetricsCollector:
    """Collecteur de métriques pour le système de compétences"""
    
    def __init__(self):
        self.redis_client = Redis()
        
    def track_skill_extraction(self, user_id: int, extraction_time: float, 
                              skills_count: int, method: str):
        """Enregistre les métriques d'extraction"""
        
        metrics = {
            "user_id": user_id,
            "extraction_time_ms": extraction_time * 1000,
            "skills_extracted": skills_count,
            "extraction_method": method,
            "timestamp": datetime.now().isoformat()
        }
        
        # Stocker dans Redis pour analyse
        self.redis_client.lpush("skills_extraction_metrics", json.dumps(metrics))
        self.redis_client.ltrim("skills_extraction_metrics", 0, 10000)  # Garder 10k entrées
        
    def track_esco_alignment(self, skill_name: str, alignment_time: float, 
                           similarity_score: float, success: bool):
        """Enregistre les métriques d'alignement ESCO"""
        
        metrics = {
            "skill_name": skill_name,
            "alignment_time_ms": alignment_time * 1000,
            "similarity_score": similarity_score,
            "alignment_success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.redis_client.lpush("esco_alignment_metrics", json.dumps(metrics))
        self.redis_client.ltrim("esco_alignment_metrics", 0, 10000)
        
    def get_extraction_stats(self, days: int = 7) -> Dict[str, Any]:
        """Récupère les statistiques d'extraction"""
        
        # Récupérer les métriques récentes
        raw_metrics = self.redis_client.lrange("skills_extraction_metrics", 0, -1)
        
        # Filtrer par période
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_metrics = []
        
        for raw_metric in raw_metrics:
            metric = json.loads(raw_metric)
            metric_date = datetime.fromisoformat(metric["timestamp"])
            
            if metric_date >= cutoff_date:
                recent_metrics.append(metric)
        
        if not recent_metrics:
            return {"error": "Aucune métrique disponible"}
        
        # Calculer les statistiques
        extraction_times = [m["extraction_time_ms"] for m in recent_metrics]
        skills_counts = [m["skills_extracted"] for m in recent_metrics]
        
        return {
            "total_extractions": len(recent_metrics),
            "avg_extraction_time_ms": sum(extraction_times) / len(extraction_times),
            "max_extraction_time_ms": max(extraction_times),
            "min_extraction_time_ms": min(extraction_times),
            "avg_skills_per_extraction": sum(skills_counts) / len(skills_counts),
            "success_rate": len([m for m in recent_metrics if m["skills_extracted"] > 0]) / len(recent_metrics),
            "period_days": days
        }
```

Cette architecture garantit une expérience d'apprentissage **personnalisée**, **engageante** et **évolutive** qui transforme l'exploration des compétences ESCO en un parcours gamifié et découverte progressive, avec une intégration complète dans l'écosystème existant d'Orientor.