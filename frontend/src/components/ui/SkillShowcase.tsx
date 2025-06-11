'use client';

import React, { useState, useEffect } from 'react';
import SkillCard from './SkillCard';
import BasicSkillCard from './BasicSkillCard';
import LoadingSpinner from './LoadingSpinner';
import { generateCompetenceTree } from '@/services/competenceTreeService';
import { getUserSkills, UserSkills } from '@/services/spaceService';

interface SkillShowcaseProps {
  userId?: number;
  className?: string;
}

interface AnchorSkill {
  id: string;
  esco_label: string;
  esco_description: string;
  category: string;
  confidence: number;
  applications?: string[];
  justification: string;
}

const SkillShowcase: React.FC<SkillShowcaseProps> = ({ userId, className = '' }) => {
  const [skills, setSkills] = useState<AnchorSkill[]>([]);
  const [basicSkills, setBasicSkills] = useState<UserSkills | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasGenerated, setHasGenerated] = useState<boolean>(false);
  const [showBasicSkills, setShowBasicSkills] = useState<boolean>(true); // Always show basic skills first

  const generateSkills = async () => {
    if (!userId) {
      setError('User ID not available');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Generate the competence tree which will infer anchor skills
      const result = await generateCompetenceTree(userId);
      
      if (result.graph_id) {
        // Fetch the generated tree data to get anchor skills
        const response = await fetch(`/api/v1/competence-tree/${result.graph_id}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });

        if (response.ok) {
          const treeData = await response.json();
          
          // Extract anchor skills from tree data
          const anchorMetadata = treeData.anchor_metadata || [];
          if (anchorMetadata.length > 0) {
            setSkills(anchorMetadata.slice(0, 5)); // Show top 5 skills
            setHasGenerated(true);
          } else {
            setError('No anchor skills found in generated tree');
          }
        } else {
          setError('Failed to fetch generated skill tree');
        }
      } else {
        setError('Failed to generate skill tree');
      }
    } catch (err) {
      console.error('Error generating skills:', err);
      setError('An error occurred while generating your skills');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch basic skills
  const fetchBasicSkills = async () => {
    try {
      const userSkills = await getUserSkills();
      setBasicSkills(userSkills);
      
      // Check if user has any non-null skill values
      const hasSkillData = Object.values(userSkills).some(value => value !== null && value !== undefined);
      setShowBasicSkills(hasSkillData);
    } catch (err) {
      console.error('Error fetching basic skills:', err);
    }
  };

  // Check if user already has anchor skills
  useEffect(() => {
    const checkExistingSkills = async () => {
      if (!userId) {
        console.log('No userId available for checking existing skills');
        return;
      }

      setIsLoading(true);
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.log('No auth token available');
          setIsLoading(false);
          return;
        }

        console.log(`Checking existing anchor skills for user ${userId}...`);
        const response = await fetch('/api/v1/competence-tree/anchor-skills', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        console.log(`Anchor skills response status: ${response.status}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Anchor skills response:', data);
          
          if (data.anchor_skills && data.anchor_skills.length > 0) {
            setSkills(data.anchor_skills.slice(0, 5));
            setHasGenerated(true);
            console.log(`Found ${data.anchor_skills.length} existing anchor skills`);
          } else {
            console.log('No anchor skills found in response');
            // Fetch basic skills as fallback
            await fetchBasicSkills();
          }
        } else {
          console.log(`Failed to fetch anchor skills: ${response.status} ${response.statusText}`);
          // Fetch basic skills as fallback
          await fetchBasicSkills();
        }
      } catch (err) {
        console.error('Error checking for existing anchor skills:', err);
        // Fetch basic skills as fallback
        await fetchBasicSkills();
      } finally {
        setIsLoading(false);
      }
    };

    checkExistingSkills();
  }, [userId]);

  // For testing purposes, show basic skills even without userId
  if (userId === undefined) {
    console.log('SkillShowcase: No userId, showing basic skills demo...');
    return (
      <div className={`w-full ${className}`}>
        <div 
          className="rounded-lg p-6"
          style={{
            backgroundColor: 'var(--primary-color)',
            borderWidth: '1px',
            borderStyle: 'solid',
            borderColor: 'var(--border-color)'
          }}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 
                className="text-xl font-bold"
                style={{ color: 'var(--accent-color)' }}
              >
                Your Core Skills
              </h2>
              <p 
                className="text-sm mt-1"
                style={{ color: 'var(--text-color)' }}
              >
                Essential abilities for career success
              </p>
            </div>
          </div>

          {/* Basic Skills Grid - Demo */}
          <div className="mb-4">
            <p 
              className="text-sm"
              style={{ color: 'var(--text-color)' }}
            >
              Explore these fundamental skills
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
            {[
              { 
                name: 'Creativity', 
                description: 'Generate innovative ideas and original solutions'
              },
              { 
                name: 'Leadership', 
                description: 'Guide teams and inspire others toward goals'
              },
              { 
                name: 'Critical Thinking', 
                description: 'Analyze information and make logical decisions'
              },
              { 
                name: 'Problem Solving', 
                description: 'Identify issues and develop effective solutions'
              },
              { 
                name: 'Digital Literacy', 
                description: 'Use technology effectively and adapt to new tools'
              }
            ].map((skill, index) => (
              <BasicSkillCard
                key={index}
                skill={{
                  name: skill.name,
                  description: skill.description
                }}
                className="h-full"
              />
            ))}
          </div>

          {/* Action bar */}
          <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
            <div className="flex items-center gap-4">
              <p 
                className="text-sm"
                style={{ color: 'var(--text-color)' }}
              >
                Login to get personalized skill insights
              </p>
            </div>
            <button
              onClick={() => window.location.href = '/login'}
              className="px-6 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
              style={{ backgroundColor: 'var(--accent-color)' }}
            >
              Login
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  if (!userId) {
    console.log('SkillShowcase: No userId available');
    return null;
  }
  
  console.log(`SkillShowcase: Rendering for userId ${userId}`);

  // Always show basic skills with new card design
  return (
    <div className={`w-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 
            className="text-xl font-bold"
            style={{ color: 'var(--accent-color)' }}
          >
            Your Core Skills
          </h2>
          <p 
            className="text-sm mt-1"
            style={{ color: 'var(--text-color)' }}
          >
            Essential abilities for career success
          </p>
        </div>
        
        {userId && !hasGenerated && (
          <button
            onClick={generateSkills}
            disabled={isLoading}
            className="px-4 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 disabled:opacity-50"
            style={{ backgroundColor: 'var(--accent-color)' }}
          >
            {isLoading ? 'Analyzing...' : 'Get AI Insights'}
          </button>
        )}
      </div>

      {/* Always show Basic Skills with new design */}
      <div className="mb-4">
        <p 
          className="text-sm"
          style={{ color: 'var(--text-color)' }}
        >
          {userId ? 'Your fundamental skills' : 'Explore these fundamental skills'}
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-6">
          {[
            { 
              name: 'Creativity', 
              description: 'Generate innovative ideas and original solutions',
              icon: '◇'
            },
            { 
              name: 'Leadership', 
              description: 'Guide teams and inspire others toward goals',
              icon: '◆'
            },
            { 
              name: 'Critical Thinking', 
              description: 'Analyze information and make logical decisions',
              icon: '○'
            },
            { 
              name: 'Problem Solving', 
              description: 'Identify issues and develop effective solutions',
              icon: '◎'
            },
            { 
              name: 'Digital Literacy', 
              description: 'Use technology effectively and adapt to new tools',
              icon: '□'
            }
          ].map((skill, index) => (
            <BasicSkillCard
              key={index}
              skill={{
                name: skill.name,
                description: skill.description,
                icon: skill.icon
              }}
              className="h-full"
            />
          ))}
        </div>

      {/* Action bar */}
      <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
        <div className="flex items-center gap-4">
          <p 
            className="text-sm"
            style={{ color: 'var(--text-color)' }}
          >
            {userId ? 'Want AI-powered insights?' : 'Login to get personalized insights'}
          </p>
        </div>
        <button
          onClick={() => userId ? generateSkills() : window.location.href = '/login'}
          disabled={isLoading}
          className="px-6 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
          style={{ backgroundColor: 'var(--accent-color)' }}
        >
          {userId ? (isLoading ? 'Analyzing...' : 'Get AI Skills') : 'Login'}
        </button>
      </div>

      {/* Show loading overlay if AI analysis is running */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-sm text-gray-600">
              AI is analyzing your profile...
            </p>
          </div>
        </div>
      )}

      {/* Show error if any */}
      {error && (
        <div className="mt-4 p-4 bg-red-100 border border-red-300 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
};

export default SkillShowcase;