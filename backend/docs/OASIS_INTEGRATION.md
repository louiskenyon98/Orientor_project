# Intégration du Module de Formatage OaSIS

Ce document décrit l'intégration du module de formatage OaSIS avec le système d'embeddings existant.

## Vue d'ensemble

Le module de formatage OaSIS (`format_user_profile_oasis_style.py`) transforme les profils utilisateurs en un format standardisé qui améliore la qualité des embeddings et la pertinence des recommandations de carrière. Cette intégration permet une transition progressive du système d'embeddings actuel vers le nouveau système basé sur OaSIS.

## Composants clés

1. **Module de formatage OaSIS** (`scripts/format_user_profile_oasis_style.py`)
   - Transforme les profils utilisateurs en format OaSIS
   - Utilise GPT-4o pour générer des descriptions riches et structurées

2. **Service d'embeddings** (`backend/app/services/embedding_service.py`)
   - Nouvelles fonctions pour générer et stocker les embeddings OaSIS
   - Maintient la compatibilité avec le système existant

3. **Service de recommandation de carrière** (`backend/app/services/career_recommendation_service.py`)
   - Modifié pour utiliser les embeddings OaSIS optionnellement
   - Permet une transition progressive entre l'ancien et le nouveau système

4. **Migration de base de données** (`backend/alembic/versions/add_oasis_columns.py`)
   - Ajoute les colonnes `oasis_profile` et `oasis_embedding` à la table `user_profiles`

5. **Script de test** (`backend/scripts/test_oasis_embeddings.py`)
   - Permet de tester toutes les fonctionnalités liées aux embeddings OaSIS

## Nouvelles fonctionnalités

### Dans `embedding_service.py`

- `format_user_profile_oasis(db, user_id)`: Formate le profil utilisateur selon le style OaSIS
- `generate_oasis_embedding(db, user_id)`: Génère un embedding à partir du profil OaSIS formaté
- `process_user_oasis_embedding(db, user_id)`: Traite la génération et le stockage de l'embedding OaSIS
- `get_user_oasis_embedding(db, user_id)`: Récupère l'embedding OaSIS existant d'un utilisateur

### Dans `career_recommendation_service.py`

- Paramètre `use_oasis` ajouté à `get_user_embedding()`: Permet de choisir entre les embeddings standard et OaSIS
- Paramètre `use_oasis` ajouté à `get_career_recommendations()`: Permet de générer des recommandations basées sur les embeddings OaSIS

## Schéma de base de données

Deux nouvelles colonnes ont été ajoutées à la table `user_profiles`:

- `oasis_profile` (Text): Stocke le profil formaté selon le style OaSIS
- `oasis_embedding` (JSONB): Stocke l'embedding généré à partir du profil OaSIS

## Utilisation

### Générer un embedding OaSIS pour un utilisateur

```python
from app.services.embedding_service import process_user_oasis_embedding

# Générer et stocker l'embedding OaSIS
success = process_user_oasis_embedding(db, user_id)
```

### Obtenir des recommandations basées sur l'embedding OaSIS

```python
from app.services.career_swipe.career_recommendation_service import get_career_recommendations

# Obtenir des recommandations basées sur l'embedding OaSIS
recommendations = get_career_recommendations(db, user_id, use_oasis=True)
```

### Tester les fonctionnalités OaSIS

```bash
# Tester toutes les fonctionnalités OaSIS pour un utilisateur spécifique
python backend/scripts/test_oasis_embeddings.py --user_id 123 --all

# Tester uniquement le formatage OaSIS
python backend/scripts/test_oasis_embeddings.py --user_id 123 --format

# Comparer les recommandations standard et OaSIS
python backend/scripts/test_oasis_embeddings.py --user_id 123 --compare
```

## Migration

Pour appliquer la migration qui ajoute les colonnes OaSIS à la base de données:

```bash
cd backend
python -m alembic upgrade head
```

## Transition progressive

Le système a été conçu pour permettre une transition progressive de l'ancien système d'embeddings vers le nouveau système basé sur OaSIS:

1. Les deux systèmes peuvent fonctionner en parallèle
2. Les embeddings OaSIS sont stockés dans des colonnes séparées
3. Le paramètre `use_oasis` permet de choisir quel système utiliser
4. En cas d'échec avec les embeddings OaSIS, le système peut revenir aux embeddings standard

## Avantages du format OaSIS

- **Standardisation**: Format cohérent pour tous les profils utilisateurs
- **Richesse sémantique**: Descriptions détaillées qui capturent mieux les nuances des profils
- **Alignement avec les descriptions d'emploi**: Format similaire aux descriptions d'emploi, améliorant la pertinence des recommandations
- **Intégration des recommandations sauvegardées**: Les préférences de l'utilisateur sont prises en compte dans le profil formaté

## Prochaines étapes

1. Évaluer la qualité des recommandations basées sur les embeddings OaSIS par rapport aux embeddings standard
2. Ajuster les paramètres du formatage OaSIS en fonction des résultats
3. Implémenter un mécanisme de mise à jour périodique des embeddings OaSIS
4. Développer une interface utilisateur pour permettre aux utilisateurs de choisir entre les deux systèmes