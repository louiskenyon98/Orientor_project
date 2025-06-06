'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import UserCard from '@/components/ui/UserCard';
import PhilosophicalCard from '@/components/ui/PhilosophicalCard';
import StarConstellation from '@/components/ui/StarConstellation';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { getJobRecommendations } from '@/services/api';
import JobRecommendationList from '@/components/jobs/JobRecommendationList';
import JobSkillsTree from '@/components/jobs/JobSkillsTree';
import { Job } from '@/components/jobs/JobCard';
import styles from '@/styles/patterns.module.css';
import sidebarStyles from '@/styles/sidebar.module.css';
import NewSidebar from '@/components/layout/NewSidebar';
import '@/styles/premium-theme.css';
import PersonalityCard from '@/components/ui/PersonalityCard';

// Interface pour la réponse de l'API de recommandations d'emploi
interface JobRecommendationsResponse {
  recommendations: Job[];
  user_id: number;
}

export default function Home() {
  const router = useRouter();
  const [userData] = useState({
    name: 'Philippe B.',
    role: 'Étudiant Msc. in Data Science',
    level: 3,
    avatarUrl: '/Avatar.PNG',
    skills: ['UI Design', 'JavaScript', 'React', 'Node.js'],
    careerTreesExplored: 3,
    skillsInProgress: 12,
    totalXP: 250,
    careerTreeCompletion: 60,
    skillTreeCompletion: 40,
    badgesEarned: 5,
    challengesCompleted: 8,
    notesSaved: 15,
    recentActivities: [
      {
        type: 'challenge',
        title: 'Challenge Complété',
        description: "Complété challenge: 'Data Analysis Basics'",
        icon: 'CheckCircle'
      },
      {
        type: 'xp',
        title: 'XP Gagné',
        description: 'Gagné 250 XP',
        icon: 'Star'
      }
    ]
  });

  // État pour stocker les résultats du test Holland (RIASEC)
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // États pour les recommandations d'emploi
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);

  // Récupérer les résultats du test Holland au chargement de la page
  useEffect(() => {
    const fetchHollandResults = async () => {
      try {
        const results = await hollandTestService.getUserLatestResults();
        setHollandResults(results);
      } catch (err) {
        console.error('Erreur lors de la récupération des résultats RIASEC:', err);
        setError('Impossible de récupérer les résultats RIASEC');
      } finally {
        setLoading(false);
      }
    };

    fetchHollandResults();
    
    // Récupérer les recommandations d'emploi
    const fetchJobRecommendations = async () => {
      try {
        setJobsLoading(true);
        setJobsError(null);
        
        // Utiliser l'ID de l'utilisateur actuel (à adapter selon votre système d'authentification)
        const response = await getJobRecommendations() as JobRecommendationsResponse;
        
        if (response && response.recommendations) {
          setJobRecommendations(response.recommendations);
          
          // Sélectionner automatiquement le premier emploi
          if (response.recommendations.length > 0) {
            setSelectedJob(response.recommendations[0]);
          }
        }
      } catch (err) {
        console.error('Erreur lors de la récupération des recommandations d\'emploi:', err);
        setJobsError('Impossible de récupérer les recommandations d\'emploi');
      } finally {
        setJobsLoading(false);
      }
    };
    
    fetchJobRecommendations();
  }, []);
  
  // Fonction pour gérer la sélection d'un emploi
  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  // Définir les couleurs pour chaque dimension RIASEC
  const riasecColors = {
    R: 'rgba(255, 99, 132, 0.7)',   // Rouge
    I: 'rgba(54, 162, 235, 0.7)',    // Bleu
    A: 'rgba(255, 206, 86, 0.7)',    // Jaune
    S: 'rgba(75, 192, 192, 0.7)',    // Vert
    E: 'rgba(153, 102, 255, 0.7)',   // Violet
    C: 'rgba(255, 159, 64, 0.7)',    // Orange
  };

  // Définir les descriptions courtes pour chaque dimension RIASEC
  const riasecLabels = {
    R: 'Réaliste',
    I: 'Investigateur',
    A: 'Artistique',
    S: 'Social',
    E: 'Entreprenant',
    C: 'Conventionnel',
  };

  // Navigation items pour la sidebar
  const navItems = [
    { name: 'Chat', icon: 'Chat', path: '/chat' },
    { name: 'Peers', icon: 'Peers', path: '/peers' },
    { name: 'Swipe', icon: 'Swipe', path: '/find-your-way' },
    { name: 'Saved', icon: 'Bookmark', path: '/space' },
    { name: 'Challenges', icon: 'Trophy', path: '/challenges' },
    { name: 'Notes', icon: 'Note', path: '/notes' },
    { name: 'Case Study', icon: 'Case Study', path: '/case-study-journey' },
    { name: 'Competence Tree', icon: 'Tree', path: '/competence-tree' },
  ];

  // Career navigation items
  const careerItems = [
    { name: 'Career Search', icon: 'List', path: '/vector-search' },
    { name: 'Skills Tree', icon: 'Tree', path: '/enhanced-skills' },
    { name: 'Career Tree', icon: 'Tree', path: '/career' },
    { name: 'Competence Tree', icon: 'Tree', path: '/competence-tree' },
    { name: 'Saved Tree', icon: 'Tree', path: '/tree-path' },
  ];

  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'HEXACO Test', icon: 'Brain', path: '/hexaco-test/select' },
    { name: 'Self-Reflection', icon: 'Reflection', path: '/self-reflection' },
    { name: 'Holland Results', icon: 'Personality', path: '/profile/holland-results' },
    { name: 'HEXACO Results', icon: 'Brain', path: '/profile/hexaco-results' },
  ];

  const navigateTo = (path: string) => {
    router.push(path);
  };

  return (
    <MainLayout showNav={false}>
      <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
        {/* Animated Star Constellation Background */}
        <StarConstellation />
        
        <div className="relative z-10 w-full flex h-full grow">
          {/* New Sidebar */}
          <NewSidebar navItems={navItems} />

          {/* Main Content */}
          <div className="flex flex-col flex-1 w-full ml-20">
            {/* Header */}
            <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
              <h1 className="premium-title text-[32px] md:text-4xl font-bold leading-tight min-w-72">
                Accueil
              </h1>
            </div>

            {/* Main Content Container */}
            <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
              {/* User Profile Section - Avatar et RIASEC */}
              <div className="mb-10">
                {/* Unified flex container for the entire profile section */}
                <div className="flex flex-col gap-8">
                  {/* Avatar Section - Centered and Larger */}
                  <div className="w-full max-w-[400px] mx-auto">
                    <UserCard
                      name={userData.name}
                      role={userData.role}
                      avatarUrl={userData.avatarUrl}
                      skills={userData.skills}
                      hollandResults={hollandResults}
                      loading={loading}
                      error={error}
                      className="premium-card p-6 w-full"
                    />
                  </div>
                </div>
              </div>

              {/* Cards Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                {/* Philosophical Card */}
                <div>
                  <PhilosophicalCard />
                </div>

                {/* Personality Card */}
                <div className="premium-card p-6">
                  <h2 className="premium-section-title mb-6">
                    Personality Tests
                  </h2>
                  <PersonalityCard items={personalityItems} />
                </div>
              </div>

              {/* Section des recommandations d'emploi - occupe toute la largeur */}
              <div className="md:col-span-12 mt-8">
                <h2 className="premium-section-title">
                  Recommandations d'emploi
                </h2>
                <div className="w-full overflow-hidden">
                  <div className="max-w-[1400px] mx-auto">
                    <JobRecommendationList
                      recommendations={jobRecommendations}
                      isLoading={jobsLoading}
                      error={jobsError}
                      onSelectJob={handleSelectJob}
                      className="mb-8"
                    />
                  </div>
                  
                  {/* Arbre de compétences pour l'emploi sélectionné */}
                  {selectedJob && (
                    <div className="premium-card p-6 mt-8">
                      <JobSkillsTree
                        jobId={selectedJob.id}
                        className="mt-8"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Dashboard Grid - responsive avec largeur complète et optimisé pour grands écrans */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8">
                {/* Student Summary - occupe toute la largeur sur mobile, 8 colonnes sur desktop */}
                <div className="md:col-span-8">
                  <h2 className="premium-section-title">
                    Résumé de l'étudiant
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-6">
                    <div className="premium-card premium-card-uniform flex flex-col gap-2 p-4 md:p-5 items-start">
                      <p className="premium-stats-number">{userData.careerTreesExplored}</p>
                      <div className="flex items-center gap-2">
                        <p className="premium-stats-label">Career Trees Explorés</p>
                      </div>
                    </div>
                    <div className="premium-card premium-card-uniform flex flex-col gap-2 p-4 md:p-5 items-start">
                      <p className="premium-stats-number">{userData.skillsInProgress}</p>
                      <div className="flex items-center gap-2">
                        <p className="premium-stats-label">Compétences en cours</p>
                      </div>
                    </div>
                    <div className="premium-card premium-card-uniform flex flex-col gap-2 p-4 md:p-5 items-start">
                      <p className="premium-stats-number">{userData.totalXP}</p>
                      <div className="flex items-center gap-2">
                        <p className="premium-stats-label">XP Total</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Stats supplémentaires - visible uniquement sur desktop, 4 colonnes */}
                {/* <div className="hidden md:block md:col-span-4">
                  <h2 className="text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Statistiques</h2>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.challengesCompleted}</p>
                      <div className="flex items-center gap-2"><p className="text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>Défis complétés</p></div>
                    </div>
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.notesSaved}</p>
                      <div className="flex items-center gap-2"><p className="text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>Notes sauvegardées</p></div>
                    </div>
                  </div>
                </div> */}

                {/* How to get there? Section */}
                <div className="md:col-span-12 mt-4">
                  <h2 className="premium-section-title">
                    Tree
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mb-6">
                    {careerItems.map((item, index) => (
                      <Link
                        key={index}
                        href={item.path}
                        className="premium-nav-card flex items-center gap-4 p-5 transition-colors"
                      >
                        <div className="premium-nav-icon premium-icon">
                          {item.icon === 'Tree' && (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                            </svg>
                          )}
                          {item.icon === 'List' && (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"></path>
                            </svg>
                          )}
                        </div>
                        <div className="flex flex-col">
                          <p className="premium-text text-lg font-medium">{item.name}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>

                {/* Personality Section */}
                {/* <div className="md:col-span-12 mt-4">
                  <h2 className="premium-section-title">
                    Personality
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
                    {personalityItems.map((item, index) => (
                      <Link
                        key={index}
                        href={item.path}
                        className="premium-nav-card flex items-center gap-4 p-5 transition-colors"
                      >
                        <div className="premium-nav-icon premium-icon">
                          {item.icon === 'Brain' ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M174,232a8,8,0,0,1-8,8H90a8,8,0,0,1,0-16h76A8,8,0,0,1,174,232ZM224,104a87.51,87.51,0,0,1-33.64,69.21A16.24,16.24,0,0,0,184,187.5c0,2.7.14,5.06.42,7.58.78,7.06,1.58,14.37-1.28,20.65A16,16,0,0,1,168,224H88a16,16,0,0,1-15.14-21.77c-2.86-6.28-2.06-13.59-1.28-20.65.28-2.52.42-4.88.42-7.58a16.24,16.24,0,0,0-6.36-14.29A87.51,87.51,0,0,1,32,104c0-48.6,43.85-88,96-88s96,39.4,96,88Zm-16,0c0-39.4-35.33-72-80-72S48,64.6,48,104a71.64,71.64,0,0,0,27.84,56.33A32.3,32.3,0,0,1,88,187.5c0,4.06-.15,7.52-.46,10.5-.62,5.48-1.12,9.87.21,11.15a.61.61,0,0,0,.25.35h80a.61.61,0,0,0,.25-.35c1.33-1.28.83-5.67.21-11.15-.31-3-.46-6.44-.46-10.5a32.3,32.3,0,0,1,12.16-27.17A71.64,71.64,0,0,0,208,104ZM140,80a12,12,0,1,0-12,12A12,12,0,0,0,140,80Zm-56,0a12,12,0,1,0,12,12A12,12,0,0,0,84,80Zm72,48a8,8,0,0,0-8-8c-13.23,0-24-9-24-20a8,8,0,0,0-16,0c0,11-10.77,20-24,20a8,8,0,0,0,0,16c13.23,0,24,9,24,20a8,8,0,0,0,16,0c0-11,10.77-20,24-20A8,8,0,0,0,156,128Z"></path>
                            </svg>
                          ) : item.icon === 'Reflection' ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216V88H40ZM40,200V104H216v96H40Zm32-80a8,8,0,0,1,8-8h96a8,8,0,0,1,0,16H80A8,8,0,0,1,72,120Zm0,32a8,8,0,0,1,8-8h96a8,8,0,0,1,0,16H80A8,8,0,0,1,72,152Zm0,32a8,8,0,0,1,8-8h64a8,8,0,0,1,0,16H80A8,8,0,0,1,72,184Z"></path>
                            </svg>
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24ZM74.08,197.5a64,64,0,0,1,107.84,0,87.83,87.83,0,0,1-107.84,0ZM96,120a32,32,0,1,1,32,32A32,32,0,0,1,96,120Zm97.76,66.41a79.66,79.66,0,0,0-36.06-28.75,48,48,0,1,0-59.4,0,79.66,79.66,0,0,0-36.06,28.75,88,88,0,1,1,131.52,0Z"></path>
                            </svg>
                          )}
                        </div>
                        <div className="flex flex-col">
                          <p className="premium-text text-lg font-medium">{item.name}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div> */}

                {/* Recent Activity - occupe toute la largeur */}
                <div className="md:col-span-12 mt-4">
                  <h2 className="premium-section-title">
                    Activité récente
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8">
                    {userData.recentActivities.map((activity, index) => (
                      <div key={index} className="premium-activity-card flex items-center gap-4 p-5 md:p-6">
                        <div className="premium-nav-icon premium-icon flex items-center justify-center shrink-0 size-12 md:size-14">
                          {activity.icon === 'CheckCircle' ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M173.66,98.34a8,8,0,0,1,0,11.32l-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35A8,8,0,0,1,173.66,98.34ZM232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"></path>
                            </svg>
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="text-white">
                              <path d="M239.2,97.29a16,16,0,0,0-13.81-11L166,81.17,142.72,25.81h0a15.95,15.95,0,0,0-29.44,0L90.07,81.17,30.61,86.32a16,16,0,0,0-9.11,28.06L66.61,153.8,53.09,212.34a16,16,0,0,0,23.84,17.34l51-31,51.11,31a16,16,0,0,0,23.84-17.34l-13.51-58.6,45.1-39.36A16,16,0,0,0,239.2,97.29Zm-15.22,5-45.1,39.36a16,16,0,0,0-5.08,15.71L187.35,216v0l-51.07-31a15.9,15.9,0,0,0-16.54,0l-51,31h0L82.2,157.4a16,16,0,0,0-5.08-15.71L32,102.35a.37.37,0,0,1,0-.09l59.44-5.14a16,16,0,0,0,13.35-9.75L128,32.08l23.2,55.29a16,16,0,0,0,13.35,9.75L224,102.26S224,102.32,224,102.33Z"></path>
                            </svg>
                          )}
                        </div>
                        <div className="flex flex-col justify-center w-full">
                          <p className="premium-text text-base md:text-lg font-medium leading-normal line-clamp-1 break-words">
                            {activity.title}
                          </p>
                          <p className="premium-text-secondary text-sm md:text-base font-normal leading-normal line-clamp-2 break-words">
                            {activity.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}