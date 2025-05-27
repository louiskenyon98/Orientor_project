'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import CompetenceTreeView from '../../components/tree/CompetenceTreeView';
import MainLayout from '../../components/layout/MainLayout';
import { generateCompetenceTree } from '../../services/competenceTreeService';

const CompetenceTreePage: React.FC = () => {
  console.log("CompetenceTreePage: Composant chargé");
  
  const router = useRouter();
  console.log("CompetenceTreePage: Router initialisé", router);
  
  const searchParams = useSearchParams();
  console.log("CompetenceTreePage: SearchParams récupérés", searchParams);
  
  const graphId = searchParams ? searchParams.get('graph_id') : null;
  console.log("CompetenceTreePage: GraphId récupéré", graphId);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fonction pour générer un nouvel arbre
  const handleGenerateTree = async () => {
    console.log("handleGenerateTree: Début de la génération de l'arbre");
    try {
      setLoading(true);
      console.log("handleGenerateTree: Loading state set to true");
      
      // Utilisez l'ID utilisateur actuel (à adapter selon votre système d'authentification)
      const userId = 1; // Exemple, à remplacer par l'ID réel de l'utilisateur
      console.log("handleGenerateTree: Appel à generateCompetenceTree avec userId:", userId);
      
      const result = await generateCompetenceTree(userId);
      console.log("handleGenerateTree: Résultat de generateCompetenceTree:", result);
      
      // Rediriger vers la même page avec le graph_id en paramètre
      const newUrl = `/competence-tree?graph_id=${result.graph_id}`;
      console.log("handleGenerateTree: Redirection vers:", newUrl);
      router.push(newUrl);
    } catch (err: any) {
      console.error("handleGenerateTree: Erreur lors de la génération:", err);
      setError(err.message || 'Une erreur est survenue lors de la génération de l\'arbre');
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="container">
        {!graphId ? (
          <div className="generate-tree-container" style={{ textAlign: 'center', padding: '50px' }}>
            <h2>Arbre de Compétences</h2>
            <p>Vous n'avez pas encore d'arbre de compétences. Générez-en un pour commencer!</p>
            <button
              onClick={handleGenerateTree}
              disabled={loading}
              style={{
                padding: '10px 20px',
                backgroundColor: '#2196f3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading ? 'Génération en cours...' : 'Générer mon arbre de compétences'}
            </button>
            {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
          </div>
        ) : (
          <CompetenceTreeView graphId={graphId} />
        )}
      </div>
    </MainLayout>
  );
};

export default CompetenceTreePage;