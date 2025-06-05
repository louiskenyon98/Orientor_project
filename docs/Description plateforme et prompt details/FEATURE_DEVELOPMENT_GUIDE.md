# Guide de Développement de Nouvelles Fonctionnalités - Plateforme Navigo

## Introduction

Ce guide fournit un framework structuré pour développer de nouvelles fonctionnalités dans la plateforme Navigo, en mettant l'accent sur l'intégration avec l'écosystème vectoriel existant et le respect des patterns architecturaux établis.

## Principes Fondamentaux

### 1. Représentation Vectorielle au Cœur
Toute nouvelle fonctionnalité doit considérer comment elle s'intègre avec les embeddings existants:
- **Embeddings Standard (1024D)**: Pour les analyses générales de profil
- **Embeddings OaSIS (384D)**: Pour les aspects psychologiques
- **Embeddings ESCO (384D)**: Pour les aspects professionnels spécialisés

### 2. Approche Longitudinale
Chaque fonctionnalité doit prévoir:
- Le suivi temporel des données
- L'évolution des profils utilisateur
- L'historique des interactions
- La progression dans le temps

### 3. Cohérence Architecturale
Respecter les patterns existants:
- Services centralisés pour les embeddings
- API REST cohérente
- Gestion d'erreurs standardisée
- Logging structuré

## Framework de Développement

### Phase 1: Analyse et Conception

#### 1.1 Analyse des Besoins Vectoriels
```python
# Questions à se poser:
# - Quel type d'embedding utiliser?
# - Faut-il créer un nouveau type d'embedding?
# - Comment la fonctionnalité s'intègre avec Pinecone?
# - Quelles métriques de similarité utiliser?

# Template d'analyse
EMBEDDING_ANALYSIS = {
    "feature_name": "nom_de_la_fonctionnalité",
    "embedding_type": "standard|oasis|esco_*|nouveau",
    "vector_operations": ["similarity", "clustering", "recommendation"],
    "pinecone_integration": True/False,
    "new_index_required": True/False,
    "temporal_aspect": True/False
}
```

#### 1.2 Modélisation des Données
```python
# Template pour nouveaux modèles SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ARRAY, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..utils.database import Base

class NewFeatureModel(Base):
    __tablename__ = "new_feature_table"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Champs vectoriels si nécessaire
    embedding = Column(ARRAY(Float), nullable=True)
    
    # Champs temporels pour suivi longitudinal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="new_feature_items")
```

#### 1.3 Architecture du Service
```python
# Template de service vectoriel
class NewFeatureService:
    def __init__(self):
        self.pinecone_client = None
        self.embedding_model = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialiser Pinecone et modèles d'embedding"""
        pass
    
    def get_user_embedding(self, db: Session, user_id: int, 
                          embedding_type: str = "standard") -> Optional[np.ndarray]:
        """Récupérer l'embedding utilisateur approprié"""
        pass
    
    def generate_recommendations(self, db: Session, user_id: int, 
                               limit: int = 10) -> List[Dict]:
        """Générer des recommandations basées sur les embeddings"""
        pass
    
    def update_user_vector(self, db: Session, user_id: int, 
                          new_data: Dict) -> bool:
        """Mettre à jour la représentation vectorielle"""
        pass
```

### Phase 2: Implémentation Backend

#### 2.1 Service d'Embedding
```python
# Exemple d'intégration avec les services existants
from app.services.Oasisembedding_service import (
    generate_embedding_from_text_384,
    store_embedding,
    parse_embedding
)

class FeatureEmbeddingService:
    def process_feature_embedding(self, db: Session, user_id: int, 
                                 feature_data: Dict) -> bool:
        """
        Traiter les embeddings pour la nouvelle fonctionnalité
        """
        try:
            # 1. Formater les données selon le template approprié
            formatted_text = self._format_feature_data(feature_data)
            
            # 2. Générer l'embedding
            embedding = generate_embedding_from_text_384(
                text=formatted_text,
                model_label=f"Feature-{self.__class__.__name__}"
            )
            
            if embedding is None:
                return False
            
            # 3. Stocker l'embedding
            return store_embedding(
                db, user_id, embedding, 
                column_name=f"feature_embedding"
            )
            
        except Exception as e:
            logger.error(f"Erreur traitement embedding: {str(e)}")
            return False
    
    def _format_feature_data(self, data: Dict) -> str:
        """Formater les données selon le template de la fonctionnalité"""
        # Implémenter le formatage spécifique
        pass
```

