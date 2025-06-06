'use client';

import React, { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { getAllJobRecommendations } from '@/services/api';
import JobSkillsTree from '@/components/jobs/JobSkillsTree';
import JobCard, { Job } from '@/components/jobs/JobCard';
import LoadingScreen from '@/components/ui/LoadingScreen';

export default function CareerRecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const response = await getAllJobRecommendations(30);
        console.log('Fetched recommendations:', response);
        if (response && response.recommendations) {
          setRecommendations(response.recommendations);
          // Set the first job as selected by default
          if (response.recommendations.length > 0) {
            setSelectedJob(response.recommendations[0]);
          }
        }
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError('Failed to load career recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <LoadingScreen message="Loading career recommendations..." />
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-red-500">{error}</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <style jsx>{`
        .career-recommendations-card .glass {
          transform: rotate(0deg) !important;
          margin: 0 !important;
        }
        .career-recommendations-card:hover .glass {
          transform: rotate(0deg) !important;
          margin: 0 !important;
        }
      `}</style>
      <div className="max-w-[3000px] mx-auto px-18 py-20">
        <h1 className="text-4xl font-bold mb-3">Career Recommendations</h1>
        <p className="text-gray-600 mb-10 text-lg">
          Discover personalized career recommendations based on your profile
        </p>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-20">
          {/* Left side: Job Cards - 6 columns */}
          <div className="xl:col-span-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-12 max-h-[3000px] overflow-y-auto pr-6">
            {recommendations.map((job) => (
              <div
                key={job.id}
                className="career-recommendations-card"
                style={{ '--r': '0' } as React.CSSProperties}
              >
                <JobCard
                  job={job}
                  isSelected={selectedJob?.id === job.id}
                  onClick={() => setSelectedJob(job)}
                  className="h-72"
                />
              </div>
            ))}
          </div>

          {/* Right side: Skills Tree - 6 columns */}
          <div className="xl:col-span-6 bg-white rounded-lg shadow-lg p-10 min-h-[1400px]">
            {selectedJob ? (
              <div className="h-full">
                <h2 className="text-3xl font-semibold mb-6">
                  {selectedJob.metadata.preferred_label || selectedJob.metadata.title || selectedJob.id.replace('occupation::key_', '')}
                </h2>
                <div className="h-[calc(100%-5rem)]">
                  <JobSkillsTree jobId={selectedJob.id} height="1000px" />
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-gray-500 text-xl">Select a job to view its skills tree</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 