# Guide d'Ingénierie de Prompts pour le Développement de Fonctionnalités Navigo

## Introduction

Ce guide fournit des templates et des stratégies pour créer des prompts détaillés et efficaces destinés à l'IA qui implémentera de nouvelles fonctionnalités dans la plateforme Navigo. L'objectif est de maximiser la précision et la cohérence des implémentations en fournissant un contexte riche et des instructions structurées.

## Anatomie d'un Prompt Efficace pour Navigo

### Structure Recommandée

```markdown
# [TITRE DE LA FONCTIONNALITÉ]

## CONTEXTE PLATEFORME
[Contexte spécifique à Navigo]

## ARCHITECTURE VECTORIELLE
[Spécifications des embeddings et intégrations]

## SPÉCIFICATIONS TECHNIQUES
[Détails techniques précis]

## INTÉGRATIONS REQUISES
[Services et APIs à utiliser]

## ASPECTS LONGITUDINAUX
[Considérations temporelles et évolutives]

## CRITÈRES DE VALIDATION
[Tests et métriques de succès]

## CONTRAINTES ET LIMITATIONS
[Restrictions techniques et business]
```

## Templates de Prompts par Type de Fonctionnalité

### 1. Template: Nouvelle Fonctionnalité de Recommandation

```markdown
# IMPLÉMENTATION: [NOM_FONCTIONNALITÉ] - Système de Recommandations Vectorielles

## CONTEXTE PLATEFORME NAVIGO

Tu développes pour Navigo, une plateforme d'orientation de carrière basée sur l'IA qui utilise des représentations vectorielles pour analyser les profils utilisateurs. La plateforme se concentre sur:

- **Représentation vectorielle au cœur**: Tous les profils utilisateurs sont représentés par des embeddings multidimensionnels
- **Approche longitudinale**: Suivi de l'évolution des utilisateurs dans le temps
- **Écosystème vectoriel mature**: Intégration avec Pinecone, multiple types d'embeddings

### Architecture Existante
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL avec pgvector
- **Frontend**: Next.js 13 avec App Router + TailwindCSS
- **Vectoriel**: Pinecone + Sentence Transformers + embeddings personnalisés
- **Déploiement**: Railway (backend) + Vercel (frontend)

## ARCHITECTURE VECTORIELLE REQUISE

### Types d'Embeddings Disponibles
```python
EMBEDDING_TYPES = {
    "standard": {
        "dimension": 1024,
        "model": "sentence-transformers/all-mpnet-base-v2",
        "usage": "Représentation générale du profil",
        "column": "embedding"
    },
    "oasis": {
        "dimension": 384,
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "usage": "Profil psychologique OaSIS",
        "column": "oasis_embedding"
    },
    "esco_full": {
        "dimension": 384,
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "usage": "Profil ESCO complet",
        "column": "esco_embedding"
    },
    "esco_occupation": {
        "dimension": 384,
        "usage": "Focus métiers ESCO",
        "column": "esco_embedding_occupation"
    },
    "esco_skill": {
        "dimension": 384,
        "usage": "Focus compétences ESCO",
        "column": "esco_embedding_skill"
    },
    "esco_skillgroup": {
        "dimension": 384,
        "usage": "Focus groupes de compétences ESCO",
        "column": "esco_embedding_skillsgroup"
    }
}
```

### Choix d'Embedding pour cette Fonctionnalité
**UTILISER**: [SPÉCIFIER LE TYPE] car [JUSTIFICATION]

### Intégration Pinecone
```python
PINECONE_CONFIG = {
    "index_name": "[NOM_INDEX]",
    "dimension": [DIMENSION],
    "metric": "cosine",
    "namespace": "[NAMESPACE_SI_REQUIS]"
}
```

## SPÉCIFICATIONS TECHNIQUES DÉTAILLÉES

### 1. Modèle de Données SQLAlchemy
```python
# Créer ce modèle dans backend/app/models/[nom_fonctionnalité].py
class [NomModèle](Base):
    __tablename__ = "[nom_table]"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Champs spécifiques à la fonctionnalité
    [SPÉCIFIER_CHAMPS]
    
    # Champs vectoriels si nécessaire
    embedding = Column(ARRAY(Float), nullable=True)
    
    # Champs temporels OBLIGATOIRES
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="[relation_name]")
```

### 2. Service Backend
```python
# Créer dans backend/app/services/[nom_fonctionnalité]_service.py
class [NomFonctionnalité]Service:
    def __init__(self):
        # Initialiser Pinecone si nécessaire
        # Référencer les services existants
        
    def get_user_embedding(self, db: Session, user_id: int) -> Optional[np.ndarray]:
        """
        OBLIGATOIRE: Utiliser les services existants
        from app.services.Oasisembedding_service import get_user_embedding, parse_embedding
        """
        
    def generate_recommendations(self, db: Session, user_id: int, limit: int = 10) -> List[Dict]:
        """
        PATTERN OBLIGATOIRE:
        1. Récupérer embedding utilisateur
        2. Requête Pinecone avec gestion d'erreurs
        3. Post-traitement et diversification
        4. Logging détaillé
        """
        
    def update_user_profile(self, db: Session, user_id: int, data: Dict) -> bool:
        """
        PATTERN OBLIGATOIRE:
        1. Validation des données
        2. Mise à jour base de données
        3. Régénération embedding si nécessaire
        4. Mise à jour Pinecone
        5. Logging des changements
        """
