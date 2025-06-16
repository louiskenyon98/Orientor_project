'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

// Mock data for demonstration
const mockPersonalityProfile = {
  hollandCode: 'IRA',
  primaryType: 'Investigative',
  secondaryType: 'Realistic',
  tertiaryType: 'Artistic',
  scores: {
    investigative: 85,
    realistic: 78,
    artistic: 72,
    social: 45,
    enterprising: 38,
    conventional: 32
  }
};

const mockPrograms = [
  {
    id: '1',
    name: 'Computer Science Technology',
    institution: 'Dawson College',
    location: 'Montreal, QC',
    type: 'CEGEP',
    duration: '3 years',
    tuition: '$183/semester',
    employmentRate: 94,
    hollandMatch: 89,
    careerAlignment: 'Software Developer',
    description: 'Learn programming, software development, and computer systems administration.',
    whyRecommended: 'Perfect match for your Investigative and Realistic personality traits',
    requirements: 'Secondary V Math and Science'
  },
  {
    id: '2',
    name: 'Software Engineering',
    institution: 'McGill University',
    location: 'Montreal, QC',
    type: 'University',
    duration: '4 years',
    tuition: '$4,570/year',
    employmentRate: 97,
    hollandMatch: 92,
    careerAlignment: 'Software Engineer',
    description: 'Comprehensive program covering software design, development, and engineering principles.',
    whyRecommended: 'Excellent fit for your analytical and problem-solving strengths',
    requirements: 'CEGEP diploma in Science or Computer Science'
  },
  {
    id: '3',
    name: 'Data Science and Analytics',
    institution: 'Université de Montréal',
    location: 'Montreal, QC',
    type: 'University',
    duration: '3 years',
    tuition: '$3,200/year',
    employmentRate: 91,
    hollandMatch: 87,
    careerAlignment: 'Data Scientist',
    description: 'Statistical analysis, machine learning, and data visualization techniques.',
    whyRecommended: 'Combines your investigative nature with creative problem-solving',
    requirements: 'CEGEP diploma with strong mathematics background'
  }
];

const mockCareerPaths = [
  {
    career: 'Software Developer',
    programs: ['Computer Science Technology', 'Software Engineering'],
    averageSalary: '$75,000',
    jobGrowth: '+22%'
  },
  {
    career: 'Data Scientist',
    programs: ['Data Science and Analytics', 'Computer Science Technology'],
    averageSalary: '$85,000',
    jobGrowth: '+35%'
  }
];

interface ProgramCardProps {
  program: typeof mockPrograms[0];
  onSave: (programId: string) => void;
  isSaved: boolean;
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, onSave, isSaved }) => {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-stitch-primary border border-stitch-border rounded-lg p-6 shadow-lg hover:shadow-xl transition-all duration-300"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-stitch-accent mb-1">{program.name}</h3>
          <p className="text-stitch-sage">{program.institution}</p>
          <p className="text-sm text-stitch-sage/70">{program.location}</p>
        </div>
        <div className="text-right">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            program.type === 'CEGEP' 
              ? 'bg-blue-100 text-blue-800' 
              : 'bg-purple-100 text-purple-800'
          }`}>
            {program.type}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-stitch-sage/70">Duration</p>
          <p className="font-semibold text-stitch-accent">{program.duration}</p>
        </div>
        <div>
          <p className="text-sm text-stitch-sage/70">Tuition</p>
          <p className="font-semibold text-stitch-accent">{program.tuition}</p>
        </div>
        <div>
          <p className="text-sm text-stitch-sage/70">Employment Rate</p>
          <p className="font-semibold text-green-600">{program.employmentRate}%</p>
        </div>
        <div>
          <p className="text-sm text-stitch-sage/70">Personality Match</p>
          <p className="font-semibold text-stitch-accent">{program.hollandMatch}%</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-stitch-sage/70 mb-1">Career Alignment</p>
        <span className="inline-block bg-stitch-accent/10 text-stitch-accent px-3 py-1 rounded-full text-sm font-medium">
          {program.careerAlignment}
        </span>
      </div>

      <p className="text-stitch-sage mb-3">{program.description}</p>
      
      <div className="bg-stitch-accent/5 rounded-lg p-3 mb-4">
        <p className="text-sm font-medium text-stitch-accent mb-1">Why we recommend this:</p>
        <p className="text-sm text-stitch-sage">{program.whyRecommended}</p>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onSave(program.id)}
          className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            isSaved
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-stitch-accent text-white hover:bg-stitch-accent/90'
          }`}
        >
          {isSaved ? '✓ Saved' : 'Save Program'}
        </button>
        <button className="px-4 py-2 border border-stitch-border text-stitch-accent rounded-md hover:bg-stitch-accent/5 transition-colors text-sm font-medium">
          Learn More
        </button>
      </div>
    </motion.div>
  );
};

