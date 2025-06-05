# Documentation Technique HEXACO-PI-R

## Table des Matières
1. [Architecture Générale](#architecture)
2. [Structure des Données](#donnees)
3. [Services Backend](#backend)
4. [API Endpoints](#api)
5. [Frontend Components](#frontend)
6. [Base de Données](#database)
7. [Algorithmes de Scoring](#scoring)
8. [Gestion des Erreurs](#erreurs)
9. [Performance et Optimisation](#performance)
10. [Tests et Validation](#tests)

## Architecture Générale {#architecture}

### Vue d'Ensemble
Le système HEXACO-PI-R suit une architecture en couches avec séparation claire des responsabilités :

```
┌─────────────────────────────────────────┐
│                Frontend                 │
│  (Next.js + TypeScript + React)        │
├─────────────────────────────────────────┤
│                API Layer                │
│         (FastAPI + Python)             │
├─────────────────────────────────────────┤
│              Services Layer             │
│    (Business Logic + Scoring)          │
├─────────────────────────────────────────┤
│               Data Layer                │
│     (PostgreSQL + CSV Files)           │
└─────────────────────────────────────────┘
```

### Composants Principaux

#### Backend Services
- **HexacoService** : Gestion des données et métadonnées
- **HexacoScoringService** : Calculs des scores et percentiles
- **LLMHexacoService** : Intégration IA pour insights
- **Router** : Endpoints API REST

#### Frontend Components
- **TestInterface** : Interface de passation du test
- **HexacoChart** : Visualisation radar des résultats
- **ResultScreen** : Affichage des résultats détaillés
- **HexacoResultsView** : Vue profil utilisateur

## Structure des Données {#donnees}

### Fichiers CSV Source

#### Format des Questions
```csv
item_id,item_text,response_min,response_max,version,language,reverse_keyed,facet
1,"Question text",1,5,60,french,True,Aesthetic Appreciation
```

**Champs :**
- `item_id` : Identifiant unique de la question (int)
- `item_text` : Texte de la question (string)
- `response_min` : Score minimum (1)
- `response_max` : Score maximum (5)
- `version` : Version du test (60 ou 100)
- `language` : Langue (french/english)
- `reverse_keyed` : Question inversée (boolean)
- `facet` : Facette HEXACO associée (string)

#### Versions Disponibles
```json
{
  "hexaco_60_fr": {
    "csv_file": "French_60_FULL.csv",
    "item_count": 60,
    "language": "fr"
  },
  "hexaco_100_fr": {
    "csv_file": "French_100_FULL.csv", 
    "item_count": 100,
    "language": "fr"
  },
  "hexaco_60_en": {
    "csv_file": "English_60_FULL.csv",
    "item_count": 60,
    "language": "en"
  },
  "hexaco_100_en": {
    "csv_file": "English_100_FULL.csv",
    "item_count": 100,
    "language": "en"
  }
}
```

### Configuration HEXACO

#### Domaines et Facettes
```json
{
  "domains": {
    "Honesty-Humility": {
      "facets": ["Sincerity", "Fairness", "Greed-Avoidance", "Modesty"],
      "description": "Tendance à être sincère, équitable, modeste et non matérialiste"
    }
  }
}
```

## Services Backend {#backend}

### HexacoService

#### Responsabilités
- Chargement et cache des données CSV
- Gestion des métadonnées de versions
- Création et gestion des sessions d'évaluation
- Sauvegarde des réponses utilisateur

#### Méthodes Principales

```python
class HexacoService:
    def __init__(self):
        self.config_path = Path("config/hexaco_facet_mapping.json")
        self.data_path = Path("data_n_notebook/data")
        self._config_cache = None
        self._questions_cache = {}
    
    def get_available_versions(self) -> Dict[str, Any]:
        """Retourne les versions disponibles du test."""
        
    def get_questions_for_version(self, version_id: str) -> List[Dict[str, Any]]:
        """Retourne les questions pour une version spécifique."""
        
    def create_assessment_session(self, db: Session, user_id: int, version_id: str) -> str:
        """Crée une nouvelle session d'évaluation."""
        
    def save_response(self, db: Session, session_id: str, item_id: int, response_value: int) -> bool:
        """Sauvegarde une réponse individuelle."""
```

#### Cache et Performance
- **Cache des questions** : Les questions sont mises en cache en mémoire après le premier chargement
- **Cache de configuration** : La configuration JSON est chargée une seule fois
- **Lazy loading** : Les données ne sont chargées qu'à la demande

### HexacoScoringService

#### Algorithme de Scoring

```python
def calculate_scores(self, responses: Dict[int, int], version_id: str) -> Dict[str, Any]:
    """
    Calcule les scores HEXACO à partir des réponses.
    
    Étapes :
    1. Charger les questions et métadonnées
    2. Appliquer l'inversion pour les items reverse_keyed
    3. Calculer les scores par facette
    4. Calculer les scores par domaine
    5. Convertir en percentiles
    """
```

#### Logique d'Inversion
```python
def _apply_reverse_keying(self, response_value: int, is_reverse: bool) -> int:
    """
    Applique l'inversion pour les questions reverse_keyed.
    Échelle 1-5 : 1→5, 2→4, 3→3, 4→2, 5→1
    """
    if is_reverse:
        return 6 - response_value
    return response_value
```

#### Calcul des Percentiles
```python
def _calculate_percentiles(self, raw_scores: Dict[str, float]) -> Dict[str, int]:
    """
    Convertit les scores bruts en percentiles basés sur les normes de population.
    Utilise des tables de conversion pré-calculées.
    """
```

### LLMHexacoService

#### Génération d'Insights IA
```python
class LLMHexacoService:
    def generate_personality_insights(self, scores: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère des insights personnalisés basés sur les scores HEXACO.
        
        Retourne :
        - Analyse détaillée du profil
        - Recommandations de développement
        - Applications professionnelles
        - Conseils relationnels
        """
```

## API Endpoints {#api}

### Endpoints Principaux

#### GET /api/hexaco/versions
```json
{
  "hexaco_60_fr": {
    "title": "Test HEXACO-PI-R (Version courte - Français)",
    "item_count": 60,
    "estimated_duration": 15,
    "language": "fr",
    "active": true
  }
}
```

#### GET /api/hexaco/questions/{version_id}
```json
[
  {
    "item_id": 1,
    "item_text": "Visiter une galerie d'art m'ennuierait.",
    "response_min": 1,
    "response_max": 5,
    "reverse_keyed": true,
    "facet": "Aesthetic Appreciation"
  }
]
```

#### POST /api/hexaco/sessions
```json
{
  "user_id": 123,
  "version_id": "hexaco_60_fr"
}
```

**Réponse :**
```json
{
  "session_id": "uuid-string",
  "status": "created",
  "total_items": 60
}
```

#### POST /api/hexaco/responses
```json
{
  "session_id": "uuid-string",
  "item_id": 1,
  "response_value": 4,
  "response_time_ms": 3500
}
```

#### POST /api/hexaco/complete
```json
{
  "session_id": "uuid-string"
}
```

**Réponse :**
```json
{
  "scores": {
    "domain_scores": {
      "Honesty-Humility": 75,
      "Emotionality": 45,
      "Extraversion": 82,
      "Agreeableness": 60,
      "Conscientiousness": 88,
      "Openness": 70
    },
    "facet_scores": {
      "Sincerity": 78,
      "Fairness": 72
    }
  },
  "insights": {
    "summary": "Votre profil révèle...",
    "strengths": ["Leadership naturel", "Grande organisation"],
    "development_areas": ["Gestion du stress", "Flexibilité"]
  }
}
```

### Gestion des Erreurs API

#### Codes d'Erreur Standard
```python
class HexacoAPIError(Exception):
    """Erreurs spécifiques à l'API HEXACO."""
    
    VERSION_NOT_FOUND = ("HEXACO_001", "Version non trouvée")
    SESSION_NOT_FOUND = ("HEXACO_002", "Session non trouvée")
    INVALID_RESPONSE = ("HEXACO_003", "Réponse invalide")
    INCOMPLETE_TEST = ("HEXACO_004", "Test incomplet")
    SCORING_ERROR = ("HEXACO_005", "Erreur de calcul des scores")
```

## Frontend Components {#frontend}

### TestInterface Component

#### Props Interface
```typescript
interface TestInterfaceProps {
  version: HexacoVersion;
  onComplete: (sessionId: string) => void;
  onProgress: (progress: number) => void;
}
```

#### État Local
```typescript
interface TestState {
  currentQuestion: number;
  responses: Record<number, number>;
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
}
```

#### Méthodes Principales
```typescript
const handleResponse = async (itemId: number, value: number) => {
  // Sauvegarde immédiate de la réponse
  await hexacoTestService.saveResponse(sessionId, itemId, value);
  
  // Mise à jour de l'état local
  setResponses(prev => ({ ...prev, [itemId]: value }));
  
  // Navigation vers la question suivante
  if (currentQuestion < questions.length - 1) {
    setCurrentQuestion(prev => prev + 1);
  } else {
    await completeTest();
  }
};
```

### HexacoChart Component

#### Visualisation Radar
```typescript
interface HexacoChartProps {
  scores: DomainScores;
  size?: number;
  showLabels?: boolean;
  interactive?: boolean;
}

const HexacoChart: React.FC<HexacoChartProps> = ({ scores, size = 300 }) => {
  const data = useMemo(() => ({
    labels: ['H', 'E', 'X', 'A', 'C', 'O'],
    datasets: [{
      data: [
        scores['Honesty-Humility'],
        scores['Emotionality'],
        scores['Extraversion'],
        scores['Agreeableness'],
        scores['Conscientiousness'],
        scores['Openness']
      ],
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 2
    }]
  }), [scores]);
  
  return <Radar data={data} options={chartOptions} />;
};
```

### Service Layer Frontend

#### HexacoTestService
```typescript
class HexacoTestService {
  private baseUrl = '/api/hexaco';
  
  async getVersions(): Promise<HexacoVersion[]> {
    const response = await fetch(`${this.baseUrl}/versions`);
    return response.json();
  }
  
  async startTest(userId: number, versionId: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, version_id: versionId })
    });
    const data = await response.json();
    return data.session_id;
  }
  
  async saveResponse(sessionId: string, itemId: number, value: number): Promise<void> {
    await fetch(`${this.baseUrl}/responses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        item_id: itemId,
        response_value: value,
        response_time_ms: Date.now() - this.questionStartTime
      })
    });
  }
}
```

## Base de Données {#database}

### Schéma des Tables

#### personality_assessments
```sql
CREATE TABLE personality_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    assessment_type VARCHAR(50) NOT NULL, -- 'hexaco'
    assessment_version VARCHAR(50) NOT NULL, -- 'hexaco_60_fr'
    session_id UUID UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
    total_items INTEGER NOT NULL,
    completed_items INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### personality_responses
```sql
CREATE TABLE personality_responses (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES personality_assessments(id),
    item_id VARCHAR(10) NOT NULL,
    item_type VARCHAR(20) DEFAULT 'likert', -- 'likert', 'binary', 'text'
    response_value JSONB NOT NULL, -- {"value": 4}
    response_time_ms INTEGER,
    revision_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### personality_scores
```sql
CREATE TABLE personality_scores (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES personality_assessments(id),
    domain VARCHAR(50) NOT NULL,
    facet VARCHAR(50),
    raw_score DECIMAL(5,2),
    percentile_score INTEGER,
    score_type VARCHAR(20) DEFAULT 'standard', -- 'standard', 'sten', 'z_score'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Index et Performance
```sql
-- Index pour les requêtes fréquentes
CREATE INDEX idx_personality_assessments_user_id ON personality_assessments(user_id);
CREATE INDEX idx_personality_assessments_session_id ON personality_assessments(session_id);
CREATE INDEX idx_personality_responses_assessment_id ON personality_responses(assessment_id);
CREATE INDEX idx_personality_scores_assessment_id ON personality_scores(assessment_id);

-- Index composites
CREATE INDEX idx_assessments_user_type_status ON personality_assessments(user_id, assessment_type, status);
```

## Algorithmes de Scoring {#scoring}

### Calcul des Scores Bruts

#### Étape 1 : Inversion des Items
```python
def process_responses(self, responses: Dict[int, int], questions: List[Dict]) -> Dict[int, int]:
    """Applique l'inversion pour les questions reverse_keyed."""
    processed = {}
    
    for question in questions:
        item_id = question['item_id']
        if item_id in responses:
            raw_value = responses[item_id]
            if question['reverse_keyed']:
                # Inversion sur échelle 1-5
                processed[item_id] = 6 - raw_value
            else:
                processed[item_id] = raw_value
    
    return processed
```

#### Étape 2 : Calcul par Facette
```python
def calculate_facet_scores(self, processed_responses: Dict[int, int], questions: List[Dict]) -> Dict[str, float]:
    """Calcule les scores moyens par facette."""
    facet_responses = defaultdict(list)
    
    # Grouper les réponses par facette
    for question in questions:
        item_id = question['item_id']
        if item_id in processed_responses:
            facet = question['facet']
            facet_responses[facet].append(processed_responses[item_id])
    
    # Calculer les moyennes
    facet_scores = {}
    for facet, responses in facet_responses.items():
        facet_scores[facet] = sum(responses) / len(responses)
    
    return facet_scores
```

#### Étape 3 : Calcul par Domaine
```python
def calculate_domain_scores(self, facet_scores: Dict[str, float]) -> Dict[str, float]:
    """Calcule les scores moyens par domaine."""
    domain_config = self.hexaco_service.get_domains_config()
    domain_scores = {}
    
    for domain, config in domain_config.items():
        domain_facets = config['facets']
        domain_values = [facet_scores[facet] for facet in domain_facets if facet in facet_scores]
        
        if domain_values:
            domain_scores[domain] = sum(domain_values) / len(domain_values)
    
    return domain_scores
```

### Conversion en Percentiles

#### Tables de Normes
```python
# Normes basées sur des échantillons de population
HEXACO_NORMS = {
    'Honesty-Humility': {
        'mean': 3.2,
        'std': 0.6,
        'percentiles': {
            1.0: 1, 1.5: 5, 2.0: 10, 2.5: 25, 3.0: 40,
            3.5: 60, 4.0: 75, 4.5: 90, 5.0: 99
        }
    }
}
```

#### Algorithme de Conversion
```python
def convert_to_percentiles(self, raw_scores: Dict[str, float]) -> Dict[str, int]:
    """Convertit les scores bruts en percentiles."""
    percentiles = {}
    
    for domain, raw_score in raw_scores.items():
        if domain in HEXACO_NORMS:
            norms = HEXACO_NORMS[domain]
            percentile = self._interpolate_percentile(raw_score, norms['percentiles'])
            percentiles[domain] = max(1, min(99, percentile))
    
    return percentiles

def _interpolate_percentile(self, score: float, percentile_table: Dict[float, int]) -> int:
    """Interpolation linéaire pour les percentiles."""
    scores = sorted(percentile_table.keys())
    
    if score <= scores[0]:
        return percentile_table[scores[0]]
    if score >= scores[-1]:
        return percentile_table[scores[-1]]
    
    # Interpolation linéaire
    for i in range(len(scores) - 1):
        if scores[i] <= score <= scores[i + 1]:
            x1, x2 = scores[i], scores[i + 1]
            y1, y2 = percentile_table[x1], percentile_table[x2]
            return int(y1 + (y2 - y1) * (score - x1) / (x2 - x1))
```

## Gestion des Erreurs {#erreurs}

### Stratégie de Gestion d'Erreurs

#### Backend Error Handling
```python
class HexacoErrorHandler:
    @staticmethod
    def handle_service_error(func):
        """Décorateur pour la gestion d'erreurs des services."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"Fichier de données manquant: {e}")
                raise HexacoDataError("Données HEXACO non disponibles")
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de parsing JSON: {e}")
                raise HexacoConfigError("Configuration HEXACO invalide")
            except Exception as e:
                logger.error(f"Erreur inattendue: {e}")
                raise HexacoServiceError("Erreur interne du service")
        return wrapper
```

#### Frontend Error Handling
```typescript
class HexacoErrorHandler {
  static handleApiError(error: any): string {
    if (error.response?.status === 404) {
      return "Version du test non trouvée";
    } else if (error.response?.status === 400) {
      return "Données invalides";
    } else if (error.response?.status >= 500) {
      return "Erreur serveur, veuillez réessayer";
    } else {
      return "Une erreur inattendue s'est produite";
    }
  }
  
  static async withRetry<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3
  ): Promise<T> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
    throw new Error("Max retries exceeded");
  }
}
```

### Logging et Monitoring

#### Configuration des Logs
```python
import logging
import structlog

# Configuration structurée des logs
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("hexaco_service")
```

#### Métriques de Performance
```python
import time
from functools import wraps

def monitor_performance(func):
    """Décorateur pour monitorer les performances."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                "Function executed successfully",
                function=func.__name__,
                duration=duration,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Function execution failed",
                function=func.__name__,
                duration=duration,
                error=str(e)
            )
            raise
    return wrapper
```

## Performance et Optimisation {#performance}

### Optimisations Backend

#### Cache Redis (Optionnel)
```python
import redis
import json
from typing import Optional

class HexacoCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.cache_ttl = 3600  # 1 heure
    
    def get_questions(self, version_id: str) -> Optional[List[Dict]]:
        """Récupère les questions depuis le cache."""
        cache_key = f"hexaco:questions:{version_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def set_questions(self, version_id: str, questions: List[Dict]):
        """Met en cache les questions."""
        cache_key = f"hexaco:questions:{version_id}"
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(questions)
        )
```

#### Optimisation Base de Données
```python
# Requêtes optimisées avec SQLAlchemy
def get_user_assessments_optimized(db: Session, user_id: int) -> List[Dict]:
    """Requête optimisée pour récupérer les évaluations utilisateur."""
    query = text("""
        SELECT 
            pa.id,
            pa.assessment_version,
            pa.status,
            pa.completed_at,
            COUNT(pr.id) as response_count,
            AVG(ps.percentile_score) as avg_score
        FROM personality_assessments pa
        LEFT JOIN personality_responses pr ON pa.id = pr.assessment_id
        LEFT JOIN personality_scores ps ON pa.id = ps.assessment_id
        WHERE pa.user_id = :user_id 
        AND pa.assessment_type = 'hexaco'
        GROUP BY pa.id, pa.assessment_version, pa.status, pa.completed_at
        ORDER BY pa.completed_at DESC
    """)
    
    return db.execute(query, {"user_id": user_id}).fetchall()
```

### Optimisations Frontend

#### Lazy Loading des Composants
```typescript
import { lazy, Suspense } from 'react';

// Chargement paresseux des composants lourds
const HexacoChart = lazy(() => import('./HexacoChart'));
const ResultScreen = lazy(() => import('./ResultScreen'));

const TestInterface: React.FC = () => {
  return (
    <div>
      <Suspense fallback={<LoadingSpinner />}>
        {showResults && <ResultScreen scores={scores} />}
      </Suspense>
    </div>
  );
};
```

#### Optimisation des Re-renders
```typescript
import { memo, useMemo, useCallback } from 'react';

const QuestionCard = memo<QuestionCardProps>(({ question, onResponse }) => {
  const handleResponse = useCallback((value: number) => {
    onResponse(question.item_id, value);
  }, [question.item_id, onResponse]);
  
  const questionText = useMemo(() => 
    question.item_text.replace(/\n/g, '<br />'),
    [question.item_text]
  );
  
  return (
    <div className="question-card">
      <p dangerouslySetInnerHTML={{ __html: questionText }} />
      <ResponseScale onSelect={handleResponse} />
    </div>
  );
});
```

## Tests et Validation {#tests}

### Tests Unitaires Backend

#### Test du Service de Scoring
```python
import pytest
from app.services.hexaco_scoring_service import HexacoScoringService

class TestHexacoScoringService:
    def setup_method(self):
        self.scoring_service = HexacoScoringService()
    
    def test_reverse_keying(self):
        """Test de l'inversion des items."""
        # Item normal
        assert self.scoring_service._apply_reverse_keying(3, False) == 3
        
        # Item inversé
        assert self.scoring_service._apply_reverse_keying(1, True) == 5
        assert self.scoring_service._apply_reverse_keying(5, True) == 1
        assert self.scoring_service._apply_reverse_keying(3, True) == 3
    
    def test_facet_score_calculation(self):
        """Test du calcul des scores de facettes."""
        responses = {1: 4, 2: 5, 3: 3}  # 3 questions pour une facette
        questions = [
            {"item_id": 1, "facet": "Sincerity", "reverse_keyed": False},
            {"item_id": 2, "facet": "Sincerity", "reverse_keyed": False},
            {"item_id": 3, "facet": "Sincerity", "reverse_keyed": True}
        ]
        
        facet_scores = self.scoring_service.calculate_facet_scores(responses, questions)
        
        # Score attendu: (4 + 5 + (6-3)) / 3 = (4 + 5 + 3) / 3 = 4.0
        assert facet_scores["Sincerity"] == 4.0
    
    @pytest.mark.parametrize("responses,expected_domains", [
        ({i: 3 for i in range(1, 61)}, 6),  # Toutes neutres
        ({i: 5 for i in range(1, 61)}, 6),  # Toutes maximales
        ({i: 1 for i in range(1, 61)}, 6),  # Toutes minimales
    ])
    def test_complete_scoring(self, responses, expected_domains):
        """Test du scoring complet."""
        scores = self.scoring_service.calculate_scores(responses, "hexaco_60_fr")
        
        assert "domain_scores" in scores
        assert len(scores["domain_scores"]) == expected_domains
        assert "facet_scores" in scores
        
        # Vérifier que tous les scores sont dans la plage valide
        for domain, score in scores["domain_scores"].items():
            assert 1 <= score <= 99, f"Score invalide pour {domain}: {score}"
```

### Tests d'Intégration

#### Test du Workflow Complet
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestHexacoIntegration:
    def test_complete_workflow(self):
        """Test du workflow complet HEXACO."""
        
        # 1. Récupérer les versions disponibles
        response = client.get("/api/hexaco/versions")
        assert response.status_code == 200
        versions = response.json()
        assert "hexaco_60_fr" in versions
        
        # 2. Créer une session de test
        response = client.post("/api/hexaco/sessions", json={
            "user_id": 1,
            "version_id": "hexaco_60_fr"
        })
        assert response.status_code ==