```

### 3. Router API FastAPI
```python
# Créer dans backend/app/routers/[nom_fonctionnalité].py
router = APIRouter(prefix="/api/v1/[nom-fonctionnalité]", tags=["[nom-fonctionnalité]"])

@router.get("/recommendations")
async def get_recommendations(
    embedding_type: str = Query("[TYPE_PAR_DÉFAUT]", description="Type d'embedding"),
    limit: int = Query(10, description="Nombre de recommandations"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    PATTERN OBLIGATOIRE:
    1. Validation des paramètres
    2. Gestion d'erreurs avec HTTPException
    3. Logging détaillé
    4. Retour structuré avec métadonnées
    """
```

### 4. Service Frontend TypeScript
```typescript
// Créer dans frontend/src/services/[nomFonctionnalité]Service.ts
interface [NomFonctionnalité]Recommendation {
    id: string;
    title: string;
    description: string;
    score: number;
    metadata: Record<string, any>;
    // Champs spécifiques
}

class [NomFonctionnalité]Service {
    async getRecommendations(
        embeddingType: string = '[TYPE_PAR_DÉFAUT]',
        limit: number = 10
    ): Promise<[NomFonctionnalité]Recommendation[]> {
        // PATTERN OBLIGATOIRE: Gestion d'erreurs complète
    }
    
    async updateProfile(data: [NomFonctionnalité]ProfileData): Promise<boolean> {
        // PATTERN OBLIGATOIRE: Validation côté client
    }
}
```

### 5. Composant React
```tsx
// Créer dans frontend/src/components/[nomFonctionnalité]/[NomComposant].tsx
interface [NomComposant]Props {
    userId?: number;
    embeddingType?: string;
    // Props spécifiques
}

export const [NomComposant]: React.FC<[NomComposant]Props> = ({
    embeddingType = '[TYPE_PAR_DÉFAUT]',
    ...props
}) => {
    // PATTERN OBLIGATOIRE:
    // 1. États pour loading, error, data
    // 2. useEffect pour chargement initial
    // 3. Gestion d'erreurs avec fallbacks
    // 4. Optimistic updates si applicable
    // 5. Accessibilité (ARIA labels)
    
    return (
        <div className="[classes-tailwind]">
            {/* Interface utilisateur */}
        </div>
    );
};
```

## INTÉGRATIONS OBLIGATOIRES

### Services Existants à Utiliser
```python
# OBLIGATOIRE: Importer et utiliser ces services
from app.services.Oasisembedding_service import (
    generate_embedding_from_text_384,
    store_embedding,
    parse_embedding,
    get_user_embedding,
    get_user_oasis_embedding
)

from app.services.Swipe_career_recommendation_service import (
    get_user_embedding,
    get_pinecone_career_recommendations
)

# Patterns d'utilisation OBLIGATOIRES
def example_usage(db: Session, user_id: int):
    # Pour récupérer un embedding
    embedding = get_user_embedding(db, user_id)
    
    # Pour générer un nouvel embedding
    new_embedding = generate_embedding_from_text_384(formatted_text)
    
    # Pour stocker un embedding
    success = store_embedding(db, user_id, embedding, "column_name")
```

### Base de Données - Patterns Obligatoires
```python
# Migration Alembic OBLIGATOIRE
def upgrade() -> None:
    # 1. Créer table avec champs temporels
    # 2. Créer index sur user_id
    # 3. Créer foreign key vers users
    # 4. Ajouter colonne embedding si nécessaire
    
def downgrade() -> None:
    # Rollback complet
```

### Logging Obligatoire
```python
from app.utils.logging_config import setup_logging
logger = setup_logging()

# PATTERNS OBLIGATOIRES
logger.info(f"[{service_name}] Starting operation for user {user_id}")
logger.error(f"[{service_name}] Error: {str(e)}")
logger.info(f"[{service_name}] Operation completed successfully")
```

## ASPECTS LONGITUDINAUX OBLIGATOIRES

### Suivi Temporel
```python
# OBLIGATOIRE: Chaque fonctionnalité doit prévoir
class TemporalTracking:
    def track_user_evolution(self, db: Session, user_id: int):
        """Suivre l'évolution temporelle"""
        
    def analyze_progression(self, db: Session, user_id: int, time_window: int):
        """Analyser la progression"""
        
    def predict_future_interests(self, db: Session, user_id: int):
        """Prédire les intérêts futurs"""
```

### Versioning des Données
```python
# PATTERN OBLIGATOIRE pour les données critiques
class DataVersioning:
    def create_snapshot(self, db: Session, user_id: int, data: Dict):
        """Créer un snapshot des données"""
        
    def get_historical_data(self, db: Session, user_id: int, timestamp: datetime):
        """Récupérer données historiques"""
```

## CRITÈRES DE VALIDATION OBLIGATOIRES

### Tests Backend
```python
# OBLIGATOIRE: Tests unitaires
def test_get_user_embedding():
    # Test récupération embedding
    
def test_generate_recommendations():
    # Test génération recommandations
    
def test_update_profile():
    # Test mise à jour profil

# OBLIGATOIRE: Tests d'intégration
def test_api_endpoints():
    # Test tous les endpoints
    
def test_database_operations():
    # Test opérations base de données
```

### Tests Frontend
```typescript
// OBLIGATOIRE: Tests composants
describe('[NomComposant]', () => {
    test('renders correctly', () => {});
    test('handles loading state', () => {});
    test('handles error state', () => {});
    test('handles user interactions', () => {});
});
```

### Métriques de Performance
```python
# OBLIGATOIRE: Monitoring des performances
@monitor_performance
def critical_function():
    # Fonctions critiques doivent être monitorées
    
# OBLIGATOIRE: Métriques vectorielles
def validate_embedding_quality(embedding: np.ndarray):
    # Validation dimension, normalisation, etc.
```

## CONTRAINTES TECHNIQUES OBLIGATOIRES

### Sécurité
- OBLIGATOIRE: Authentification sur tous les endpoints
- OBLIGATOIRE: Validation des entrées utilisateur
- OBLIGATOIRE: Sanitisation des données
- OBLIGATOIRE: Rate limiting sur les endpoints coûteux

### Performance
- OBLIGATOIRE: Pagination pour les listes > 50 éléments
- OBLIGATOIRE: Cache pour les requêtes fréquentes
- OBLIGATOIRE: Timeout sur les requêtes Pinecone
- OBLIGATOIRE: Optimisation des requêtes SQL

### Compatibilité
- OBLIGATOIRE: Support des types d'embeddings existants
- OBLIGATOIRE: Backward compatibility avec l'API existante
- OBLIGATOIRE: Migration de données sans interruption
- OBLIGATOIRE: Fallbacks pour les services externes

## LIVRABLES ATTENDUS

### Backend
1. [ ] Modèle SQLAlchemy avec migration Alembic
2. [ ] Service avec intégration vectorielle
3. [ ] Router API FastAPI complet
4. [ ] Tests unitaires et d'intégration
5. [ ] Documentation API

### Frontend
1. [ ] Service TypeScript avec types
2. [ ] Composants React réutilisables
3. [ ] Page Next.js avec routing
4. [ ] Tests composants
5. [ ] Documentation utilisateur

### Infrastructure
1. [ ] Configuration Pinecone si nécessaire
2. [ ] Scripts de déploiement
3. [ ] Monitoring et alertes
4. [ ] Documentation technique

## EXEMPLE COMPLET: Prompt pour Fonctionnalité de Recommandations de Mentors

# IMPLÉMENTATION: Système de Recommandations de Mentors Basé sur l'IA

## CONTEXTE PLATEFORME NAVIGO
[Contexte complet comme ci-dessus]

## ARCHITECTURE VECTORIELLE REQUISE
**UTILISER**: `oasis_embedding` (384D) car cette fonctionnalité se concentre sur la compatibilité psychologique entre mentors et mentees, nécessitant une compréhension des traits de personnalité.

**INDEX PINECONE**: `mentor-matching-384`

## SPÉCIFICATIONS TECHNIQUES DÉTAILLÉES

### Modèle de Données
```python
class MentorProfile(Base):
    __tablename__ = "mentor_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Champs spécifiques mentor
    expertise_areas = Column(ARRAY(String), nullable=False)
    years_experience = Column(Integer, nullable=False)
    availability_hours = Column(Integer, default=5)
    max_mentees = Column(Integer, default=3)
    
    # Embedding pour matching
    mentor_embedding = Column(ARRAY(Float), nullable=True)
    
    # Champs temporels
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="mentor_profile")
    mentoring_sessions = relationship("MentoringSession", back_populates="mentor")

class MentoringMatch(Base):
    __tablename__ = "mentoring_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Métriques de matching
    compatibility_score = Column(Float, nullable=False)
    psychological_alignment = Column(Float, nullable=False)
    expertise_match = Column(Float, nullable=False)
    
    # Statut et suivi
    status = Column(String, default="pending")  # pending, active, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    mentee = relationship("User", foreign_keys=[mentee_id])
    mentor = relationship("User", foreign_keys=[mentor_id])
```

### Service Backend
```python
class MentorMatchingService:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index("mentor-matching-384")
    
    def find_mentor_recommendations(self, db: Session, mentee_id: int, 
                                  limit: int = 5) -> List[Dict]:
        """
        Trouver des recommandations de mentors basées sur la compatibilité psychologique
        """
        try:
            # 1. Récupérer l'embedding OaSIS du mentee
            mentee_embedding = get_user_oasis_embedding(db, mentee_id)
            if mentee_embedding is None:
                logger.error(f"No OaSIS embedding found for mentee {mentee_id}")
                return []
            
            # 2. Requête Pinecone pour mentors similaires
            results = self.index.query(
                vector=mentee_embedding.tolist(),
                top_k=limit * 2,  # Plus de candidats pour filtrage
                filter={"user_type": "mentor", "available": True},
                include_metadata=True
            )
            
            # 3. Post-traitement et scoring avancé
            recommendations = []
            for match in results.matches:
                mentor_data = self._enrich_mentor_data(db, match)
                compatibility_score = self._calculate_compatibility(
                    mentee_embedding, match.values, mentor_data
                )
                
                recommendations.append({
                    "mentor_id": match.metadata["user_id"],
                    "compatibility_score": compatibility_score,
                    "psychological_alignment": match.score,
                    "mentor_data": mentor_data
                })
            
            # 4. Tri et limitation finale
            recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error finding mentor recommendations: {str(e)}")
            return []
    
    def _calculate_compatibility(self, mentee_embedding: np.ndarray, 
                               mentor_embedding: List[float], 
                               mentor_data: Dict) -> float:
        """
        Calculer un score de compatibilité avancé
        """
        # Similarité psychologique (40%)
        psych_similarity = cosine_similarity(
            mentee_embedding.reshape(1, -1),
            np.array(mentor_embedding).reshape(1, -1)
        )[0][0]
        
        # Complémentarité des compétences (35%)
        skill_complement = self._calculate_skill_complement(mentor_data)
        
        # Disponibilité et charge de travail (25%)
        availability_score = self._calculate_availability_score(mentor_data)
        
        return (psych_similarity * 0.4 + 
                skill_complement * 0.35 + 
                availability_score * 0.25)
```

### Router API
```python
@router.get("/mentor-recommendations")
async def get_mentor_recommendations(
    limit: int = Query(5, description="Nombre de mentors recommandés"),
    expertise_filter: Optional[str] = Query(None, description="Filtrer par expertise"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtenir des recommandations de mentors personnalisées
    """
    try:
        service = MentorMatchingService()
        recommendations = service.find_mentor_recommendations(
            db, current_user.id, limit
        )
        
        return {
            "recommendations": recommendations,
            "mentee_id": current_user.id,
            "total_found": len(recommendations),
            "algorithm_version": "v1.0"
        }
        
    except Exception as e:
        logger.error(f"Error in mentor recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request-mentoring")
async def request_mentoring(
    request: MentoringRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Demander un mentorat avec un mentor spécifique
    """
    # Implémentation de la demande de mentorat
```

## ASPECTS LONGITUDINAUX SPÉCIFIQUES

### Évolution de la Relation Mentor-Mentee
```python
class MentoringEvolutionService:
    def track_relationship_progress(self, db: Session, match_id: int):
        """Suivre l'évolution de la relation de mentorat"""
        
    def analyze_compatibility_over_time(self, db: Session, match_id: int):
        """Analyser l'évolution de la compatibilité"""
        
    def predict_relationship_success(self, db: Session, match_id: int):
        """Prédire le succès de la relation"""
```

## CRITÈRES DE VALIDATION SPÉCIFIQUES

### Métriques de Succès
- Taux d'acceptation des recommandations > 70%
- Score de satisfaction mentor-mentee > 4.0/5.0
- Durée moyenne des relations de mentorat > 3 mois
- Temps de réponse API < 500ms

### Tests Spécialisés
```python
def test_psychological_compatibility():
    """Tester la compatibilité psychologique"""
    
def test_mentor_availability_filtering():
    """Tester le filtrage par disponibilité"""
    
def test_recommendation_diversity():
    """Tester la diversité des recommandations"""
```

Ce template fournit un exemple complet de prompt structuré pour une fonctionnalité complexe intégrant tous les aspects de l'écosystème Navigo.
```

## Stratégies d'Optimisation des Prompts

### 1. Contextualisation Progressive
```markdown
# NIVEAU 1: Contexte Général
[Architecture globale de Navigo]

# NIVEAU 2: Contexte Technique
[Stack technique et patterns]

# NIVEAU 3: Contexte Fonctionnel
[Fonctionnalité spécifique]

# NIVEAU 4: Contexte d'Implémentation
[Détails techniques précis]
```

### 2. Spécification par Contraintes
```markdown
## CONTRAINTES OBLIGATOIRES
- DOIT utiliser les services existants
- DOIT respecter les patterns d'API
- DOIT inclure les aspects temporels
- DOIT implémenter le monitoring

## CONTRAINTES RECOMMANDÉES
- DEVRAIT optimiser les performances
- DEVRAIT inclure des tests complets
- DEVRAIT documenter les décisions

## CONTRAINTES OPTIONNELLES
- PEUT ajouter des fonctionnalités bonus
- PEUT optimiser l'UX
- PEUT inclure des métriques avancées
```

### 3. Validation par Exemples
```markdown
## EXEMPLES DE RÉUSSITE
[Code examples qui respectent les standards]

## EXEMPLES À ÉVITER
[Anti-patterns et erreurs communes]

## EXEMPLES DE TESTS
[Tests qui valident correctement]
```

## Prompts Spécialisés par Domaine

### Prompt pour Fonctionnalités d'Analyse Vectorielle
```markdown
# SPÉCIALISATION: Analyse Vectorielle Avancée

## CONTEXTE VECTORIEL SPÉCIALISÉ
Tu travailles sur une fonctionnalité qui nécessite une analyse vectorielle sophistiquée dans l'écosystème Navigo. Cette fonctionnalité doit:

### Manipulations Vectorielles Requises
- Calculs de similarité cosinus
- Clustering d'embeddings
- Réduction de dimensionnalité
- Analyse de drift temporel

### Intégrations Vectorielles Obligatoires
```python
# Services vectoriels à utiliser
from app.services.Oasisembedding_service import parse_embedding
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import numpy as np

# Patterns obligatoires
def analyze_embedding_evolution(embeddings_history: List[np.ndarray]):
    """Analyser l'évolution des embeddings"""
    
def cluster_similar_profiles(embeddings: List[np.ndarray], n_clusters: int):
    """Clustering des profils similaires"""
    
def detect_embedding_anomalies(embedding: np.ndarray, reference_embeddings: List[np.ndarray]):
    """Détecter les anomalies dans les embeddings"""
```

### Métriques Vectorielles Obligatoires
- Cohérence interne des clusters
- Stabilité temporelle des embeddings
- Qualité de la séparation des groupes
- Drift detection metrics
```

### Prompt pour Fonctionnalités d'Interface Utilisateur
```markdown
# SPÉCIALISATION: Interface Utilisateur Navigo

## CONTEXTE UX/UI SPÉCIALISÉ
Tu développes une interface utilisateur pour Navigo qui doit respecter:

### Design System Navigo
```css
/* Couleurs principales */
:root {
  --primary-color: #your-primary;
  --secondary-color: #your-secondary;
  --accent-color: #your-accent;
  --text-color: #your-text;
  --background-color: #your-background;
}

/* Patterns de composants */
.premium-card { /* Style des cartes */ }
.premium-button { /* Style des boutons */ }
.premium-input { /* Style des inputs */ }
```

### Composants Réutilisables Obligatoires
```tsx
// Utiliser ces composants existants
import MainLayout from '@/components/layout/MainLayout';
import NewSidebar from '@/components/layout/NewSidebar';
import UserCard from '@/components/ui/UserCard';
import PhilosophicalCard from '@/components/ui/PhilosophicalCard';

// Patterns d'état obligatoires
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<DataType[]>([]);
```

### Accessibilité Obligatoire
- ARIA labels sur tous les éléments interactifs
- Navigation au clavier
- Contraste suffisant
- Responsive design mobile-first
```

## Métriques de Qualité des Prompts

### Checklist de Validation
- [ ] Contexte Navigo complet fourni
- [ ] Architecture vectorielle spécifiée
- [ ] Services existants référencés
- [ ] Patterns obligatoires inclus
- [ ] Aspects temporels couverts
- [ ] Critères de validation définis
- [ ] Exemples concrets fournis
- [ ] Contraintes techniques listées

### Indicateurs de Succès
- **Précision**: L'IA comprend exactement ce qui est attendu
- **Cohérence**: L'implémentation respecte l'architecture existante
- **Complétude**: Tous les aspects sont couverts
- **Testabilité**: Les critères de validation sont clairs

## Conclusion

Ce guide fournit un framework complet pour créer des prompts efficaces qui maximisent la qualité des implémentations IA dans l'écosystème Navigo. En suivant ces templates et stratégies, vous obtiendrez des fonctionnalités qui s'intègrent parfaitement avec l'architecture vectorielle existante et respectent les standards de qualité de la plateforme.