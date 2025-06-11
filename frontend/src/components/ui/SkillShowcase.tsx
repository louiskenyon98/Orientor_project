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
  const [showBasicSkills, setShowBasicSkills] = useState<boolean>(false);

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

  // Don't render until we have a userId
  if (userId === undefined) {
    console.log('SkillShowcase: Waiting for userId...');
    return (
      <div className="w-full rounded-lg p-6" style={{ backgroundColor: 'var(--primary-color)', borderWidth: '1px', borderStyle: 'solid', borderColor: 'var(--border-color)' }}>
        <div className="flex items-center justify-center py-8">
          <p className="text-sm" style={{ color: 'var(--text-color)' }}>Loading skills...</p>
        </div>
      </div>
    );
  }
  
  if (!userId) {
    console.log('SkillShowcase: No userId available');
    return null;
  }
  
  console.log(`SkillShowcase: Rendering for userId ${userId}`);

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
              Your Personalized Skills
            </h2>
            <p 
              className="text-sm mt-1"
              style={{ color: 'var(--text-color)' }}
            >
              AI-curated skills based on your profile, interests, and personality
            </p>
          </div>
          
          {!hasGenerated && (
            <button
              onClick={generateSkills}
              disabled={isLoading}
              className="px-4 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 disabled:opacity-50"
              style={{ backgroundColor: 'var(--accent-color)' }}
            >
              {isLoading ? 'Analyzing...' : 'Discover My Skills'}
            </button>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <LoadingSpinner size="lg" />
            <p 
              className="mt-4 text-sm"
              style={{ color: 'var(--text-color)' }}
            >
              AI is analyzing your profile to discover your key skills...
            </p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div 
            className="rounded-lg p-4 mb-6"
            style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgb(239, 68, 68)' }}
          >
            <p className="text-red-600 text-sm">{error}</p>
            <button
              onClick={generateSkills}
              className="mt-2 text-red-600 text-sm underline hover:no-underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Skills Grid - AI-Curated Skills */}
        {skills.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
              {skills.map((skill, index) => (
                <SkillCard
                  key={skill.id || index}
                  skill={skill}
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
                  Ready to start your learning journey?
                </p>
                {/* Debug refresh button */}
                <button
                  onClick={() => {
                    console.log('Manual refresh triggered');
                    window.location.reload();
                  }}
                  className="text-xs px-3 py-1 rounded border"
                  style={{ 
                    borderColor: 'var(--border-color)',
                    color: 'var(--text-color)'
                  }}
                >
                  Refresh
                </button>
              </div>
              <button
                onClick={() => window.location.href = '/competence-tree'}
                className="px-6 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
                style={{ backgroundColor: 'var(--accent-color)' }}
              >
                Explore Full Skill Tree
              </button>
            </div>
          </>
        )}

        {/* Basic Skills Grid - Fallback when no AI skills */}
        {showBasicSkills && skills.length === 0 && !hasGenerated && basicSkills && (
          <>
            <div className="mb-4">
              <p 
                className="text-sm"
                style={{ color: 'var(--text-color)' }}
              >
                Your current skill levels (based on assessments)
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
              {[
                { name: 'Creativity', value: basicSkills.creativity, category: 'creative' },
                { name: 'Leadership', value: basicSkills.leadership, category: 'leadership' },
                { name: 'Critical Thinking', value: basicSkills.critical_thinking, category: 'cognitive' },
                { name: 'Problem Solving', value: basicSkills.problem_solving, category: 'cognitive' },
                { name: 'Digital Literacy', value: basicSkills.digital_literacy, category: 'technical' }
              ].map((skill, index) => (
                <BasicSkillCard
                  key={index}
                  skill={{
                    name: skill.name,
                    value: skill.value,
                    level: '',
                    category: skill.category
                  }}
                  className="h-full"
                />
              ))}
            </div>

            {/* Action bar for basic skills */}
            <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
              <div className="flex items-center gap-4">
                <p 
                  className="text-sm"
                  style={{ color: 'var(--text-color)' }}
                >
                  Want AI-powered skill insights?
                </p>
              </div>
              <button
                onClick={generateSkills}
                disabled={isLoading}
                className="px-6 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
                style={{ backgroundColor: 'var(--accent-color)' }}
              >
                {isLoading ? 'Analyzing...' : 'Get AI Skills'}
              </button>
            </div>
          </>
        )}

        {/* Empty State */}
        {!isLoading && !error && skills.length === 0 && !hasGenerated && !showBasicSkills && (
          <div className="text-center py-12">
            <div className="mb-4">
              <div 
                className="w-16 h-16 rounded-full mx-auto flex items-center justify-center text-2xl"
                style={{ backgroundColor: 'var(--border-color)' }}
              >
                🎯
              </div>
            </div>
            <h3 
              className="text-lg font-medium mb-2"
              style={{ color: 'var(--accent-color)' }}
            >
              Discover Your Key Skills
            </h3>
            <p 
              className="text-sm mb-4 max-w-md mx-auto"
              style={{ color: 'var(--text-color)' }}
            >
              Let our AI analyze your profile, personality, and interests to identify your core skills and create a personalized learning path.
            </p>
            <button
              onClick={generateSkills}
              disabled={isLoading}
              className="px-6 py-3 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
              style={{ backgroundColor: 'var(--accent-color)' }}
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SkillShowcase;