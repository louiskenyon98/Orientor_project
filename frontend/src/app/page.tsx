'use client';

import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

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

  // Navigation items pour la sidebar
  const navItems = [
    { name: 'Overview', icon: 'Home', path: '/', active: true },
    { name: 'Chat', icon: 'Chat', path: '/chat' },
    { name: 'Swipe', icon: 'List', path: '/find-your-way' },
    { name: 'Career Tree', icon: 'Tree', path: '/career' },
    { name: 'Skills Tree', icon: 'Tree', path: '/enhanced-skills' },
    { name: 'Challenges', icon: 'Trophy', path: '/challenges' },
    { name: 'Saved', icon: 'Bookmark', path: '/space' },
    { name: 'peers', icon: 'List', path: '/peers' },
    { name: 'Career Search', icon: 'List', path: '/vector-search' },
    { name: 'Notes', icon: 'Note', path: '/notes' },
    { name: 'Holland Test', icon: 'List', path: '/holland-test' },
    { name: 'Case Study', icon: 'List', path: '/case-study-journey' },
    { name: 'Profile', icon: 'Settings', path: '/profile' },
    { name: 'Personality', icon: 'List', path: '/profile/holland-results' }
  ];

  // Actions suggérées
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

  const navigateTo = (path: string) => {
    router.push(path);
  };

  return (
    <MainLayout showNav={false}>
      <div className="relative flex size-full min-h-screen flex-col bg-stitch-primary overflow-x-hidden">
        <div className="flex h-full grow">
          {/* Sidebar - étroite sur mobile, plus large sur desktop */}
          <div className="w-16 md:w-64 border-r border-stitch-border transition-all duration-300">
            <div className="flex flex-col gap-6 items-center md:items-start pt-8 px-2 md:px-6">
              {/* Logo/Titre - visible uniquement sur desktop */}
              <div className="hidden md:flex items-center mb-6">
                <h1 className="text-stitch-accent text-2xl font-bold font-departure">Navigo</h1>
              </div>

              {/* Navigation Items */}
              {navItems.map((item, index) => (
                <Link href={item.path} key={index} className="relative group w-full">
                  <div className={`flex items-center justify-center md:justify-start w-12 h-12 md:w-full md:h-14 rounded-lg 
                    ${item.active ? 'bg-[#eaf0ec] text-[#111814]' : 'hover:bg-[#eaf0ec] text-stitch-sage hover:text-[#111814]'} 
                    transition-colors md:px-4`}>
                    
                    {/* Icon */}
                    {item.icon === 'Home' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0,1.14,1.14,0,0,0,.11.11l80,75.48A16,16,0,0,1,224,115.55Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Tree' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                      </svg>
                    )}
                    {item.icon === 'List' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Trophy' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Note' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Bookmark' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,177.57-51.77-32.35a8,8,0,0,0-8.48,0L72,209.57V48H184Z"></path>
                      </svg>
                    )}
                    
                    {/* Label - visible uniquement sur desktop */}
                    <span className="hidden md:block ml-3 text-base font-medium">{item.name}</span>
                    
                    {/* Tooltip - visible uniquement sur mobile */}
                    <span className="absolute left-full ml-2 px-2 py-1 bg-stitch-primary text-stitch-sage text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap md:hidden">
                      {item.name}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Main Content - adapté pour desktop */}
          <div className="layout-content-container flex flex-col flex-1 md:max-w-none">
            {/* Header */}
            <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6">
              <p className="text-stitch-accent tracking-light text-[32px] md:text-4xl font-bold leading-tight min-w-72 font-departure">Accueil</p>
              
              {/* User Profile - visible uniquement sur desktop */}
              <div className="hidden md:flex items-center gap-4">
                <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-stitch-accent">
                  <img src={userData.avatarUrl} alt="Profile" className="w-full h-full object-cover" />
                </div>
                <div>
                  <p className="text-stitch-accent font-bold">{userData.name}</p>
                  <p className="text-stitch-sage text-sm">{userData.role}</p>
                </div>
              </div>
            </div>

            {/* Dashboard Grid - responsive */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-6 px-4 md:px-6">
              {/* Student Summary - occupe toute la largeur sur mobile, 8 colonnes sur desktop */}
              <div className="md:col-span-8">
                <h2 className="text-stitch-accent text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5 font-departure">Résumé de l'étudiant</h2>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
                  <div className="flex flex-col gap-2 rounded-lg border border-stitch-border p-3 md:p-4 items-start">
                    <p className="text-stitch-accent tracking-light text-2xl md:text-3xl font-bold leading-tight font-departure">{userData.careerTreesExplored}</p>
                    <div className="flex items-center gap-2"><p className="text-stitch-sage text-sm md:text-base font-normal leading-normal">Career Trees Explorés</p></div>
                  </div>
                  <div className="flex flex-col gap-2 rounded-lg border border-stitch-border p-3 md:p-4 items-start">
                    <p className="text-stitch-accent tracking-light text-2xl md:text-3xl font-bold leading-tight font-departure">{userData.skillsInProgress}</p>
                    <div className="flex items-center gap-2"><p className="text-stitch-sage text-sm md:text-base font-normal leading-normal">Compétences en cours</p></div>
                  </div>
                  <div className="flex flex-col gap-2 rounded-lg border border-stitch-border p-3 md:p-4 items-start">
                    <p className="text-stitch-accent tracking-light text-2xl md:text-3xl font-bold leading-tight font-departure">{userData.totalXP}</p>
                    <div className="flex items-center gap-2"><p className="text-stitch-sage text-sm md:text-base font-normal leading-normal">XP Total</p></div>
                  </div>
                </div>
              </div>

              {/* Stats supplémentaires - visible uniquement sur desktop, 4 colonnes */}
              <div className="hidden md:block md:col-span-4">
                <h2 className="text-stitch-accent text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5 font-departure">Statistiques</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-2 rounded-lg border border-stitch-border p-4 items-start">
                    <p className="text-stitch-accent tracking-light text-3xl font-bold leading-tight font-departure">{userData.challengesCompleted}</p>
                    <div className="flex items-center gap-2"><p className="text-stitch-sage text-base font-normal leading-normal">Défis complétés</p></div>
                  </div>
                  <div className="flex flex-col gap-2 rounded-lg border border-stitch-border p-4 items-start">
                    <p className="text-stitch-accent tracking-light text-3xl font-bold leading-tight font-departure">{userData.notesSaved}</p>
                    <div className="flex items-center gap-2"><p className="text-stitch-sage text-base font-normal leading-normal">Notes sauvegardées</p></div>
                  </div>
                </div>
              </div>

              {/* Progress Points - occupe toute la largeur sur mobile, 8 colonnes sur desktop */}
              <div className="md:col-span-8">
                <h2 className="text-stitch-accent text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5 font-departure">Points forts de progression</h2>
                <div className="space-y-4 md:space-y-6">
                  <div className="flex flex-col gap-3">
                    <div className="flex gap-6 justify-between">
                      <p className="text-stitch-sage text-base font-medium leading-normal">Progression Career Tree</p>
                      <p className="text-stitch-sage text-sm font-normal leading-normal">{userData.careerTreeCompletion}%</p>
                    </div>
                    <div className="rounded bg-stitch-track">
                      <div className="h-2 md:h-3 rounded bg-stitch-accent" style={{ width: `${userData.careerTreeCompletion}%` }}></div>
                    </div>
                  </div>
                  <div className="flex flex-col gap-3">
                    <div className="flex gap-6 justify-between">
                      <p className="text-stitch-sage text-base font-medium leading-normal">Progression Skill Tree</p>
                      <p className="text-stitch-sage text-sm font-normal leading-normal">{userData.skillTreeCompletion}%</p>
                    </div>
                    <div className="rounded bg-stitch-track">
                      <div className="h-2 md:h-3 rounded bg-stitch-accent" style={{ width: `${userData.skillTreeCompletion}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Suggested Actions - occupe toute la largeur sur mobile, 4 colonnes sur desktop */}
              <div className="md:col-span-4">
                <h2 className="text-stitch-accent text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5 font-departure">Actions suggérées</h2>
                <div className="space-y-2 md:space-y-3">
                  {suggestedActions.map((action, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-4 bg-stitch-primary px-4 py-3 md:py-4 rounded-lg border border-stitch-border cursor-pointer hover:bg-[#eaf0ec] transition-colors"
                      onClick={() => navigateTo(action.path)}
                    >
                      <div className="text-stitch-sage flex items-center justify-center rounded-lg bg-[#eaf0ec] shrink-0 size-10 md:size-12">
                        {action.icon === 'Tree' ? (
                          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                          </svg>
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"></path>
                          </svg>
                        )}
                      </div>
                      <p className="text-stitch-sage text-base md:text-lg font-normal leading-normal flex-1 truncate">{action.title}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity - occupe toute la largeur */}
              <div className="md:col-span-12">
                <h2 className="text-stitch-accent text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5 font-departure">Activité récente</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                  {userData.recentActivities.map((activity, index) => (
                    <div key={index} className="flex items-center gap-4 bg-stitch-primary p-4 md:p-5 rounded-lg border border-stitch-border">
                      <div className="text-stitch-sage flex items-center justify-center rounded-lg bg-[#eaf0ec] shrink-0 size-12 md:size-14">
                        {activity.icon === 'CheckCircle' ? (
                          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M173.66,98.34a8,8,0,0,1,0,11.32l-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35A8,8,0,0,1,173.66,98.34ZM232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"></path>
                          </svg>
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M239.2,97.29a16,16,0,0,0-13.81-11L166,81.17,142.72,25.81h0a15.95,15.95,0,0,0-29.44,0L90.07,81.17,30.61,86.32a16,16,0,0,0-9.11,28.06L66.61,153.8,53.09,212.34a16,16,0,0,0,23.84,17.34l51-31,51.11,31a16,16,0,0,0,23.84-17.34l-13.51-58.6,45.1-39.36A16,16,0,0,0,239.2,97.29Zm-15.22,5-45.1,39.36a16,16,0,0,0-5.08,15.71L187.35,216v0l-51.07-31a15.9,15.9,0,0,0-16.54,0l-51,31h0L82.2,157.4a16,16,0,0,0-5.08-15.71L32,102.35a.37.37,0,0,1,0-.09l59.44-5.14a16,16,0,0,0,13.35-9.75L128,32.08l23.2,55.29a16,16,0,0,0,13.35,9.75L224,102.26S224,102.32,224,102.33Z"></path>
                          </svg>
                        )}
                      </div>
                      <div className="flex flex-col justify-center">
                        <p className="text-stitch-accent text-base md:text-lg font-medium leading-normal line-clamp-1">{activity.title}</p>
                        <p className="text-stitch-sage text-sm md:text-base font-normal leading-normal line-clamp-2">{activity.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}