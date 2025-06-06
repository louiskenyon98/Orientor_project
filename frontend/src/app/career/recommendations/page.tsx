'use client';

import React, { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { getAllJobRecommendations } from '@/services/api';
import JobSkillsTree from '@/components/jobs/JobSkillsTree';

export default function CareerRecommendationsPage() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any>(null);
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
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
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
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Career Recommendations</h1>
        <p className="text-gray-600 mb-8">
          Discover personalized career recommendations based on your profile
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left side: Job Cards */}
          <div className="space-y-4 max-h-[800px] overflow-y-auto pr-4">
            {recommendations.map((job) => (
              <div
                key={job.id}
                className={`bgblue w-full cursor-pointer transition-all duration-200 ${
                  selectedJob?.id === job.id ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedJob(job)}
              >
                <div className="card">
                  <h3 className="text-xl font-semibold mb-2">{job.metadata.title}</h3>
                  <p className="text-gray-300">{job.metadata.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Right side: Skills Tree */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            {selectedJob ? (
              <JobSkillsTree jobId={selectedJob.id} />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-gray-500">Select a job to view its skills tree</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 