export default function EducationPage() {
  const [savedPrograms, setSavedPrograms] = useState<string[]>([]);

  const handleSaveProgram = (programId: string) => {
    setSavedPrograms(prev => 
      prev.includes(programId) 
        ? prev.filter(id => id !== programId)
        : [...prev, programId]
    );
  };

  return (
    <div className="min-h-screen bg-stitch-primary text-stitch-sage">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-stitch-accent mb-4">Education Programs</h1>
          <p className="text-xl text-stitch-sage max-w-3xl mx-auto">
            Discover educational programs tailored to your personality and career goals
          </p>
        </motion.div>

        {/* Personality Profile Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-stitch-primary border border-stitch-border rounded-lg p-6 mb-8"
        >
          <h2 className="text-2xl font-bold text-stitch-accent mb-4">Your Personality Profile</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="font-semibold text-stitch-accent mb-2">Holland Code: {mockPersonalityProfile.hollandCode}</h3>
              <div className="space-y-1">
                <p><strong>Primary:</strong> {mockPersonalityProfile.primaryType}</p>
                <p><strong>Secondary:</strong> {mockPersonalityProfile.secondaryType}</p>
                <p><strong>Tertiary:</strong> {mockPersonalityProfile.tertiaryType}</p>
              </div>
            </div>
            <div className="md:col-span-2">
              <h3 className="font-semibold text-stitch-accent mb-2">Personality Strengths</h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(mockPersonalityProfile.scores).map(([type, score]) => (
                  <div key={type} className="flex justify-between">
                    <span className="capitalize">{type}:</span>
                    <span className="font-medium">{score}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Programs Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-stitch-accent mb-6">Recommended Programs</h2>
          <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {mockPrograms.map((program) => (
              <ProgramCard
                key={program.id}
                program={program}
                onSave={handleSaveProgram}
                isSaved={savedPrograms.includes(program.id)}
              />
            ))}
          </div>
        </motion.div>

        {/* Career Pathways */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold text-stitch-accent mb-6">Career-Education Pathways</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {mockCareerPaths.map((path, index) => (
              <div key={index} className="bg-stitch-primary border border-stitch-border rounded-lg p-6">
                <h3 className="text-xl font-bold text-stitch-accent mb-3">{path.career}</h3>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-stitch-sage/70">Average Salary</p>
                    <p className="font-semibold text-green-600">{path.averageSalary}</p>
                  </div>
                  <div>
                    <p className="text-sm text-stitch-sage/70">Job Growth</p>
                    <p className="font-semibold text-green-600">{path.jobGrowth}</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-stitch-sage/70 mb-2">Relevant Programs:</p>
                  <div className="space-y-1">
                    {path.programs.map((program, i) => (
                      <span key={i} className="inline-block bg-stitch-accent/10 text-stitch-accent px-2 py-1 rounded text-sm mr-2 mb-1">
                        {program}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-stitch-accent/5 rounded-lg p-6"
        >
          <h2 className="text-2xl font-bold text-stitch-accent mb-4">Your Education Journey</h2>
          <div className="grid md:grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-3xl font-bold text-stitch-accent">{mockPrograms.length}</p>
              <p className="text-stitch-sage">Programs Recommended</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-stitch-accent">{savedPrograms.length}</p>
              <p className="text-stitch-sage">Programs Saved</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-stitch-accent">
                {Math.round(mockPrograms.reduce((sum, p) => sum + p.hollandMatch, 0) / mockPrograms.length)}%
              </p>
              <p className="text-stitch-sage">Average Personality Match</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}