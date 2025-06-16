'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './philosophical-card.module.css';

interface DailyQuestionCardProps {
  userId?: number;
}

const dailyQuestions = [
  "Qu'est-ce qui vous motive le plus dans votre parcours professionnel actuel ?",
  "Si vous pouviez changer une chose dans votre approche d'apprentissage, que serait-ce ?",
  "Quelle compétence aimeriez-vous développer cette semaine et pourquoi ?",
  "Comment définissez-vous le succès dans votre domaine d'études ?",
  "Quel conseil donneriez-vous à quelqu'un qui commence dans votre domaine ?",
  "Quelle est la plus grande leçon que vous avez apprise récemment ?",
  "Comment équilibrez-vous vos objectifs à court et long terme ?",
  "Qu'est-ce qui vous inspire le plus dans votre domaine d'études ?",
  "Comment gérez-vous les défis et les obstacles dans votre apprentissage ?",
  "Quelle habitude pourriez-vous adopter pour améliorer votre productivité ?",
];

const DailyQuestionCard: React.FC<DailyQuestionCardProps> = ({ userId = 1 }) => {
  const router = useRouter();
  const [question, setQuestion] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  
  useEffect(() => {
    // Generate a "daily" question based on the current date
    const today = new Date();
    const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    const questionIndex = dayOfYear % dailyQuestions.length;
    
    setTimeout(() => {
      setQuestion(dailyQuestions[questionIndex]);
      setLoading(false);
    }, 500);
  }, [userId]);
  
  const handleClick = () => {
    // Navigate to chat with the question as initial message
    const encodedQuestion = encodeURIComponent(question);
    router.push(`/chat?initial_message=${encodedQuestion}&type=daily_reflection`);
  };

  return (
    <div className={styles.container}>
      <div
        className={`${styles.card1} ${loading ? styles.loading : ''}`}
        onClick={handleClick}
        style={{ cursor: 'pointer' }}
      >
        <h3 className={styles.title}>💭 Question du jour</h3>
        <p className={styles.preview}>
          {loading ? "Préparation de votre question quotidienne..." : question}
        </p>
        {loading && (
          <div className={styles.loadingIndicator}>
            <span className={styles.dot}></span>
            <span className={styles.dot}></span>
            <span className={styles.dot}></span>
          </div>
        )}
        {!loading && (
          <div style={{ 
            marginTop: '12px', 
            fontSize: '12px', 
            color: 'rgba(255, 255, 255, 0.7)',
            fontStyle: 'italic'
          }}>
            Cliquez pour discuter avec l'IA
          </div>
        )}
      </div>
    </div>
  );
};

export default DailyQuestionCard;