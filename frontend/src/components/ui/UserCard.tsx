'use client';
import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import styles from '@/styles/card.module.css';
import { ScoreResponse } from '@/services/hollandTestService';
import AvatarService, { AvatarData } from '@/services/avatarService';

interface UserCardProps {
  name: string;
  role: string;
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
  skills,
  className,
  hollandResults,
  loading,
  error
}) => {
  const router = useRouter();
  const [avatarData, setAvatarData] = useState<AvatarData | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(true);

  // Charger l'avatar de l'utilisateur
  useEffect(() => {
    const loadAvatar = async () => {
      try {
        setAvatarLoading(true);
        const data = await AvatarService.getUserAvatar();
        setAvatarData(data);
      } catch (err) {
        console.log('Aucun avatar trouvé pour cet utilisateur');
        setAvatarData(null);
      } finally {
        setAvatarLoading(false);
      }
    };

    loadAvatar();
  }, []);

  const handleProfileClick = () => {
    router.push('/profile_avatar');
  };

  const avatarImageUrl = avatarData?.avatar_image_url
    ? AvatarService.getAvatarImageUrl(avatarData.avatar_image_url)
    : null;

  return (
    <div className={`${styles.card} ${className || ''}`}>
      <div className={styles.card__img} />
      
      {/* Avatar Section */}
      <div className={styles.card__avatar}>
        {avatarLoading ? (
          <div className={styles.avatar__loading}>
            <div className={styles.avatar__spinner}></div>
          </div>
        ) : avatarImageUrl ? (
          <div className={styles.avatar__container}>
            <Image
              src={avatarImageUrl}
              alt={avatarData?.avatar_name || name}
              width={200}
              height={200}
              className={styles.avatar__image}
            />
            <div className={styles.avatar__glow}></div>
          </div>
        ) : (
          <div className={styles.avatar__placeholder}>
            <svg
              width="80"
              height="80"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/>
              <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="2"/>
            </svg>
            <p className={styles.avatar__placeholder_text}>Générer Avatar</p>
          </div>
        )}
      </div>

      <h2 className={styles.card__title}>{avatarData?.avatar_name || name}</h2>
      <p className={styles.card__subtitle}>{role}</p>
      
      {/* Avatar Description */}
      {avatarData?.avatar_description && (
        <p className={styles.card__description}>{avatarData.avatar_description}</p>
      )}
      
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
      
      <button className={styles.card__btn} onClick={handleProfileClick}>
        {avatarData ? 'Voir Profil' : 'Créer Avatar'}
      </button>
    </div>
  );
};

export default UserCard;ame={styles.card__btn} onClick={handleProfileClick}>
            Profile
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserCard;