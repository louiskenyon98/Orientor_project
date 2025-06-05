'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import { getInsight, generateInsight, regenerateInsight, saveInsight, rewriteInsight, InsightData, mockInsightData } from '@/services/insightService';
import Link from 'next/link';
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
  const [regenerating, setRegenerating] = useState<boolean>(false);

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
        
        // D'abord essayer de récupérer un insight existant
        try {
          console.log("Tentative de récupération d'un insight existant...");
          const existingData = await getInsight();
          console.log("Insight existant trouvé:", existingData);
          setInsight(existingData);
        } catch (getError) {
          // Si aucun insight n'existe, ne pas en générer automatiquement
          console.log("Aucun insight existant trouvé");
          setInsight(null);
        }
      } catch (error) {
        console.error('Erreur lors du chargement de l\'insight:', error);
        setInsight(null);
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

  const handleGenerateFirstInsight = async () => {
    if (!userId) return;
    
    try {
      setLoading(true);
      console.log("Génération du premier insight...");
      const newInsight = await generateInsight(userId);
      console.log("Premier insight généré:", newInsight);
      setInsight(newInsight);
    } catch (error) {
      console.error('Erreur lors de la génération du premier insight:', error);
      alert('Erreur lors de la génération. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateInsight = async () => {
    try {
      setRegenerating(true);
      console.log("Régénération de l'insight...");
      const newInsight = await regenerateInsight();
      console.log("Insight régénéré:", newInsight);
      setInsight(newInsight);
    } catch (error) {
      console.error('Erreur lors de la régénération de l\'insight:', error);
      alert('Erreur lors de la régénération. Veuillez réessayer.');
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <MainLayout showNav={true}>
        <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
          <div className="relative z-10 w-full flex h-full grow">
            <div className="flex flex-col flex-1 w-full">
              <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
                <div className="flex items-center gap-4">
                  <Link
                    href="/"
                    className="premium-button-icon"
                    title="Retour à l'accueil"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </Link>
                  <h1 className="premium-title text-[32px] md:text-4xl font-bold leading-tight">
                    Insight Philosophique
                  </h1>
                </div>
              </div>
              <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
                <div className="flex items-center justify-center min-h-[400px]">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="premium-text-secondary">Génération de votre insight philosophique...</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout showNav={true}>
      <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
        <div className="relative z-10 w-full flex h-full grow">
          <div className="flex flex-col flex-1 w-full">
            {/* Header */}
            <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
              <div className="flex items-center gap-4">
                <Link
                  href="/"
                  className="premium-button-icon"
                  title="Retour à l'accueil"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Link>
                <h1 className="premium-title text-[32px] md:text-4xl font-bold leading-tight">
                  Insight Philosophique
                </h1>
              </div>
            </div>

            {/* Main Content Container */}
            <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
              {!insight && !loading && (
                <div className="text-center py-12">
                  <div className="max-w-2xl mx-auto">
                    <h2 className="premium-title text-2xl mb-4">Aucune analyse philosophique disponible</h2>
                    <p className="premium-text-secondary text-lg mb-8">
                      Générez votre première analyse personnalisée basée sur votre profil, vos tests de personnalité et vos réflexions.
                    </p>
                    <button
                      className="premium-button-primary px-8 py-3 text-lg"
                      onClick={handleGenerateFirstInsight}
                    >
                      Générer mon analyse philosophique
                    </button>
                  </div>
                </div>
              )}
              
              {insight && (
                <div className="space-y-8">
                  {/* 3D Card Section */}
                  <div className={styles.insightContainer}>
                    <div className={styles.cardInner}>
                      <div className={styles.cardFront}>
                        <p className="text-center px-4">{insight.preview}</p>
                      </div>
                      <div className={styles.cardBack}>
                        <p className="text-center px-4">{insight.if_you_accept}</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Main Content */}
                  <div className="premium-card p-6">
                    <button
                      className="premium-button-secondary mb-6"
                      onClick={() => setShowFullText(!showFullText)}
                    >
                      {showFullText ? 'Masquer le texte complet' : 'Afficher le texte complet'}
                    </button>
                    
                    {showFullText && (
                      <div className="mb-8">
                        <h2 className="premium-title text-xl mb-4">Texte complet</h2>
                        <div className="premium-text-primary text-base leading-relaxed whitespace-pre-wrap">
                          {insight.full_text}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Actions Section */}
                  <div className="premium-card p-6 space-y-6">
                    <div className="flex flex-wrap gap-4">
                      <button
                        className="premium-button-primary"
                        onClick={handleSaveInsight}
                        disabled={saving}
                      >
                        {saving ? 'Sauvegarde en cours...' : 'Sauvegarder cet insight'}
                      </button>
                      
                      <button
                        className="premium-button-secondary"
                        onClick={handleRegenerateInsight}
                        disabled={regenerating}
                      >
                        {regenerating ? 'Régénération en cours...' : 'Régénérer l\'insight'}
                      </button>
                    </div>
                    
                    <div>
                      <h3 className="premium-title text-lg mb-4">Vous souhaitez une perspective différente?</h3>
                      <textarea
                        className="premium-input w-full h-32 mb-4"
                        placeholder="Donnez votre feedback pour obtenir un insight réécrit..."
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                      />
                      <button
                        className="premium-button-accent"
                        onClick={handleRewriteInsight}
                        disabled={rewriting || !feedback}
                      >
                        {rewriting ? 'Réécriture en cours...' : 'Réécrire l\'insight'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default InsightPage;