#### 2.2 Router API
```python
# Template de router FastAPI
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.routers.user import get_current_user

router = APIRouter(prefix="/api/v1/new-feature", tags=["new-feature"])

@router.get("/recommendations")
async def get_feature_recommendations(
    embedding_type: str = Query("standard", description="Type d'embedding"),
    limit: int = Query(10, description="Nombre de recommandations"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtenir des recommandations pour la nouvelle fonctionnalité
    """
    try:
        service = NewFeatureService()
        recommendations = service.generate_recommendations(
            db, current_user.id, limit
        )
        
        return {
            "recommendations": recommendations,
            "user_id": current_user.id,
            "embedding_type": embedding_type
        }
        
    except Exception as e:
        logger.error(f"Erreur recommandations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-profile")
async def update_feature_profile(
    profile_data: FeatureProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mettre à jour le profil pour la fonctionnalité
    """
    try:
        service = NewFeatureService()
        success = service.update_user_vector(
            db, current_user.id, profile_data.dict()
        )
        
        if success:
            return {"message": "Profil mis à jour avec succès"}
        else:
            raise HTTPException(status_code=400, detail="Échec mise à jour")
            
    except Exception as e:
        logger.error(f"Erreur mise à jour: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3 Migration de Base de Données
```python
# Template de migration Alembic
"""Add new feature tables

Revision ID: add_new_feature
Revises: previous_revision
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Créer la nouvelle table
    op.create_table('new_feature_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feature_embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Créer les index
    op.create_index(op.f('ix_new_feature_table_id'), 'new_feature_table', ['id'], unique=False)
    op.create_index(op.f('ix_new_feature_table_user_id'), 'new_feature_table', ['user_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_new_feature_table_user_id'), table_name='new_feature_table')
    op.drop_index(op.f('ix_new_feature_table_id'), table_name='new_feature_table')
    op.drop_table('new_feature_table')
```

### Phase 3: Implémentation Frontend

#### 3.1 Service API Frontend
```typescript
// Template de service API frontend
import api from './api';

export interface FeatureRecommendation {
  id: string;
  title: string;
  description: string;
  score: number;
  metadata: Record<string, any>;
}

export interface FeatureProfileData {
  // Définir les champs du profil
  [key: string]: any;
}

class NewFeatureService {
  async getRecommendations(
    embeddingType: string = 'standard',
    limit: number = 10
  ): Promise<FeatureRecommendation[]> {
    try {
      const response = await api.get(
        `/api/v1/new-feature/recommendations?embedding_type=${embeddingType}&limit=${limit}`
      );
      return response.data.recommendations;
    } catch (error) {
      console.error('Erreur récupération recommandations:', error);
      throw error;
    }
  }

  async updateProfile(profileData: FeatureProfileData): Promise<boolean> {
    try {
      await api.post('/api/v1/new-feature/update-profile', profileData);
      return true;
    } catch (error) {
      console.error('Erreur mise à jour profil:', error);
      throw error;
    }
  }
}

export const newFeatureService = new NewFeatureService();
```

#### 3.2 Composant React
```tsx
// Template de composant React
import React, { useState, useEffect } from 'react';
import { newFeatureService, FeatureRecommendation } from '@/services/newFeatureService';

interface NewFeatureComponentProps {
  userId?: number;
  embeddingType?: string;
}

export const NewFeatureComponent: React.FC<NewFeatureComponentProps> = ({
  userId,
  embeddingType = 'standard'
}) => {
  const [recommendations, setRecommendations] = useState<FeatureRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const data = await newFeatureService.getRecommendations(embeddingType);
        setRecommendations(data);
      } catch (err) {
        setError('Erreur lors du chargement des recommandations');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [embeddingType]);

  if (loading) return <div>Chargement...</div>;
  if (error) return <div>Erreur: {error}</div>;

  return (
    <div className="new-feature-component">
      <h2>Nouvelle Fonctionnalité</h2>
      <div className="recommendations-grid">
        {recommendations.map((rec) => (
          <div key={rec.id} className="recommendation-card">
            <h3>{rec.title}</h3>
            <p>{rec.description}</p>
            <span className="score">Score: {rec.score.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### 3.3 Page Next.js
```tsx
// Template de page Next.js
'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { NewFeatureComponent } from '@/components/NewFeatureComponent';

export default function NewFeaturePage() {
  return (
    <MainLayout showNav={true}>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Nouvelle Fonctionnalité</h1>
          
          <NewFeatureComponent embeddingType="standard" />
        </div>
      </div>
    </MainLayout>
  );
}
```

### Phase 4: Intégration Vectorielle Avancée

#### 4.1 Pinecone Integration
```python
# Template d'intégration Pinecone
import pinecone
from pinecone import Pinecone
import numpy as np
from typing import List, Dict, Any

class PineconeFeatureService:
    def __init__(self, index_name: str = "new-feature-index"):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = index_name
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialiser l'index Pinecone pour la fonctionnalité"""
        try:
            # Vérifier si l'index existe
            if self.index_name not in self.pc.list_indexes().names():
                # Créer l'index si nécessaire
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # Ajuster selon le type d'embedding
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Index Pinecone {self.index_name} initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation Pinecone: {str(e)}")
    
    def upsert_user_vector(self, user_id: int, embedding: np.ndarray, 
                          metadata: Dict[str, Any]) -> bool:
        """Insérer/mettre à jour le vecteur utilisateur"""
        try:
            vector_data = {
                "id": f"user_{user_id}",
                "values": embedding.tolist(),
                "metadata": metadata
            }
            
            self.index.upsert(vectors=[vector_data])
            return True
            
        except Exception as e:
            logger.error(f"Erreur upsert vecteur: {str(e)}")
            return False
    
    def query_similar_items(self, embedding: np.ndarray, 
                           top_k: int = 10, 
                           filter_dict: Dict = None) -> List[Dict]:
        """Rechercher des éléments similaires"""
        try:
            results = self.index.query(
                vector=embedding.tolist(),
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
            
        except Exception as e:
            logger.error(f"Erreur requête similarité: {str(e)}")
            return []
```

#### 4.2 Analyse Temporelle
```python
# Template pour analyse longitudinale
class TemporalAnalysisService:
    def analyze_user_evolution(self, db: Session, user_id: int, 
                              time_window_days: int = 30) -> Dict[str, Any]:
        """
        Analyser l'évolution temporelle d'un utilisateur
        """
        try:
            # Récupérer l'historique des embeddings
            embeddings_history = self._get_embeddings_history(
                db, user_id, time_window_days
            )
            
            if len(embeddings_history) < 2:
                return {"error": "Pas assez de données historiques"}
            
            # Calculer les métriques d'évolution
            evolution_metrics = self._calculate_evolution_metrics(embeddings_history)
            
            # Identifier les tendances
            trends = self._identify_trends(embeddings_history)
            
            return {
                "user_id": user_id,
                "time_window": time_window_days,
                "evolution_metrics": evolution_metrics,
                "trends": trends,
                "data_points": len(embeddings_history)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse temporelle: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_evolution_metrics(self, embeddings_history: List[Dict]) -> Dict:
        """Calculer les métriques d'évolution"""
        # Implémenter le calcul de métriques comme:
        # - Vitesse de changement
        # - Direction de l'évolution
        # - Stabilité du profil
        pass
    
    def predict_future_interests(self, db: Session, user_id: int) -> List[Dict]:
        """Prédire les intérêts futurs basés sur l'évolution"""
        # Implémenter la prédiction basée sur les tendances
        pass
```

### Phase 5: Tests et Validation

#### 5.1 Tests Unitaires
```python
# Template de tests unitaires
import pytest
from unittest.mock import Mock, patch
from app.services.new_feature_service import NewFeatureService

class TestNewFeatureService:
    @pytest.fixture
    def service(self):
        return NewFeatureService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    def test_get_user_embedding(self, service, mock_db):
        """Tester la récupération d'embedding utilisateur"""
        # Arrange
        user_id = 1
        expected_embedding = np.array([0.1, 0.2, 0.3])
        
        # Act
        with patch.object(service, '_fetch_embedding_from_db') as mock_fetch:
            mock_fetch.return_value = expected_embedding
            result = service.get_user_embedding(mock_db, user_id)
        
        # Assert
        assert np.array_equal(result, expected_embedding)
        mock_fetch.assert_called_once_with(mock_db, user_id, "standard")
    
    def test_generate_recommendations(self, service, mock_db):
        """Tester la génération de recommandations"""
        # Implémenter les tests de recommandations
        pass
```

#### 5.2 Tests d'Intégration
```python
# Template de tests d'intégration
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestNewFeatureAPI:
    def test_get_recommendations_endpoint(self):
        """Tester l'endpoint de recommandations"""
        response = client.get(
            "/api/v1/new-feature/recommendations?limit=5",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) <= 5
    
    def test_update_profile_endpoint(self):
        """Tester l'endpoint de mise à jour de profil"""
        profile_data = {
            "field1": "value1",
            "field2": "value2"
        }
        
        response = client.post(
            "/api/v1/new-feature/update-profile",
            json=profile_data,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Profil mis à jour avec succès"
```

### Phase 6: Déploiement et Monitoring

#### 6.1 Configuration de Déploiement
```yaml
# docker-compose.override.yml pour la nouvelle fonctionnalité
version: "3.8"

services:
  backend:
    environment:
      - NEW_FEATURE_ENABLED=true
      - NEW_FEATURE_PINECONE_INDEX=new-feature-index
      - NEW_FEATURE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

#### 6.2 Monitoring et Métriques
```python
# Template de monitoring
import time
from functools import wraps
from app.utils.logging_config import setup_logging

logger = setup_logging()

def monitor_performance(func):
    """Décorateur pour monitorer les performances"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper

class FeatureMetrics:
    @staticmethod
    def log_embedding_generation(user_id: int, embedding_type: str, 
                               success: bool, duration: float):
        """Logger la génération d'embeddings"""
        logger.info(f"Embedding generation - User: {user_id}, "
                   f"Type: {embedding_type}, Success: {success}, "
                   f"Duration: {duration:.2f}s")
    
    @staticmethod
    def log_recommendation_request(user_id: int, limit: int, 
                                 results_count: int, duration: float):
        """Logger les requêtes de recommandations"""
        logger.info(f"Recommendation request - User: {user_id}, "
                   f"Limit: {limit}, Results: {results_count}, "
                   f"Duration: {duration:.2f}s")
```

## Checklist de Développement

### ✅ Phase de Conception
- [ ] Analyse des besoins vectoriels
- [ ] Choix du type d'embedding approprié
- [ ] Conception de l'architecture du service
- [ ] Modélisation des données avec aspects temporels
- [ ] Définition des APIs

### ✅ Phase d'Implémentation Backend
- [ ] Service d'embedding intégré
- [ ] Router API avec gestion d'erreurs
- [ ] Migration de base de données
- [ ] Intégration Pinecone si nécessaire
- [ ] Tests unitaires et d'intégration

### ✅ Phase d'Implémentation Frontend
- [ ] Service API frontend
- [ ] Composants React réutilisables
- [ ] Pages Next.js avec routing
- [ ] Gestion des états et erreurs
- [ ] Tests frontend

### ✅ Phase de Validation
- [ ] Tests de performance
- [ ] Validation des embeddings
- [ ] Tests d'intégration complète
- [ ] Validation UX/UI

### ✅ Phase de Déploiement
- [ ] Configuration de déploiement
- [ ] Monitoring et logging
- [ ] Documentation utilisateur
- [ ] Formation équipe

## Bonnes Pratiques

### 1. Gestion des Embeddings
- Toujours valider la dimension des embeddings
- Implémenter la gestion d'erreurs pour les modèles
- Prévoir la mise à jour incrémentale
- Monitorer les performances des requêtes vectorielles

### 2. Aspects Temporels
- Stocker l'historique des modifications
- Implémenter le versioning des données
- Prévoir l'analyse d'évolution
- Considérer la rétention des données

### 3. Performance
- Utiliser la mise en cache appropriée
- Optimiser les requêtes Pinecone
- Implémenter la pagination
- Monitorer les temps de réponse

### 4. Sécurité
- Valider toutes les entrées utilisateur
- Implémenter l'authentification appropriée
- Protéger les données sensibles
- Auditer les accès aux embeddings

Ce guide fournit un framework complet pour développer de nouvelles fonctionnalités dans l'écosystème Navigo tout en maintenant la cohérence architecturale et en exploitant pleinement les capacités vectorielles de la plateforme.