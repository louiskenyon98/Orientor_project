'use client';
import React from 'react';
import Image from 'next/image';
import styles from '@/styles/card.module.css';
import { ScoreResponse } from '@/services/hollandTestService';

interface UserCardProps {
  name: string;
  role: string;
  avatarUrl: string;
  skills: string[];
  className?: string;
  hollandResults?: ScoreResponse | null;
  loading?: boolean;
  error?: string | null;
}

const riasecColors = {
  R: 'rgba(255, 99, 132, 0.7)',   // Rouge
  I: 'rgba(54, 162, 235, 0.7)',    // Bleu
  A: 'rgba(255, 206, 86, 0.7)',    // Jaune
  S: 'rgba(75, 192, 192, 0.7)',    // Vert
  E: 'rgba(153, 102, 255, 0.7)',   // Violet
  C: 'rgba(255, 159, 64, 0.7)',    // Orange
};

const riasecLabels = {
  R: 'Réaliste',
  I: 'Investigateur',
  A: 'Artistique',
  S: 'Social',
  E: 'Entreprenant',
  C: 'Conventionnel',
};

const UserCard: React.FC<UserCardProps> = ({ 
  name, 
  role, 
  avatarUrl, 
  skills, 
  className,
  hollandResults,
  loading,
  error 
}) => {
  return (
    <div className={`${styles.card} ${className || ''}`}>
      <div className={styles.card__img} />
      <div className={styles.card__avatar}>
        <Image
          src={avatarUrl}
          alt={name}
          width={200}
          height={200}
          className="rounded-full"
        />
      </div>
      <h2 className={styles.card__title}>{name}</h2>
      <p className={styles.card__subtitle}>{role}</p>
      
      {/* RIASEC Profile Section */}
      {loading ? (
        <p className={styles.card__subtitle}>Chargement du profil RIASEC...</p>
      ) : error ? (
        <p className={styles.card__subtitle} style={{ color: 'red' }}>{error}</p>
      ) : hollandResults ? (
        <div className={styles.card__riasec}>
          <div className={styles.card__riasec_codes}>
            {hollandResults.top_3_code.split('').map((letter, index) => (
              <div
                key={index}
                className={styles.card__riasec_code}
                style={{ backgroundColor: riasecColors[letter as keyof typeof riasecColors] }}
              >
                {letter}
              </div>
            ))}
          </div>
          <p className={styles.card__riasec_label}>
            {riasecLabels[hollandResults.top_3_code[0] as keyof typeof riasecLabels]}
          </p>
        </div>
      ) : (
        <p className={styles.card__subtitle}>Pas de profil RIASEC</p>
      )}
      
      <button className={styles.card__btn}>Profile</button>
    </div>
  );
};

export default UserCard;