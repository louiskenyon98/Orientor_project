'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import UserCard from '@/components/ui/UserCard';
import PhilosophicalCard from '@/components/ui/PhilosophicalCard';
import Calendar from '@/components/ui/Calendar';
import EventsNotes from '@/components/ui/EventsNotes';
import JobRecommendationVerticalList from '@/components/jobs/JobRecommendationVerticalList';
import PersonalityCard from '@/components/ui/PersonalityCard';
import SkillShowcase from '@/components/ui/SkillShowcase';
import StarConstellation from '@/components/ui/StarConstellation';
import VectorSearchCard from '@/components/search/VectorSearchCard';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { getJobRecommendations } from '@/services/api';
import { Job } from '@/components/jobs/JobCard';
import axios from 'axios';

interface JobRecommendationsResponse {
  recommendations: Job[];
  user_id: number;
}

interface EnhancedPeerProfile {
  user_id: number;
  name: string;
  major: string;
  year?: number;
  job_title?: string;
  industry?: string;
  compatibility_score: number;
  explanation: string;
  score_details: {
    overall_compatibility: number;
    timestamp: string;
  };
}

export default function Home() {
  const router = useRouter();
  
  // Define API URL with fallback and trim any trailing spaces
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const cleanApiUrl = API_URL ? API_URL.trim() : '';
  
  // State
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | undefined>(undefined);
  const [peers, setPeers] = useState<EnhancedPeerProfile[]>([]);
  const [peersLoading, setPeersLoading] = useState(true);
  const [peersError, setPeersError] = useState<string | null>(null);

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

  // Fetch top peers
  useEffect(() => {
    const fetchPeers = async () => {
      try {
        setPeersLoading(true);
        setPeersError(null);
        
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.log('No auth token found for peer fetching');
          setPeersError('Authentication required');
          return;
        }
        
        const response = await axios.get<EnhancedPeerProfile[]>(`${cleanApiUrl}/peers/compatible`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // Get top 3 peers for homepage
        const topPeers = response.data.slice(0, 3);
        setPeers(topPeers);
      } catch (err: any) {
        console.error('Error fetching peers:', err);
        setPeersError('Unable to fetch peer recommendations');
      } finally {
        setPeersLoading(false);
      }
    };

    fetchPeers();
  }, [cleanApiUrl]);

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  return (
    <MainLayout>
      <div className="relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
        
        <div className="relative z-10 w-full">
          <div className="flex-1 w-full px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
            {/* First Section - Avatar, Personality Card, Calendar with different widths */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-8">
              {/* User Avatar Card (Left) - Takes 3 columns */}
              <div className="col-span-12 md:col-span-3 flex flex-col">
                <div className="mb-4">
                  <h2 className="text-xl font-semibold mb-4" style={{ color: '#000000' }}>My Progress</h2>
                  <UserCard
                    name={userData.name}
                    role={userData.role}
                    skills={userData.skills}
                    hollandResults={hollandResults}
                    loading={loading}
                    error={error}
                    className="p-6 w-full"
                    style={{
                      width: '100%',
                      minHeight: '254px',
                      borderRadius: '30px',
                      background: '#e0e0e0',
                      boxShadow: '15px 15px 30px #bebebe, -15px -15px 30px #ffffff'
                    }}
                  />
                </div>
                
              </div>

              {/* Personalité Card (Center) - Takes 6 columns */}
              <div className="col-span-12 md:col-span-6" style={{ marginTop: '52px' }}>
                <PhilosophicalCard userId={currentUserId} />
              </div>

              {/* Calendar (Right) - Takes 3 columns (narrower) */}
              <div className="col-span-12 md:col-span-3">
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

            {/* Second Section - Top Peers, Recommended Jobs, Vector Search, Events & Notes with different widths */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-8">
              {/* Top Peers (Left) - Takes 3 columns */}
              <div className="col-span-12 md:col-span-3">
                <div style={{
                  width: '100%',
                  minHeight: '254px',
                  borderRadius: '30px',
                  background: '#e0e0e0',
                  boxShadow: '15px 15px 30px #bebebe, -15px -15px 30px #ffffff',
                  padding: '24px'
                }}>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold" style={{ color: '#000000' }}>Top Peers</h2>
                    <Link
                      href="/peers"
                      className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1"
                    >
                      <span>See all</span>
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                        <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                      </svg>
                    </Link>
                  </div>
                  
                  {peersLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-sm text-gray-600 mt-2">Loading peers...</p>
                    </div>
                  ) : peersError ? (
                    <div className="text-center py-8">
                      <p className="text-sm text-red-600">{peersError}</p>
                    </div>
                  ) : peers.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-sm text-gray-600">No peer recommendations available</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {peers.map((peer) => (
                        <div
                          key={peer.user_id}
                          className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer transition-colors"
                          onClick={() => router.push(`/peers/${peer.user_id}`)}
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                              {peer.name?.charAt(0).toUpperCase() || '?'}
                            </div>
                            <div className="flex-1">
                              <h3 className="font-medium text-sm">
                                {peer.name || `User ${peer.user_id}`}
                              </h3>
                              <p className="text-xs text-gray-600 dark:text-gray-400">
                                {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                              </p>
                              {peer.job_title && (
                                <p className="text-xs text-gray-500">
                                  {peer.job_title}
                                </p>
                              )}
                            </div>
                            <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                              {Math.round((peer.compatibility_score || 0) * 100)}% match
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Recommended Jobs (Center Left) - Takes 3 columns */}
              <div className="col-span-12 md:col-span-3">
                <div style={{
                  width: '100%',
                  minHeight: '254px',
                  borderRadius: '30px',
                  background: '#e0e0e0',
                  boxShadow: '15px 15px 30px #bebebe, -15px -15px 30px #ffffff',
                  padding: '24px'
                }}>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold" style={{ color: '#000000' }}>Recommended Jobs</h2>
                    <Link
                      href="/career/recommendations"
                      className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1"
                    >
                      <span>See all</span>
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                        <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                      </svg>
                    </Link>
                  </div>
                  
                  {jobsLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-sm text-gray-600 mt-2">Loading recommendations...</p>
                    </div>
                  ) : jobsError ? (
                    <div className="text-center py-8">
                      <p className="text-sm text-red-600">{jobsError}</p>
                    </div>
                  ) : jobRecommendations.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-sm text-gray-600">No job recommendations available</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {jobRecommendations.slice(0, 3).map((job) => (
                        <div
                          key={job.id}
                          className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer transition-colors"
                          onClick={() => handleSelectJob(job)}
                        >
                          <h3 className="font-medium text-sm mb-1">
                            {job.metadata.preferred_label || job.metadata.title || 'Job Title'}
                          </h3>
                          <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                            {job.metadata.description || 'No description available'}
                          </p>
                          <div className="flex justify-between items-center mt-2">
                            <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                              {Math.round(job.score * 100)}% match
                            </div>
                            {job.metadata.skills && job.metadata.skills.length > 0 && (
                              <div className="flex gap-1 flex-wrap">
                                {job.metadata.skills.slice(0, 2).map((skill, index) => (
                                  <span
                                    key={index}
                                    className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full"
                                  >
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Vector Search (Center Right) - Takes 3 columns */}
              <div className="col-span-12 md:col-span-3">
                <VectorSearchCard />
              </div>

              {/* Events & Notes (Right) - Takes 3 columns */}
              <div className="col-span-12 md:col-span-3">
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