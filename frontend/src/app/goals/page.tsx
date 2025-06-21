'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import TimelineVisualization, { SkillNode, TimelineTier } from '@/components/career/TimelineVisualization';
import SkillRelationshipGraph from '@/components/career/SkillRelationshipGraph';
// import { motion } from 'framer-motion'; // Removed for build compatibility
import { toast } from 'react-hot-toast';

// Mock data generator with GraphSage-style scoring
const generateMockCareerData = (): TimelineTier[] => {
  return [
    {
      id: 'tier-1',
      title: 'Foundation & Exploration',
      level: 1,
      timeline_months: 6,
      confidence_threshold: 0.8,
      skills: [
        {
          id: 'skill-1-1',
          label: 'Programming Fundamentals',
          confidence_score: 0.92,
          type: 'skill',
          level: 1,
          relationships: ['skill-1-2', 'skill-2-1'],
          metadata: {
            description: 'Learn core programming concepts and syntax',
            estimated_months: 3,
            prerequisites: [],
            learning_resources: ['Online courses', 'Practice projects']
          }
        },
        {
          id: 'skill-1-2',
          label: 'Problem Solving',
          confidence_score: 0.85,
          type: 'skill',
          level: 1,
          relationships: ['skill-1-1', 'skill-2-3'],
          metadata: {
            description: 'Develop analytical thinking and debugging skills',
            estimated_months: 2,
            prerequisites: [],
            learning_resources: ['Algorithm challenges', 'Code reviews']
          }
        },
        {
          id: 'skill-1-3',
          label: 'Version Control',
          confidence_score: 0.78,
          type: 'skill',
          level: 1,
          relationships: ['skill-2-1', 'skill-2-2'],
          metadata: {
            description: 'Master Git and collaborative development workflows',
            estimated_months: 1,
            prerequisites: ['skill-1-1'],
            learning_resources: ['Git tutorials', 'GitHub projects']
          }
        },
        {
          id: 'skill-1-4',
          label: 'Web Technologies',
          confidence_score: 0.65,
          type: 'skill',
          level: 1,
          relationships: ['skill-2-1', 'skill-2-4'],
          metadata: {
            description: 'Understanding of HTML, CSS, and JavaScript basics',
            estimated_months: 4,
            prerequisites: [],
            learning_resources: ['MDN docs', 'Frontend projects']
          }
        },
        {
          id: 'skill-1-5',
          label: 'Database Basics',
          confidence_score: 0.42,
          type: 'skill',
          level: 1,
          relationships: ['skill-2-2', 'skill-3-2'],
          metadata: {
            description: 'SQL fundamentals and database design principles',
            estimated_months: 2,
            prerequisites: [],
            learning_resources: ['SQL tutorials', 'Database projects']
          }
        }
      ]
    },
    {
      id: 'tier-2',
      title: 'Skill Development',
      level: 2,
      timeline_months: 12,
      confidence_threshold: 0.7,
      skills: [
        {
          id: 'skill-2-1',
          label: 'Frontend Frameworks',
          confidence_score: 0.89,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-1', 'skill-1-4', 'skill-3-1'],
          metadata: {
            description: 'React, Vue, or Angular framework proficiency',
            estimated_months: 6,
            prerequisites: ['skill-1-1', 'skill-1-4'],
            learning_resources: ['Framework docs', 'Component libraries']
          }
        },
        {
          id: 'skill-2-2',
          label: 'Backend Development',
          confidence_score: 0.73,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-1', 'skill-1-5', 'skill-3-2'],
          metadata: {
            description: 'Server-side programming and API development',
            estimated_months: 8,
            prerequisites: ['skill-1-1', 'skill-1-5'],
            learning_resources: ['Node.js', 'Python', 'API design']
          }
        },
        {
          id: 'skill-2-3',
          label: 'Testing & QA',
          confidence_score: 0.61,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-2', 'skill-3-1', 'skill-3-3'],
          metadata: {
            description: 'Unit testing, integration testing, and QA practices',
            estimated_months: 4,
            prerequisites: ['skill-1-1', 'skill-1-2'],
            learning_resources: ['Testing frameworks', 'TDD practices']
          }
        },
        {
          id: 'skill-2-4',
          label: 'UI/UX Design',
          confidence_score: 0.55,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-4', 'skill-3-1'],
          metadata: {
            description: 'User interface design and user experience principles',
            estimated_months: 5,
            prerequisites: ['skill-1-4'],
            learning_resources: ['Design tools', 'UX research']
          }
        },
        {
          id: 'skill-2-5',
          label: 'DevOps Basics',
          confidence_score: 0.38,
          type: 'skill',
          level: 2,
          relationships: ['skill-1-3', 'skill-3-3'],
          metadata: {
            description: 'CI/CD, containerization, and deployment strategies',
            estimated_months: 6,
            prerequisites: ['skill-1-3'],
            learning_resources: ['Docker', 'CI/CD tools', 'Cloud platforms']
          }
        }
      ]
    },
    {
      id: 'tier-3',
      title: 'Specialization & Leadership',
      level: 3,
      timeline_months: 18,
      confidence_threshold: 0.6,
      skills: [
        {
          id: 'skill-3-1',
          label: 'Full-Stack Architecture',
          confidence_score: 0.81,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-1', 'skill-2-2', 'skill-4-1'],
          metadata: {
            description: 'End-to-end application architecture and design patterns',
            estimated_months: 10,
            prerequisites: ['skill-2-1', 'skill-2-2'],
            learning_resources: ['System design', 'Architecture patterns']
          }
        },
        {
          id: 'skill-3-2',
          label: 'Database Optimization',
          confidence_score: 0.67,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-2', 'skill-4-2'],
          metadata: {
            description: 'Advanced database design, indexing, and performance tuning',
            estimated_months: 8,
            prerequisites: ['skill-1-5', 'skill-2-2'],
            learning_resources: ['Database internals', 'Performance analysis']
          }
        },
        {
          id: 'skill-3-3',
          label: 'Team Leadership',
          confidence_score: 0.52,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-3', 'skill-4-1', 'skill-4-3'],
          metadata: {
            description: 'Technical leadership, mentoring, and project management',
            estimated_months: 12,
            prerequisites: ['skill-2-3'],
            learning_resources: ['Leadership training', 'Agile methodologies']
          }
        },
        {
          id: 'skill-3-4',
          label: 'Security & Privacy',
          confidence_score: 0.44,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-2', 'skill-4-2'],
          metadata: {
            description: 'Application security, data privacy, and compliance',
            estimated_months: 6,
            prerequisites: ['skill-2-2'],
            learning_resources: ['Security frameworks', 'Compliance standards']
          }
        },
        {
          id: 'skill-3-5',
          label: 'Performance Optimization',
          confidence_score: 0.39,
          type: 'skill',
          level: 3,
          relationships: ['skill-2-1', 'skill-2-2', 'skill-4-2'],
          metadata: {
            description: 'Application performance analysis and optimization techniques',
            estimated_months: 8,
            prerequisites: ['skill-2-1', 'skill-2-2'],
            learning_resources: ['Profiling tools', 'Optimization patterns']
          }
        }
      ]
    },
    {
      id: 'tier-4',
      title: 'Mastery & Innovation',
      level: 4,
      timeline_months: 24,
      confidence_threshold: 0.5,
      skills: [
        {
          id: 'skill-4-1',
          label: 'Technical Strategy',
          confidence_score: 0.72,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-1', 'skill-3-3'],
          metadata: {
            description: 'Technology roadmapping, technical vision, and strategic planning',
            estimated_months: 15,
            prerequisites: ['skill-3-1', 'skill-3-3'],
            learning_resources: ['Strategy frameworks', 'Technology trends']
          }
        },
        {
          id: 'skill-4-2',
          label: 'System Scalability',
          confidence_score: 0.58,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-1', 'skill-3-2', 'skill-3-5'],
          metadata: {
            description: 'Large-scale system design and scalability engineering',
            estimated_months: 18,
            prerequisites: ['skill-3-1', 'skill-3-2'],
            learning_resources: ['Distributed systems', 'Scalability patterns']
          }
        },
        {
          id: 'skill-4-3',
          label: 'Innovation Leadership',
          confidence_score: 0.45,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-3'],
          metadata: {
            description: 'Leading innovation initiatives and emerging technology adoption',
            estimated_months: 20,
            prerequisites: ['skill-3-3'],
            learning_resources: ['Innovation frameworks', 'Emerging technologies']
          }
        },
        {
          id: 'skill-4-4',
          label: 'Cross-Domain Expertise',
          confidence_score: 0.33,
          type: 'skill',
          level: 4,
          relationships: ['skill-3-1', 'skill-3-4'],
          metadata: {
            description: 'Expertise spanning multiple technology domains and business areas',
            estimated_months: 24,
            prerequisites: ['skill-3-1'],
            learning_resources: ['Domain knowledge', 'Business understanding']
          }
        }
      ]
    }
  ];
};

