import React from 'react';
import styles from './CareerProgress.module.css';

interface CareerProgressProps {
  progressData: {
    pathways: {
      name: string;
      completion: number;
      badges: string[];
      xp: number;
    }[];
  };
}

const CareerProgress: React.FC<CareerProgressProps> = ({ progressData }) => {
  return (
    <div className={styles.progressContainer}>
      {/* Pathway Progress Cards */}
      <div className={styles.pathwayCards}>
        {progressData.pathways.map((pathway) => (
          <div key={pathway.name} className={styles.pathwayCard}>
            <h3 className={styles.pathwayTitle}>{pathway.name}</h3>
            <div className={styles.progressBar}>
              <div 
                className={styles.progressFill}
                style={{ width: `${pathway.completion}%` }}
              ></div>
            </div>
            <div className={styles.stats}>
              <span>{pathway.completion}% Complete</span>
              <span>{pathway.xp} XP Earned</span>
            </div>
            {/* Badges */}
            <div className={styles.badges}>
              {pathway.badges.map((badge, index) => (
                <span key={index} className={styles.badge}>
                  {badge}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Pathway Visualization */}
      <div className={`${styles.pathwayMap} ${styles.loading}`}>
        {/* TODO: Add SVG/Canvas-based pathway visualization here */}
        <div className={styles.placeholder}>
          Career Pathway Map Loading...
        </div>
      </div>
    </div>
  );
};

export default CareerProgress;
