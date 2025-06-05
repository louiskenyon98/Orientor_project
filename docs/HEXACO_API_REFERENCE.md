# Référence API HEXACO-PI-R

## Table des Matières
1. [Vue d'Ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Endpoints de Configuration](#configuration)
4. [Endpoints de Test](#test)
5. [Endpoints de Scoring](#scoring)
6. [Endpoints d'Analyse](#analyse)
7. [Gestion des Erreurs](#erreurs)
8. [Exemples d'Utilisation](#exemples)
9. [SDK et Clients](#sdk)

## Vue d'Ensemble {#vue-densemble}

### URL de Base
```
Production: https://api.orientor.com
Développement: http://localhost:8000
```

### Format des Réponses
Toutes les réponses API sont au format JSON avec la structure suivante :

```json
{
  "success": true,
  "data": { ... },
  "message": "Description optionnelle",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "uuid-string"
}
```

### Codes de Statut HTTP
- `200` - Succès
- `201` - Créé avec succès
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Non autorisé
- `404` - Ressource non trouvée
- `422` - Erreur de validation
- `429` - Trop de requêtes
- `500` - Erreur serveur interne

### Versioning
L'API utilise le versioning par header :
```
Accept: application/vnd.orientor.v1+json
```

## Authentification {#authentification}

### JWT Token
```http
Authorization: Bearer <jwt_token>
```

### Obtenir un Token
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 123,
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

## Endpoints de Configuration {#configuration}

### GET /api/hexaco/versions
Récupère la liste des versions disponibles du test HEXACO.

**Paramètres :** Aucun

**Réponse :**
```json
{
  "success": true,
  "data": {
    "hexaco_60_fr": {
      "title": "Test HEXACO-PI-R (Version courte - Français)",
      "description": "Évaluation complète de personnalité en 60 questions",
      "item_count": 60,
      "estimated_duration": 15,
      "language": "fr",
      "active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    "hexaco_100_fr": {
      "title": "Test HEXACO-PI-R (Version complète - Français)",
      "description": "Évaluation approfondie de personnalité en 100 questions",
      "item_count": 100,
      "estimated_duration": 25,
      "language": "fr",
      "active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

### GET /api/hexaco/languages
Récupère la liste des langues disponibles.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "fr": {
      "name": "Français",
      "flag": "🇫🇷",
      "description": "Version française du test HEXACO-PI-R",
      "versions": ["hexaco_60_fr", "hexaco_100_fr"]
    },
    "en": {
      "name": "English",
      "flag": "🇺🇸",
      "description": "English version of HEXACO-PI-R test",
      "versions": ["hexaco_60_en", "hexaco_100_en"]
    }
  }
}
```

### GET /api/hexaco/domains
Récupère la configuration des domaines et facettes HEXACO.

**Réponse :**
```json
{
  "success": true,
  "data": {
    "Honesty-Humility": {
      "code": "H",
      "facets": [
        {
          "name": "Sincerity",
          "code": "H1",
          "description": "Tendance à être authentique et honnête"
        },
        {
          "name": "Fairness",
          "code": "H2",
          "description": "Éviter de tromper ou manipuler autrui"
        },
        {
          "name": "Greed-Avoidance",
          "code": "H3",
          "description": "Ne pas être obsédé par la richesse"
        },
        {
          "name": "Modesty",
          "code": "H4",
          "description": "Ne pas se considérer comme supérieur aux autres"
        }
      ],
      "description": "Tendance à être sincère, équitable, modeste et non matérialiste",
      "color": "#FF6B6B"
    }
  }
}
```

### GET /api/hexaco/questions/{version_id}
Récupère les questions pour une version spécifique du test.

**Paramètres :**
- `version_id` (path) : Identifiant de la version (ex: "hexaco_60_fr")

**Paramètres de requête optionnels :**
- `shuffle` (boolean) : Mélanger l'ordre des questions (défaut: false)
- `include_metadata` (boolean) : Inclure les métadonnées (défaut: true)

**Réponse :**
```json
{
  "success": true,
  "data": {
    "version_info": {
      "version_id": "hexaco_60_fr",
      "title": "Test HEXACO-PI-R (Version courte - Français)",
      "item_count": 60,
      "language": "fr"
    },
    "questions": [
      {
        "item_id": 1,
        "item_text": "Visiter une galerie d'art m'ennuierait.",
        "response_min": 1,
        "response_max": 5,
        "response_labels": {
          "1": "Fortement en désaccord",
          "2": "En désaccord",
          "3": "Neutre",
          "4": "D'accord",
          "5": "Fortement d'accord"
        },
        "reverse_keyed": true,
        "facet": "Aesthetic Appreciation",
        "domain": "Openness",
        "order": 1
      }
    ]
  }
}
```

## Endpoints de Test {#test}

### POST /api/hexaco/sessions
Crée une nouvelle session d'évaluation HEXACO.

**Corps de la requête :**
```json
{
  "user_id": 123,
  "version_id": "hexaco_60_fr",
  "metadata": {
    "source": "web_app",
    "device": "desktop",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "assessment_id": 456,
    "status": "created",
    "version_id": "hexaco_60_fr",
    "total_items": 60,
    "completed_items": 0,
    "estimated_duration": 15,
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-15T12:30:00Z"
  }
}
```

### GET /api/hexaco/sessions/{session_id}
Récupère les informations d'une session d'évaluation.

**Paramètres :**
- `session_id` (path) : UUID de la session

**Réponse :**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "assessment_id": 456,
    "user_id": 123,
    "version_id": "hexaco_60_fr",
    "status": "in_progress",
    "total_items": 60,
    "completed_items": 25,
    "progress_percentage": 41.67,
    "current_question": 26,
    "estimated_time_remaining": 8,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:45:00Z",
    "expires_at": "2024-01-15T12:30:00Z"
  }
}
```

### POST /api/hexaco/responses
Sauvegarde une réponse à une question.

**Corps de la requête :**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "item_id": 1,
  "response_value": 4,
  "response_time_ms": 3500,
  "metadata": {
    "question_start_time": "2024-01-15T10:30:15Z",
    "question_end_time": "2024-01-15T10:30:18Z",
    "revision_count": 0
  }
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "response_id": 789,
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "item_id": 1,
    "response_value": 4,
    "response_time_ms": 3500,
    "saved_at": "2024-01-15T10:30:18Z",
    "progress": {
      "completed_items": 26,
      "total_items": 60,
      "progress_percentage": 43.33
    }
  }
}
```

### PUT /api/hexaco/responses/{response_id}
Met à jour une réponse existante.

**Paramètres :**
- `response_id` (path) : ID de la réponse

**Corps de la requête :**
```json
{
  "response_value": 3,
  "response_time_ms": 2800
}
```

### GET /api/hexaco/responses/{session_id}
Récupère toutes les réponses d'une session.

**Paramètres :**
- `session_id` (path) : UUID de la session

**Réponse :**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "responses": [
      {
        "response_id": 789,
        "item_id": 1,
        "response_value": 4,
        "response_time_ms": 3500,
        "revision_count": 0,
        "created_at": "2024-01-15T10:30:18Z",
        "updated_at": "2024-01-15T10:30:18Z"
      }
    ],
    "summary": {
      "total_responses": 60,
      "average_response_time": 4200,
      "total_test_time": 252000
    }
  }
}
```

### POST /api/hexaco/complete
Marque une évaluation comme complétée et déclenche le calcul des scores.

**Corps de la requête :**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "completion_metadata": {
    "completion_time": "2024-01-15T10:45:00Z",
    "user_feedback": "Test facile à comprendre",
    "technical_issues": false
  }
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "completed_at": "2024-01-15T10:45:00Z",
    "scores_calculated": true,
    "results_available": true,
    "results_url": "/api/hexaco/results/550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## Endpoints de Scoring {#scoring}

### GET /api/hexaco/results/{session_id}
Récupère les résultats complets d'une évaluation.

**Paramètres :**
- `session_id` (path) : UUID de la session

**Paramètres de requête optionnels :**
- `include_raw_scores` (boolean) : Inclure les scores bruts (défaut: false)
- `include_facet_details` (boolean) : Inclure les détails des facettes (défaut: true)
- `format` (string) : Format de réponse ("standard", "detailed", "summary")

**Réponse :**
```json
{
  "success": true,
  "data": {
    "session_info": {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": 123,
      "version_id": "hexaco_60_fr",
      "completed_at": "2024-01-15T10:45:00Z",
      "total_test_time": 900
    },
    "domain_scores": {
      "Honesty-Humility": {
        "percentile": 75,
        "raw_score": 3.8,
        "interpretation": "Élevé",
        "description": "Vous avez tendance à être sincère, équitable et modeste."
      },
      "Emotionality": {
        "percentile": 45,
        "raw_score": 2.9,
        "interpretation": "Moyen",
        "description": "Vous gérez généralement bien vos émotions."
      },
      "Extraversion": {
        "percentile": 82,
        "raw_score": 4.1,
        "interpretation": "Très élevé",
        "description": "Vous êtes très sociable et énergique."
      },
      "Agreeableness": {
        "percentile": 60,
        "raw_score": 3.4,
        "interpretation": "Modérément élevé",
        "description": "Vous êtes généralement coopératif et patient."
      },
      "Conscientiousness": {
        "percentile": 88,
        "raw_score": 4.3,
        "interpretation": "Très élevé",
        "description": "Vous êtes très organisé et discipliné."
      },
      "Openness": {
        "percentile": 70,
        "raw_score": 3.7,
        "interpretation": "Élevé",
        "description": "Vous appréciez l'art et les nouvelles expériences."
      }
    },
    "facet_scores": {
      "Sincerity": {
        "percentile": 78,
        "raw_score": 3.9,
        "domain": "Honesty-Humility"
      },
      "Fairness": {
        "percentile": 72,
        "raw_score": 3.7,
        "domain": "Honesty-Humility"
      }
    },
    "profile_summary": {
      "highest_domains": ["Conscientiousness", "Extraversion"],
      "lowest_domains": ["Emotionality"],
      "personality_type": "Organisateur Social",
      "key_strengths": [
        "Leadership naturel",
        "Grande organisation",
        "Fiabilité"
      ],
      "development_areas": [
        "Gestion du stress",
        "Flexibilité"
      ]
    },
    "chart_data": {
      "radar_chart": {
        "labels": ["H", "E", "X", "A", "C", "O"],
        "values": [75, 45, 82, 60, 88, 70]
      },
      "bar_chart": {
        "domains": [
          {"name": "Honnêteté-Humilité", "value": 75, "color": "#FF6B6B"},
          {"name": "Émotionnalité", "value": 45, "color": "#4ECDC4"},
          {"name": "Extraversion", "value": 82, "color": "#45B7D1"},
          {"name": "Agréabilité", "value": 60, "color": "#96CEB4"},
          {"name": "Conscienciosité", "value": 88, "color": "#FFEAA7"},
          {"name": "Ouverture", "value": 70, "color": "#DDA0DD"}
        ]
      }
    }
  }
}
```

### POST /api/hexaco/calculate-scores
Calcule les scores pour des réponses données (utile pour les tests ou simulations).

**Corps de la requête :**
```json
{
  "version_id": "hexaco_60_fr",
  "responses": {
    "1": 4,
    "2": 3,
    "3": 5
  },
  "options": {
    "include_raw_scores": true,
    "include_interpretations": true
  }
}
```

### GET /api/hexaco/norms/{version_id}
Récupère les normes de population pour une version du test.

**Paramètres :**
- `version_id` (path) : Identifiant de la version

**Réponse :**
```json
{
  "success": true,
  "data": {
    "version_id": "hexaco_60_fr",
    "sample_size": 5000,
    "demographics": {
      "age_range": "18-65",
      "gender_distribution": {"male": 48, "female": 52},
      "countries": ["France", "Canada", "Belgium"]
    },
    "domain_norms": {
      "Honesty-Humility": {
        "mean": 3.2,
        "std_dev": 0.6,
        "percentiles": {
          "10": 2.4,
          "25": 2.8,
          "50": 3.2,
          "75": 3.6,
          "90": 4.0
        }
      }
    }
  }
}
```

## Endpoints d'Analyse {#analyse}

### POST /api/hexaco/insights
Génère des insights personnalisés basés sur les scores HEXACO.

**Corps de la requête :**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "context": {
    "career_focus": true,
    "relationship_focus": false,
    "development_focus": true,
    "user_goals": ["leadership", "team_management"]
  },
  "language": "fr"
}
```

**Réponse :**
```json
{
  "success": true,
  "data": {
    "personality_insights": {
      "overview": "Votre profil révèle un leader naturel avec de fortes capacités organisationnelles...",
      "detailed_analysis": {
        "strengths": [
          {
            "area": "Leadership",
            "description": "Votre combinaison d'extraversion élevée et de conscienciosité vous rend naturellement apte au leadership.",
            "supporting_domains": ["Extraversion", "Conscientiousness"]
          }
        ],
        "challenges": [
          {
            "area": "Gestion du stress",
            "description": "Votre score modéré en émotionnalité suggère que vous pourriez bénéficier de techniques de gestion du stress.",
            "supporting_domains": ["Emotionality"]
          }
        ]
      }
    },
    "career_recommendations": [
      {
        "role": "Chef de projet",
        "match_score": 92,
        "reasoning": "Votre organisation et votre leadership naturel sont parfaits pour ce rôle.",
        "required_skills": ["Planification", "Communication", "Gestion d'équipe"]
      }
    ],
    "development_plan": {
      "short_term": [
        {
          "goal": "Améliorer la gestion du stress",
          "actions": ["Méditation quotidienne", "Techniques de respiration"],
          "timeline": "1-3 mois"
        }
      ],
      "long_term": [
        {
          "goal": "Développer l'intelligence émotionnelle",
          "actions": ["Formation en leadership", "Coaching personnel"],
          "timeline": "6-12 mois"
        }
      ]
    }
  }
}
```

### GET /api/hexaco/comparisons/{session_id}
Compare les résultats avec différents groupes de référence.

**Paramètres de requête :**
- `compare_to` (string) : Groupe de comparaison ("general_population", "professionals", "leaders")
- `demographic_filters` (object) : Filtres démographiques

**Réponse :**
```json
{
  "success": true,
  "data": {
    "user_scores": {
      "Honesty-Humility": 75,
      "Extraversion": 82
    },
    "comparisons": {
      "general_population": {
        "Honesty-Humility": {
          "user_percentile": 75,
          "group_mean": 50,
          "difference": "+25",
          "interpretation": "Significativement plus élevé"
        }
      },
      "professionals": {
        "Honesty-Humility": {
          "user_percentile": 65,
          "group_mean": 60,
          "difference": "+5",
          "interpretation": "Légèrement plus élevé"
        }
      }
    }
  }
}
```

### GET /api/hexaco/reports/{session_id}
Génère un rapport PDF détaillé des résultats.

**Paramètres de requête :**
- `format` (string) : Format du rapport ("pdf", "html", "json")
- `template` (string) : Template à utiliser ("standard", "professional", "detailed")
- `language` (string) : Langue du rapport ("fr", "en")

**Réponse :**
```json
{
  "success": true,
  "data": {
    "report_id": "report_123456",
    "download_url": "https://api.orientor.com/api/hexaco/downloads/report_123456.pdf",
    "expires_at": "2024-01-22T10:45:00Z",
    "format": "pdf",
    "size_bytes": 2048576,
    "pages": 12
  }
}
```

## Gestion des Erreurs {#erreurs}

### Structure des Erreurs
```json
{
  "success": false,
  "error": {
    "code": "HEXACO_001",
    "message": "Version non trouvée",
    "details": "La version 'hexaco_invalid' n'existe pas",
    "field": "version_id",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Codes d'Erreur HEXACO

#### Erreurs de Configuration (HEXACO_0xx)
- `HEXACO_001` : Version non trouvée
- `HEXACO_002` : Langue non supportée
- `HEXACO_003` : Configuration invalide

#### Erreurs de Session (HEXACO_1xx)
- `HEXACO_101` : Session non trouvée
- `HEXACO_102` : Session expirée
- `HEXACO_103` : Session déjà complétée
- `HEXACO_104` : Session non autorisée

#### Erreurs de Réponse (HEXACO_2xx)
- `HEXACO_201` : Réponse invalide
- `HEXACO_202` : Question non trouvée
- `HEXACO_203` : Valeur hors limites
- `HEXACO_204` : Réponse déjà enregistrée

#### Erreurs de Scoring (HEXACO_3xx)
- `HEXACO_301` : Test incomplet
- `HEXACO_302` : Erreur de calcul
- `HEXACO_303` : Données insuffisantes
- `HEXACO_304` : Normes non disponibles

#### Erreurs d'Analyse (HEXACO_4xx)
- `HEXACO_401` : Résultats non disponibles
- `HEXACO_402` : Contexte invalide
- `HEXACO_403` : Analyse non supportée

### Gestion des Erreurs de Validation
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Erreurs de validation",
    "details": {
      "version_id": ["Ce champ est requis"],
      "response_value": ["Doit être entre 1 et 5"],
      "user_id": ["Doit être un entier positif"]
    }
  }
}
```

### Limites de Taux (Rate Limiting)
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Trop de requêtes",
    "details": "Limite de 100 requêtes par minute dépassée",
    "retry_after": 60
  }
}
```

## Exemples d'Utilisation {#exemples}

### Workflow Complet en JavaScript

```javascript
class HexacoAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        'Accept': 'application/vnd.orientor.v1+json'
      },
      ...options
    };

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error?.message || 'API Error');
    }

    return data;
  }

  // Récupérer les versions disponibles
  async getVersions() {
    return this.request('/api/hexaco/versions');
  }

  // Créer une session de test
  async createSession(userId, versionId) {
    return this.request('/api/hexaco/sessions', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        version_id: versionId
      })
    });
  }

  // Récupérer les questions
  async getQuestions(versionId) {
    return this.request(`/api/hexaco/questions/${versionId}`);
  }

  // Sauvegarder une réponse
  async saveResponse(sessionId, itemId, value, responseTime) {
    return this.request('/api/hexaco/responses', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        item_id: itemId,
        response_value: value,
        response_time_ms: responseTime
      })
    });
  }

  // Compléter le test
  async completeTest(sessionId) {
    return this.request('/api/hexaco/complete', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId
      })
    });
  }

  // Récupérer les résultats
  async getResults(sessionId) {
    return this.request(`/api/hexaco/results/${sessionId}`);
  }
}

