'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { generateInsight, saveInsight, rewriteInsight, InsightData, mockInsightData } from '@/services/insightService';
import styles from './insight.module.css';

const InsightPage: React.FC = () => {
  const router = useRouter();
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [insight, setInsight] = useState<InsightData | null>(null);
  const [feedback, setFeedback] = useState<string>('');
  const [showFullText, setShowFullText] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [rewriting, setRewriting] = useState<boolean>(false);

  useEffect(() => {
    // Récupérer l'ID de l'utilisateur depuis le localStorage
    const fetchUserId = () => {
      try {
        // Récupérer l'ID de l'utilisateur depuis le localStorage
        const userDataStr = localStorage.getItem('user_data');
        if (userDataStr) {
          const userData = JSON.parse(userDataStr);
          if (userData && userData.id) {
            console.log("ID utilisateur récupéré:", userData.id);
            setUserId(userData.id);
            return userData.id;
          }
        }
        
        // Fallback: utiliser l'ID 19 (celui qui est actuellement connecté selon les logs)
        console.warn("Aucun ID utilisateur trouvé dans localStorage, utilisation de l'ID 19");
        const fallbackId = 19;
        setUserId(fallbackId);
        return fallbackId;
      } catch (error) {
        console.error("Erreur lors de la récupération de l'ID utilisateur:", error);
        // Fallback en cas d'erreur
        const fallbackId = 19;
        setUserId(fallbackId);
        return fallbackId;
      }
    };

    const loadInsight = async () => {
      try {
        setLoading(true);
        const id = fetchUserId();
        
        // Appeler l'API même en mode développement pour tester les modifications
        console.log("Appel de l'API pour générer un insight...");
        const data = await generateInsight(id);
        console.log("Réponse de l'API:", data);
        setInsight(data);
      } catch (error) {
        console.error('Erreur lors du chargement de l\'insight:', error);
        // Fallback aux données simulées en cas d'erreur
        console.warn("Utilisation des données simulées suite à une erreur");
        setInsight(mockInsightData);
      } finally {
        setLoading(false);
      }
    };

    loadInsight();
  }, []);

  const handleSaveInsight = async () => {
    if (!userId || !insight) return;
    
    try {
      setSaving(true);
      await saveInsight(userId, insight.full_text);
      alert('Insight sauvegardé avec succès!');
      router.push('/profile'); // Rediriger vers le profil ou une autre page appropriée
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de l\'insight:', error);
      alert('Erreur lors de la sauvegarde. Veuillez réessayer.');
    } finally {
      setSaving(false);
    }
  };

  const handleRewriteInsight = async () => {
    if (!userId || !feedback) return;
    
    try {
      setRewriting(true);
      
      // Appeler l'API même en mode développement pour tester les modifications
      console.log("Appel de l'API pour réécrire l'insight avec le feedback:", feedback);
      const newInsight = await rewriteInsight(userId, feedback);
      console.log("Réponse de l'API pour la réécriture:", newInsight);
      setInsight(newInsight);
      setFeedback('');
    } catch (error) {
      console.error('Erreur lors de la réécriture de l\'insight:', error);
      alert('Erreur lors de la réécriture. Veuillez réessayer.');
    } finally {
      setRewriting(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.loadingSpinner}></div>
          <p>Génération de votre insight philosophique...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Philosophical Insight</h1>
      
      {insight && (
        <div className={styles.insightContainer}>
          <div className={styles.previewSection}>
            <h2>Aperçu</h2>
            <p className={styles.previewText}>{insight.preview}</p>
          </div>
          
          <div className={styles.mainSection}>
            <button 
              className={styles.toggleButton}
              onClick={() => setShowFullText(!showFullText)}
            >
              {showFullText ? 'Masquer le texte complet' : 'Afficher le texte complet'}
            </button>
            
            {showFullText && (
              <div className={styles.fullTextSection}>
                <h2>Texte complet</h2>
                <p className={styles.fullText}>{insight.full_text}</p>
              </div>
            )}
            
            <div className={styles.acceptSection}>
              <h2>Si vous acceptez cette vérité</h2>
              <p className={styles.acceptText}>{insight.if_you_accept}</p>
            </div>
          </div>
          
          <div className={styles.actionsSection}>
            <button 
              className={`${styles.actionButton} ${styles.saveButton}`}
              onClick={handleSaveInsight}
              disabled={saving}
            >
              {saving ? 'Sauvegarde en cours...' : 'Sauvegarder cet insight'}
            </button>
            
            <div className={styles.rewriteSection}>
              <h3>Vous souhaitez une perspective différente?</h3>
              <textarea
                className={styles.feedbackInput}
                placeholder="Donnez votre feedback pour obtenir un insight réécrit..."
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                rows={4}
              />
              <button 
                className={`${styles.actionButton} ${styles.rewriteButton}`}
                onClick={handleRewriteInsight}
                disabled={rewriting || !feedback}
              >
                {rewriting ? 'Réécriture en cours...' : 'Réécrire l\'insight'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      <button 
        className={styles.backButton}
        onClick={() => router.back()}
      >
        Retour
      </button>
    </div>
  );
};

export default InsightPage;