const GoalsPage: React.FC = () => {
  const [careerData, setCareerData] = useState<TimelineTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<SkillNode | null>(null);
  const [activeView, setActiveView] = useState<'timeline' | 'graph'>('timeline');

  useEffect(() => {
    // Simulate loading career progression data
    const loadCareerData = async () => {
      setLoading(true);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      try {
        const data = generateMockCareerData();
        setCareerData(data);
        toast.success('Career progression loaded successfully!');
      } catch (error) {
        toast.error('Failed to load career progression data');
        console.error('Error loading career data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadCareerData();
  }, []);

  const handleSkillClick = (skill: SkillNode) => {
    setSelectedSkill(skill);
    toast(`Selected: ${skill.label}`, {
      icon: '🎯',
      duration: 2000,
    });
  };

  const handleSetCareerGoal = (skill: SkillNode) => {
    toast.success(`Set "${skill.label}" as career goal!`);
    // TODO: Implement actual career goal setting API
  };

  const totalSkills = careerData.reduce((sum, tier) => sum + tier.skills.length, 0);
  const highConfidenceSkills = careerData.reduce(
    (sum, tier) => sum + tier.skills.filter(s => s.confidence_score >= tier.confidence_threshold).length,
    0
  );

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your career progression...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 animate-in slide-in-from-top duration-300">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Career Goals</h1>
              <p className="text-gray-600 mt-2">
                Track your progression with GraphSage-powered confidence scoring
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* View Toggle */}
              <div className="bg-gray-100 rounded-lg p-1 flex">
                <button
                  onClick={() => setActiveView('timeline')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'timeline'
                      ? 'bg-white text-gray-900 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Timeline View
                </button>
                <button
                  onClick={() => setActiveView('graph')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeView === 'graph'
                      ? 'bg-white text-gray-900 shadow'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Graph View
                </button>
              </div>
              
              {/* Stats */}
              <div className="text-right">
                <div className="text-sm text-gray-600">Progress Overview</div>
                <div className="text-lg font-semibold text-gray-900">
                  {highConfidenceSkills} / {totalSkills} skills ready
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        {activeView === 'timeline' ? (
          <div className="animate-in slide-in-from-left duration-300">
            <TimelineVisualization
              tiers={careerData}
              onSkillClick={handleSkillClick}
              className="mb-8"
            />
          </div>
        ) : (
          <div className="animate-in slide-in-from-right duration-300">
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-900">Skill Relationship Graph</h3>
                <p className="text-gray-600 mb-4">
                  Interactive visualization of skill connections and GraphSage confidence scores
                </p>
                
                <SkillRelationshipGraph
                  skills={careerData.flatMap(tier => tier.skills)}
                  onSkillClick={handleSkillClick}
                  highlightedSkills={selectedSkill ? new Set([selectedSkill.id, ...(selectedSkill.relationships || [])]) : new Set()}
                  className="h-96"
                />
              </div>
              
              {/* Graph Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Total Skills</div>
                  <div className="text-2xl font-bold text-gray-900">{totalSkills}</div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">High Confidence</div>
                  <div className="text-2xl font-bold text-green-600">{highConfidenceSkills}</div>
                </div>
                
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                  <div className="text-sm text-gray-600">Skill Connections</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {careerData.reduce((sum, tier) => 
                      sum + tier.skills.reduce((skillSum, skill) => 
                        skillSum + (skill.relationships?.length || 0), 0
                      ), 0
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Panel */}
        {selectedSkill && (
          <div className="fixed bottom-4 right-4 bg-white rounded-xl shadow-lg border border-gray-200 p-6 max-w-sm animate-in slide-in-from-bottom duration-200">
            <h3 className="font-semibold text-gray-900 mb-2">Selected Skill</h3>
            <p className="text-gray-600 mb-4">{selectedSkill.label}</p>
            
            <div className="flex space-x-2">
              <button
                onClick={() => handleSetCareerGoal(selectedSkill)}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Set as Goal
              </button>
              <button
                onClick={() => setSelectedSkill(null)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default GoalsPage;