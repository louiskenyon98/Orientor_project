# Documentation API HEXACO-PI-R

## Vue d'ensemble

L'API HEXACO-PI-R permet d'administrer et de scorer le test de personnalité HEXACO-PI-R dans 4 versions :
- **hexaco_60_fr** : Version courte française (60 questions, ~15 min)
- **hexaco_60_en** : Version courte anglaise (60 questions, ~15 min)
- **hexaco_100_fr** : Version complète française (100 questions, ~25 min)
- **hexaco_100_en** : Version complète anglaise (100 questions, ~25 min)

## Endpoints disponibles

### 1. Métadonnées générales
```http
GET /api/tests/hexaco/
```
Retourne les métadonnées complètes : versions, langues et domaines HEXACO.

**Réponse :**
```json
{
  "versions": {
    "hexaco_60_fr": {
      "title": "Test HEXACO-PI-R (Version courte - Français)",
      "description": "Évaluation complète de personnalité en 60 questions",
      "item_count": 60,
      "estimated_duration": 15,
      "language": "fr",
      "active": true
    }
  },
  "languages": {
    "fr": {
      "name": "Français",
      "flag": "🇫🇷",
      "description": "Version française du test HEXACO-PI-R"
    }
  },
  "domains": {
    "Honesty-Humility": {
      "facets": ["Sincerity", "Fairness", "Greed-Avoidance", "Modesty"],
      "description": "Tendance à être sincère, équitable, modeste et non matérialiste"
    }
  }
}
```

### 2. Langues disponibles
```http
GET /api/tests/hexaco/languages
```

### 3. Versions disponibles
```http
GET /api/tests/hexaco/versions?language=fr
```
Paramètre optionnel `language` pour filtrer par langue.

### 4. Démarrer un test
```http
POST /api/tests/hexaco/start
```
**Body :**
```json
{
  "version_id": "hexaco_60_fr"
}
```
**Réponse :**
```json
{
  "session_id": "uuid-de-la-session",
  "message": "Session de test HEXACO créée avec succès"
}
```

### 5. Récupérer les questions
```http
GET /api/tests/hexaco/questions?version_id=hexaco_60_fr
```
**Réponse :**
```json
[
  {
    "item_id": 1,
    "item_text": "Je serais assez ennuyé par une visite dans une galerie d'art.",
    "response_min": 1,
    "response_max": 5,
    "version": "60",
    "language": "french",
    "reverse_keyed": true,
    "facet": "Aesthetic Appreciation"
  }
]
```

### 6. Sauvegarder une réponse
```http
POST /api/tests/hexaco/answer
```
**Body :**
```json
{
  "session_id": "uuid-de-la-session",
  "item_id": 1,
  "response_value": 3,
  "response_time_ms": 2500
}
```

### 7. Vérifier le progrès
```http
GET /api/tests/hexaco/progress/{session_id}
```
**Réponse :**
```json
{
  "total_items": 60,
  "completed_items": 25,
  "progress_percentage": 41.7,
  "status": "in_progress",
  "assessment_version": "hexaco_60_fr"
}
```

### 8. Calculer les scores
```http
GET /api/tests/hexaco/score/{session_id}?include_description=true
```
**Réponse :**
```json
{
  "domains": {
    "Honesty-Humility": 3.2,
    "Emotionality": 2.8,
    "Extraversion": 4.1,
    "Agreeableness": 3.7,
    "Conscientiousness": 4.3,
    "Openness": 3.9
  },
  "facets": {
    "Sincerity": 3.5,
    "Fairness": 3.0,
    "Greed-Avoidance": 3.1,
    "Modesty": 3.2
  },
  "percentiles": {
    "Honesty-Humility": 45.2,
    "Emotionality": 32.1
  },
  "reliability": {
    "Honesty-Humility": 0.87,
    "Emotionality": 0.82
  },
  "total_responses": 60,
  "completion_rate": 1.0,
  "narrative_description": "Description personnalisée générée par IA..."
}
```

### 9. Récupérer un profil utilisateur
```http
GET /api/tests/hexaco/my-profile?assessment_version=hexaco_60_fr
```

## Workflow complet

1. **Sélection de langue et version**
   ```javascript
   // Récupérer les langues disponibles
   const languages = await fetch('/api/tests/hexaco/languages');
   
   // Récupérer les versions pour une langue
   const versions = await fetch('/api/tests/hexaco/versions?language=fr');
   ```

2. **Démarrage du test**
   ```javascript
   const response = await fetch('/api/tests/hexaco/start', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ version_id: 'hexaco_60_fr' })
   });
   const { session_id } = await response.json();
   ```

3. **Récupération des questions**
   ```javascript
   const questions = await fetch('/api/tests/hexaco/questions?version_id=hexaco_60_fr');
   ```

4. **Soumission des réponses**
   ```javascript
   for (const question of questions) {
     await fetch('/api/tests/hexaco/answer', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({
         session_id,
         item_id: question.item_id,
         response_value: userResponse, // 1-5
         response_time_ms: responseTime
       })
     });
   }
   ```

5. **Calcul des scores**
   ```javascript
   const scores = await fetch(`/api/tests/hexaco/score/${session_id}?include_description=true`);
   ```

## Échelle de réponse

Toutes les questions HEXACO utilisent une échelle de Likert à 5 points :
- **1** = Fortement en désaccord
- **2** = En désaccord  
- **3** = Neutre
- **4** = D'accord
- **5** = Fortement d'accord

## Gestion des items inversés

Certains items sont "reverse_keyed" (inversés). Le scoring est automatiquement géré :
- Item normal : score = réponse utilisateur
- Item inversé : score = 6 - réponse utilisateur

## Domaines et facettes HEXACO

### Honesty-Humility (Honnêteté-Humilité)
- **Sincerity** (Sincérité)
- **Fairness** (Équité)  
- **Greed-Avoidance** (Évitement de l'avidité)
- **Modesty** (Modestie)

### Emotionality (Émotionnalité)
- **Fearfulness** (Peur)
- **Anxiety** (Anxiété)
- **Dependence** (Dépendance)
- **Sentimentality** (Sentimentalité)

### Extraversion
- **Social Self-Esteem** (Estime de soi sociale)
- **Social Boldness** (Audace sociale)
- **Sociability** (Sociabilité)
- **Liveliness** (Vivacité)

### Agreeableness (Agréabilité)
- **Forgiveness** (Pardon)
- **Gentleness** (Douceur)
- **Flexibility** (Flexibilité)
- **Patience** (Patience)

### Conscientiousness (Conscienciosité)
- **Organization** (Organisation)
- **Diligence** (Diligence)
- **Perfectionism** (Perfectionnisme)
- **Prudence** (Prudence)

### Openness (Ouverture)
- **Aesthetic Appreciation** (Appréciation esthétique)
- **Inquisitiveness** (Curiosité)
- **Creativity** (Créativité)
- **Unconventionality** (Non-conventionnalité)

## Authentification

Tous les endpoints nécessitent une authentification Bearer token :
```http
Authorization: Bearer your-jwt-token
```

## Codes d'erreur

- **400** : Données invalides (ex: réponse hors échelle 1-5)
- **401** : Non authentifié
- **403** : Accès refusé
- **404** : Session/version non trouvée
- **500** : Erreur serveur

## Limites et considérations

- Une session de test expire après 24h d'inactivité
- Les réponses peuvent être modifiées tant que le test n'est pas terminé
- Le calcul des scores finalise automatiquement le test
- Les descriptions narratives nécessitent une clé API OpenAI configurée