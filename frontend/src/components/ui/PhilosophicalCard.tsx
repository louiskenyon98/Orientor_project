'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './philosophical-card.module.css';
import { getInsight, generateInsight, mockInsightData } from '@/services/insightService';

interface PhilosophicalCardProps {
  previewText?: string;
  userId?: number;
}

const PhilosophicalCard: React.FC<PhilosophicalCardProps> = ({ previewText, userId = 1 }) => {
  const router = useRouter();
  const [preview, setPreview] = useState<string>(previewText || "Chargement de votre insight philosophique...");
  const [loading, setLoading] = useState<boolean>(!previewText);
  
  useEffect(() => {
    if (previewText) {
      setPreview(previewText);
      setLoading(false);
      return;
    }
    
    const fetchInsightPreview = async () => {
      try {
        if (process.env.NODE_ENV === 'development') {
          setTimeout(() => {
            setPreview(mockInsightData.preview);
            setLoading(false);
          }, 1000);
          return;
        }
        
        try {
          const existingInsight = await getInsight();
          setPreview(existingInsight.preview);
        } catch (getError) {
          console.log('Aucun insight existant trouvé');
          setPreview("Cliquez pour générer votre première analyse philosophique personnalisée...");
        }
      } catch (error) {
        console.error('Erreur lors du chargement de l\'aperçu de l\'insight:', error);
        setPreview("Explorez des perspectives philosophiques qui élargissent votre vision du monde et stimulent votre réflexion critique...");
      } finally {
        setLoading(false);
      }
    };
    
    fetchInsightPreview();
  }, [previewText, userId]);
  
  const handleClick = () => {
    router.push('/insight');
  };

  return (
    <div className={styles.container}>
      <div
        className={`${styles.card1} ${loading ? styles.loading : ''}`}
        onClick={handleClick}
      >
        <h3 className={styles.title}>🧠 Personalité</h3>
        <p className={styles.preview}>
          {preview}
        </p>
        {loading && (
          <div className={styles.loadingIndicator}>
            <span className={styles.dot}></span>
            <span className={styles.dot}></span>
            <span className={styles.dot}></span>
          </div>
        )}
      </div>
    </div>
  );
};

export default PhilosophicalCard;