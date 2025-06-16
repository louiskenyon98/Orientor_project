'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useRouter } from 'next/navigation';
import UserCard from '@/components/ui/UserCard';
import PhilosophicalCard from '@/components/ui/PhilosophicalCard';
import Calendar from '@/components/ui/Calendar';
import PeersList from '@/components/ui/PeersList';
import EventsNotes from '@/components/ui/EventsNotes';
import JobRecommendationVerticalList from '@/components/jobs/JobRecommendationVerticalList';
import PersonalityCard from '@/components/ui/PersonalityCard';
import SkillShowcase from '@/components/ui/SkillShowcase';
import StarConstellation from '@/components/ui/StarConstellation';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { getJobRecommendations } from '@/services/api';
import { Job } from '@/components/jobs/JobCard';

interface JobRecommendationsResponse {
  recommendations: Job[];
  user_id: number;
}

export default function Home() {
  const router = useRouter();
  
  // State
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | undefined>(undefined);

  // Sample user data
  const userData = {
    name: 'Philippe B.',
    role: 'Étudiant Msc. in Data Science',
    level: 3,
    avatarUrl: '/Avatar.PNG',
    skills: ['UI Design', 'JavaScript', 'React', 'Node.js'],
    totalXP: 250,
  };

  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'HEXACO Test', icon: 'Brain', path: '/hexaco-test/select' },
    { name: 'Self-Reflection', icon: 'Reflection', path: '/self-reflection' },
    { name: 'Holland Results', icon: 'Personality', path: '/profile/holland-results' },
    { name: 'HEXACO Results', icon: 'Brain', path: '/profile/hexaco-results' },
  ];

  // Fetch user data and Holland results
  useEffect(() => {
    const fetchHollandResults = async () => {
      try {
        const results = await hollandTestService.getUserLatestResults();
        setHollandResults(results);
      } catch (err) {
        console.error('Error fetching Holland results:', err);
        setError('Unable to fetch Holland results');
      } finally {
        setLoading(false);
      }
    };

    fetchHollandResults();
  }, []);

  // Fetch job recommendations
  useEffect(() => {
    const fetchJobRecommendations = async () => {
      try {
        setJobsLoading(true);
        setJobsError(null);
        const response = await getJobRecommendations() as JobRecommendationsResponse;
        
        if (response && response.recommendations) {
          const limitedRecommendations = response.recommendations.slice(0, 3);
          setJobRecommendations(limitedRecommendations);
          
          if (limitedRecommendations.length > 0) {
            setSelectedJob(limitedRecommendations[0]);
          }
        }
      } catch (err) {
        console.error('Error fetching job recommendations:', err);
        setJobsError('Unable to fetch job recommendations');
      } finally {
        setJobsLoading(false);
      }
    };
    
    fetchJobRecommendations();
  }, []);

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  return (
    <MainLayout>
      <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
        <StarConstellation />
        
        <div className="relative z-10 w-full">
          <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
            {/* First Section - 3 columns: Avatar, Personality Card, Calendar */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {/* User Avatar Card (Left) - Restored Original */}
              <div className="flex flex-col">
                <div className="mb-4">
                  <h2 className="premium-section-title mb-4">My Progress</h2>
                  <UserCard
                    name={userData.name}
                    role={userData.role}
                    skills={userData.skills}
                    hollandResults={hollandResults}
                    loading={loading}
                    error={error}
                    className="premium-card p-6 w-full"
                  />
                </div>
                
              </div>

              {/* Personalité Card (Center) - Clean Interactive Card Only */}
              <div>
                <PhilosophicalCard userId={currentUserId} />
              </div>

              {/* Calendar (Right) */}
              <div className="flex justify-center items-start">
                <Calendar 
                  events={[
                    { id: '1', date: new Date(2025, 0, 20), title: 'Holland Test Review', type: 'test' },
                    { id: '2', date: new Date(2025, 0, 25), title: 'Career Challenge', type: 'challenge' },
                    { id: '3', date: new Date(2025, 0, 28), title: 'Peer Meetup', type: 'event' }
                  ]}
                  onDateClick={(date) => console.log('Date clicked:', date)}
                />
              </div>
            </div>

            {/* Second Section - 3 columns: Top Peers, Recommended Jobs, Events & Notes */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {/* Top Peers (Left) */}
              <div>
                <PeersList 
                  peers={[
                    {
                      id: 1,
                      name: 'Sarah Chen',
                      avatarUrl: '/api/placeholder/48/48',
                      compatibility: 0.92,
                      description: 'Data Science enthusiast with ML focus',
                      skills: ['Python', 'TensorFlow', 'Statistics']
                    },
                    {
                      id: 2,
                      name: 'Alex Kumar',
                      avatarUrl: '/api/placeholder/48/48',
                      compatibility: 0.87,
                      description: 'Full-stack developer passionate about AI',
                      skills: ['React', 'Node.js', 'AWS']
                    },
                    {
                      id: 3,
                      name: 'Emma Johnson',
                      avatarUrl: '/api/placeholder/48/48',
                      compatibility: 0.85,
                      description: 'UX/UI designer with data viz expertise',
                      skills: ['Figma', 'D3.js', 'User Research']
                    }
                  ]}
                  onPeerClick={(peer) => router.push(`/peers/${peer.id}`)}
                />
              </div>

              {/* Recommended Jobs (Center) */}
              <div>
                <JobRecommendationVerticalList
                  jobs={jobRecommendations}
                  onJobClick={handleSelectJob}
                  onSaveJob={(job) => console.log('Save job:', job)}
                />
              </div>

              {/* Events & Notes (Right) */}
              <div>
                <EventsNotes
                  events={[
                    {
                      id: '1',
                      title: 'Holland Test Review',
                      date: new Date(2025, 0, 20),
                      type: 'test',
                      description: 'Review your personality test results'
                    },
                    {
                      id: '2',
                      title: 'Career Challenge',
                      date: new Date(2025, 0, 25),
                      type: 'challenge',
                      description: 'Complete the data analysis challenge'
                    }
                  ]}
                  notes={[
                    {
                      id: 1,
                      title: 'Career Goals 2025',
                      content: 'Focus on machine learning and deep learning skills...',
                      createdAt: new Date(2025, 0, 15),
                      tags: ['Career', 'Goals']
                    },
                    {
                      id: 2,
                      title: 'Interview Prep Notes',
                      content: 'Remember to highlight project experience...',
                      createdAt: new Date(2025, 0, 10),
                      tags: ['Interview', 'Preparation']
                    }
                  ]}
                  onEventClick={(event) => console.log('Event clicked:', event)}
                  onNoteClick={(note) => router.push(`/notes/${note.id}`)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}