// Exemple d'utilisation
async function runHexacoTest() {
  const api = new HexacoAPI('https://api.orientor.com', 'your-jwt-token');
  
  try {
    // 1. Récupérer les versions
    const versions = await api.getVersions();
    console.log('Versions disponibles:', versions.data);
    
    // 2. Créer une session
    const session = await api.createSession(123, 'hexaco_60_fr');
    const sessionId = session.data.session_id;
    console.log('Session créée:', sessionId);
    
    // 3. Récupérer les questions
    const questions = await api.getQuestions('hexaco_60_fr');
    console.log(`${questions.data.questions.length} questions chargées`);
    
    // 4. Simuler les réponses
    for (const question of questions.data.questions) {
      const startTime = Date.now();
      
      // Simuler le temps de réflexion
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Réponse aléatoire entre 1 et 5
      const response = Math.floor(Math.random() * 5) + 1;
      const responseTime = Date.now() - startTime;
      
      await api.saveResponse(sessionId, question.item_id, response, responseTime);
      console.log(`Question ${question.item_id} répondue: ${response}`);
    }
    
    // 5. Compléter le test
    await api.completeTest(sessionId);
    console.log('Test complété');
    
    // 6. Récupérer les résultats
    const results = await api.getResults(sessionId);
    console.log('Résultats:', results.data.domain_scores);
    
  } catch (error) {
    console.error('Erreur:', error.message);
  }
}
```

### Exemple Python avec Requests

```python
import requests
import time
import random
from typing import Dict, Any

class HexacoAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.orientor.v1+json'
        })