'use client';
import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import UserCard from '@/components/ui/UserCard';
import ChallengeCard from '@/components/ui/ChallengeCard';
import XPProgress from '@/components/ui/XPProgress';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
export default function Home() {
  const router = useRouter();
  const [userData, setUserData] = useState({
    name: 'Philippe B.',
    role: 'Étudiant Msc. in Data Science',
    // level: 3,
    // Update the avatarUrl to a relative path that Next.js can serve
    avatarUrl: '/Avatar.PNG', // Ensure the image is in the public folder
    skills: ['UI Design', 'JavaScript', 'React', 'Node.js'],
    careerTreesExplored: 3,
    skillsInProgress: 12,
    totalXP: 250,
    careerTreeCompletion: 60,
    skillTreeCompletion: 40,
    badgesEarned: 5,
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

  // Données pour les suggestions d'actions
  const suggestedActions = [
    {
      title: 'Explorer Career Tree',
      icon: 'Tree',
      path: '/find-your-way'
    },
    {
      title: 'Commencer un nouveau défi',
      icon: 'Trophy',
      path: '/enhanced-skills'
    }
  ];

  // Fonction pour naviguer vers une page
  const navigateTo = (path: string) => {
    router.push(path);
  };

  return (
    <MainLayout showNav={false}>
      <div className="relative flex size-full min-h-screen flex-col bg-stitch-primary overflow-x-hidden">
        <div className="layout-container flex h-full grow flex-col">
          <div className="gap-1 px-6 flex flex-1 justify-center py-5">
            {/* Colonne de gauche - Profil utilisateur et navigation */}
            <div className="layout-content-container flex flex-col w-80">
              {/* Profil utilisateur */}
              <div className="flex p-4">
                <div className="flex w-full flex-col gap-4 items-center">
                  <div className="flex gap-4 flex-col items-center">
                    <div
                      className="bg-center bg-no-repeat aspect-square bg-cover rounded-full min-h-32 w-32 border-2 border-stitch-accent"
                      style={{ backgroundImage: `url("${userData.avatarUrl}")` }}
                    ></div>
                    <div className="flex flex-col items-center justify-center">
                      <p className="text-[22px] font-bold leading-tight tracking-[-0.015em] text-center font-departure text-stitch-accent">{userData.name}</p>
                      <p className="text-stitch-sage text-base font-normal leading-normal text-center">{userData.role}</p>
                      <p className="text-stitch-sage text-base font-normal leading-normal text-center">Niveau {userData.level}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation latérale avec icônes */}
              <div className="flex h-full min-h-[700px] flex-col justify-between p-4">
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col gap-2">
                    {/* Lien actif - Overview */}
                    <div className="flex items-center gap-3 px-3 py-2 rounded-full bg-[#eaf0ec]">
                      <div className="text-[#111814]">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path
                            d="M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0,1.14,1.14,0,0,0,.11.11l80,75.48A16,16,0,0,1,224,115.55Z"
                          ></path>
                        </svg>
                      </div>
                      <p className="text-[#111814] text-sm font-medium leading-normal">Accueil</p>
                    </div>

                    {/* Lien - Career Tree */}
                    <Link href="/find-your-way" className="flex items-center gap-3 px-3 py-2 hover:bg-[#eaf0ec] rounded-full transition-colors">
                      <div className="text-stitch-sage">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path
                            d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"
                          ></path>
                        </svg>
                      </div>
                      <p className="text-stitch-sage text-sm font-medium leading-normal">Career Tree</p>
                    </Link>

                    {/* Lien - Skills */}
                    <Link href="/enhanced-skills" className="flex items-center gap-3 px-3 py-2 hover:bg-[#eaf0ec] rounded-full transition-colors">
                      <div className="text-stitch-sage">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path
                            d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"
                          ></path>
                        </svg>
                      </div>
                      <p className="text-stitch-sage text-sm font-medium leading-normal">Compétences</p>
                    </Link>

                    {/* Lien - Challenges */}
                    <Link href="/space" className="flex items-center gap-3 px-3 py-2 hover:bg-[#eaf0ec] rounded-full transition-colors">
                      <div className="text-stitch-sage">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path
                            d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"
                          ></path>
                        </svg>
                      </div>
                      <p className="text-stitch-sage text-sm font-medium leading-normal">Défis</p>
                    </Link>

                    {/* Lien - Notes */}
                    <Link href="/space" className="flex items-center gap-3 px-3 py-2 hover:bg-[#eaf0ec] rounded-full transition-colors">
                      <div className="text-stitch-sage">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path
                            d="M88,96a8,8,0,0,1,8-8h64a8,8,0,0,1,0,16H96A8,8,0,0,1,88,96Zm8,40h64a8,8,0,0,0,0-16H96a8,8,0,0,0,0,16Zm32,16H96a8,8,0,0,0,0,16h32a8,8,0,0,0,0-16ZM224,48V156.69A15.86,15.86,0,0,1,219.31,168L168,219.31A15.86,15.86,0,0,1,156.69,224H48a16,16,0,0,1-16-16V48A16,16,0,0,1,48,32H208A16,16,0,0,1,224,48ZM48,208H152V160a8,8,0,0,1,8-8h48V48H48Zm120-40v28.7L196.69,168Z"
                          ></path>
                        </svg>
                      </div>
                      <p className="text-stitch-sage text-sm font-medium leading-normal">Notes</p>
                    </Link>

                    {/* Lien - Saved */}
                    <Link href="/space" className="flex items-center gap-3 px-3 py-2 hover:bg-[#eaf0ec] rounded-full transition-colors">
                      <div className="text-stitch-sage">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                          <path
                            d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,16V161.57l-51.77-32.35a8,8,0,0,0-8.48,0L72,161.56V48ZM132.23,177.22a8,8,0,0,0-8.48,0L72,209.57V180.43l56-35,56,35v29.14Z"
                          ></path>
                        </svg>
                      </div>
                      <p className="text-stitch-sage text-sm font-medium leading-normal">Sauvegardés</p>
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Colonne de droite - Contenu principal */}
            <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
              {/* En-tête */}
              <div className="flex flex-wrap justify-between gap-3 p-4">
                <p className="text-stitch-accent tracking-light text-[32px] font-bold leading-tight min-w-72 font-departure">Accueil</p>
              </div>

              {/* Résumé de l'étudiant */}
              <h2 className="text-stitch-accent text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5 font-departure">Résumé de l'étudiant</h2>
              <div className="flex flex-wrap gap-3 px-4 py-3">
                <div className="flex min-w-[111px] flex-1 basis-[fit-content] flex-col gap-2 rounded-lg border border-stitch-border p-3 items-start">
                  <p className="text-stitch-accent tracking-light text-2xl font-bold leading-tight font-departure">{userData.careerTreesExplored}</p>
                  <div className="flex items-center gap-2"><p className="text-stitch-sage text-sm font-normal leading-normal">Career Trees Explorés</p></div>
                </div>
                <div className="flex min-w-[111px] flex-1 basis-[fit-content] flex-col gap-2 rounded-lg border border-stitch-border p-3 items-start">
                  <p className="text-stitch-accent tracking-light text-2xl font-bold leading-tight font-departure">{userData.skillsInProgress}</p>
                  <div className="flex items-center gap-2"><p className="text-stitch-sage text-sm font-normal leading-normal">Compétences en cours</p></div>
                </div>
                <div className="flex min-w-[111px] flex-1 basis-[fit-content] flex-col gap-2 rounded-lg border border-stitch-border p-3 items-start">
                  <p className="text-stitch-accent tracking-light text-2xl font-bold leading-tight font-departure">{userData.totalXP}</p>
                  <div className="flex items-center gap-2"><p className="text-stitch-sage text-sm font-normal leading-normal">XP Total</p></div>
                </div>
              </div>

              {/* Points forts de progression */}
              <h2 className="text-stitch-accent text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5 font-departure">Points forts de progression</h2>
              <div className="flex flex-col gap-3 p-4">
                <div className="flex gap-6 justify-between">
                  <p className="text-stitch-sage text-base font-medium leading-normal">Progression Career Tree</p>
                  <p className="text-stitch-sage text-sm font-normal leading-normal">{userData.careerTreeCompletion}%</p>
                </div>
                <div className="rounded bg-stitch-track">
                  <div className="h-2 rounded bg-stitch-accent" style={{ width: `${userData.careerTreeCompletion}%` }}></div>
                </div>
              </div>
              <div className="flex flex-col gap-3 p-4">
                <div className="flex gap-6 justify-between">
                  <p className="text-stitch-sage text-base font-medium leading-normal">Progression Skill Tree</p>
                  <p className="text-stitch-sage text-sm font-normal leading-normal">{userData.skillTreeCompletion}%</p>
                </div>
                <div className="rounded bg-stitch-track">
                  <div className="h-2 rounded bg-stitch-accent" style={{ width: `${userData.skillTreeCompletion}%` }}></div>
                </div>
              </div>

              {/* Badges et XP */}
              <div className="flex items-center gap-4 bg-stitch-primary px-4 min-h-[72px] py-2">
                <div className="text-stitch-sage flex items-center justify-center rounded-lg bg-[#eaf0ec] shrink-0 size-12">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path
                      d="M216,96A88,88,0,1,0,72,163.83V240a8,8,0,0,0,11.58,7.16L128,225l44.43,22.21A8.07,8.07,0,0,0,176,248a8,8,0,0,0,8-8V163.83A87.85,87.85,0,0,0,216,96ZM56,96a72,72,0,1,1,72,72A72.08,72.08,0,0,1,56,96ZM168,227.06l-36.43-18.21a8,8,0,0,0-7.16,0L88,227.06V174.37a87.89,87.89,0,0,0,80,0ZM128,152A56,56,0,1,0,72,96,56.06,56.06,0,0,0,128,152Zm0-96A40,40,0,1,1,88,96,40,40,0,0,1,128,56Z"
                    ></path>
                  </svg>
                </div>
                <div className="flex flex-col justify-center">
                  <p className="text-stitch-accent text-base font-medium leading-normal line-clamp-1">Badges Gagnés</p>
                  <p className="text-stitch-sage text-sm font-normal leading-normal line-clamp-2">Complété {userData.badgesEarned} défis</p>
                </div>
              </div>
              <div className="flex items-center gap-4 bg-stitch-primary px-4 min-h-[72px] py-2">
                <div className="text-stitch-sage flex items-center justify-center rounded-lg bg-[#eaf0ec] shrink-0 size-12">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                    <path
                      d="M239.2,97.29a16,16,0,0,0-13.81-11L166,81.17,142.72,25.81h0a15.95,15.95,0,0,0-29.44,0L90.07,81.17,30.61,86.32a16,16,0,0,0-9.11,28.06L66.61,153.8,53.09,212.34a16,16,0,0,0,23.84,17.34l51-31,51.11,31a16,16,0,0,0,23.84-17.34l-13.51-58.6,45.1-39.36A16,16,0,0,0,239.2,97.29Zm-15.22,5-45.1,39.36a16,16,0,0,0-5.08,15.71L187.35,216v0l-51.07-31a15.9,15.9,0,0,0-16.54,0l-51,31h0L82.2,157.4a16,16,0,0,0-5.08-15.71L32,102.35a.37.37,0,0,1,0-.09l59.44-5.14a16,16,0,0,0,13.35-9.75L128,32.08l23.2,55.29a16,16,0,0,0,13.35,9.75L224,102.26S224,102.32,224,102.33Z"
                    ></path>
                  </svg>
                </div>
                <div className="flex flex-col justify-center">
                  <p className="text-stitch-accent text-base font-medium leading-normal line-clamp-1">XP Gagné</p>
                  <p className="text-stitch-sage text-sm font-normal leading-normal line-clamp-2">Gagné {userData.totalXP} XP</p>
                </div>
              </div>

              {/* Suggestions d'actions */}
              <h2 className="text-stitch-accent text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5 font-departure">Actions suggérées</h2>
              {suggestedActions.map((action, index) => (
                <div
                  key={index}
                  className="flex items-center gap-4 bg-stitch-primary px-4 min-h-14 cursor-pointer hover:bg-[#eaf0ec] transition-colors"
                  onClick={() => navigateTo(action.path)}
                >
                  <div className="text-stitch-sage flex items-center justify-center rounded-lg bg-[#eaf0ec] shrink-0 size-10">
                    {action.icon === 'Tree' ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                        <path
                          d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"
                        ></path>
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                        <path
                          d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"
                        ></path>
                      </svg>
                    )}
                  </div>
                  <p className="text-stitch-sage text-base font-normal leading-normal flex-1 truncate">{action.title}</p>
                </div>
              ))}

              {/* Activité récente */}
              <h2 className="text-stitch-accent text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5 font-departure">Activité récente</h2>
              {userData.recentActivities.map((activity, index) => (
                <div key={index} className="flex items-center gap-4 bg-stitch-primary px-4 min-h-[72px] py-2">
                  <div className="text-stitch-sage flex items-center justify-center rounded-lg bg-[#eaf0ec] shrink-0 size-12">
                    {activity.icon === 'CheckCircle' ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                        <path
                          d="M173.66,98.34a8,8,0,0,1,0,11.32l-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35A8,8,0,0,1,173.66,98.34ZM232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"
                        ></path>
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                        <path
                          d="M239.2,97.29a16,16,0,0,0-13.81-11L166,81.17,142.72,25.81h0a15.95,15.95,0,0,0-29.44,0L90.07,81.17,30.61,86.32a16,16,0,0,0-9.11,28.06L66.61,153.8,53.09,212.34a16,16,0,0,0,23.84,17.34l51-31,51.11,31a16,16,0,0,0,23.84-17.34l-13.51-58.6,45.1-39.36A16,16,0,0,0,239.2,97.29Zm-15.22,5-45.1,39.36a16,16,0,0,0-5.08,15.71L187.35,216v0l-51.07-31a15.9,15.9,0,0,0-16.54,0l-51,31h0L82.2,157.4a16,16,0,0,0-5.08-15.71L32,102.35a.37.37,0,0,1,0-.09l59.44-5.14a16,16,0,0,0,13.35-9.75L128,32.08l23.2,55.29a16,16,0,0,0,13.35,9.75L224,102.26S224,102.32,224,102.33Z"
                        ></path>
                      </svg>
                    )}
                  </div>
                  <div className="flex flex-col justify-center">
                    <p className="text-stitch-accent text-base font-medium leading-normal line-clamp-1">{activity.title}</p>
                    <p className="text-stitch-sage text-sm font-normal leading-normal line-clamp-2">{activity.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}