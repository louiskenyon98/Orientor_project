import { CareerFitCalculator } from '../../services/careerFitCalculator';
import { UserSkills, Career, SkillLevel, CareerFitScore } from '../../types/career';

describe('CareerFitCalculator', () => {
  let calculator: CareerFitCalculator;

  beforeEach(() => {
    calculator = new CareerFitCalculator();
  });

  describe('calculateFitScore', () => {
    it('should calculate fit score based on skill overlap', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.ADVANCED, yearsOfExperience: 5 },
          { id: 'skill2', name: 'React', level: SkillLevel.INTERMEDIATE, yearsOfExperience: 3 },
          { id: 'skill3', name: 'Python', level: SkillLevel.BEGINNER, yearsOfExperience: 1 }
        ]
      };

      const career: Career = {
        id: 'career1',
        title: 'Full Stack Developer',
        requiredSkills: [
          { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' },
          { id: 'skill2', name: 'React', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' },
          { id: 'skill4', name: 'Node.js', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'medium' }
        ],
        description: 'Develop web applications',
        industryCode: 'IT',
        salaryRange: { min: 60000, max: 100000 }
      };

      const score = calculator.calculateFitScore(userSkills, career);

      expect(score).toBeGreaterThan(0);
      expect(score).toBeLessThanOrEqual(100);
      expect(score).toBeCloseTo(66.67, 1); // 2 out of 3 skills matched
    });

    it('should weight skills by importance correctly', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.ADVANCED, yearsOfExperience: 5 },
          { id: 'skill2', name: 'Docker', level: SkillLevel.BEGINNER, yearsOfExperience: 1 }
        ]
      };

      const career: Career = {
        id: 'career1',
        title: 'Senior Developer',
        requiredSkills: [
          { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill2', name: 'Docker', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'low' }
        ],
        description: 'Lead development projects',
        industryCode: 'IT',
        salaryRange: { min: 80000, max: 120000 }
      };

      const score = calculator.calculateFitScore(userSkills, career);

      // Should score high because critical skill is matched perfectly
      expect(score).toBeGreaterThan(80);
    });

    it('should handle missing skills gracefully', () => {
      const userSkills: UserSkills = {
        skills: []
      };

      const career: Career = {
        id: 'career1',
        title: 'Data Scientist',
        requiredSkills: [
          { id: 'skill1', name: 'Python', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill2', name: 'Machine Learning', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' }
        ],
        description: 'Analyze data and build ML models',
        industryCode: 'IT',
        salaryRange: { min: 90000, max: 150000 }
      };

      const score = calculator.calculateFitScore(userSkills, career);

      expect(score).toBe(0);
    });

    it('should return score between 0-100', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.EXPERT, yearsOfExperience: 10 },
          { id: 'skill2', name: 'React', level: SkillLevel.EXPERT, yearsOfExperience: 8 },
          { id: 'skill3', name: 'Node.js', level: SkillLevel.EXPERT, yearsOfExperience: 7 }
        ]
      };

      const career: Career = {
        id: 'career1',
        title: 'Junior Developer',
        requiredSkills: [
          { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.BEGINNER, importance: 'high' }
        ],
        description: 'Entry level development',
        industryCode: 'IT',
        salaryRange: { min: 40000, max: 60000 }
      };

      const score = calculator.calculateFitScore(userSkills, career);

      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });

    it('should consider user proficiency levels', () => {
      const userSkillsAdvanced: UserSkills = {
        skills: [
          { id: 'skill1', name: 'Python', level: SkillLevel.ADVANCED, yearsOfExperience: 5 }
        ]
      };

      const userSkillsBeginner: UserSkills = {
        skills: [
          { id: 'skill1', name: 'Python', level: SkillLevel.BEGINNER, yearsOfExperience: 1 }
        ]
      };

      const career: Career = {
        id: 'career1',
        title: 'Python Developer',
        requiredSkills: [
          { id: 'skill1', name: 'Python', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'critical' }
        ],
        description: 'Python development',
        industryCode: 'IT',
        salaryRange: { min: 70000, max: 100000 }
      };

      const scoreAdvanced = calculator.calculateFitScore(userSkillsAdvanced, career);
      const scoreBeginner = calculator.calculateFitScore(userSkillsBeginner, career);

      expect(scoreAdvanced).toBeGreaterThan(scoreBeginner);
    });
  });

  describe('compareCareerPaths', () => {
    it('should compare two career paths accurately', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.ADVANCED, yearsOfExperience: 5 },
          { id: 'skill2', name: 'React', level: SkillLevel.INTERMEDIATE, yearsOfExperience: 3 }
        ]
      };

      const career1: Career = {
        id: 'career1',
        title: 'Frontend Developer',
        requiredSkills: [
          { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill2', name: 'React', requiredLevel: SkillLevel.ADVANCED, importance: 'high' }
        ],
        description: 'Frontend development',
        industryCode: 'IT',
        salaryRange: { min: 70000, max: 110000 }
      };

      const career2: Career = {
        id: 'career2',
        title: 'Backend Developer',
        requiredSkills: [
          { id: 'skill3', name: 'Node.js', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill4', name: 'MongoDB', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
        ],
        description: 'Backend development',
        industryCode: 'IT',
        salaryRange: { min: 75000, max: 115000 }
      };

      const comparison = calculator.compareCareerPaths(userSkills, career1, career2);

      expect(comparison).toHaveProperty('career1Score');
      expect(comparison).toHaveProperty('career2Score');
      expect(comparison).toHaveProperty('recommendation');
      expect(comparison).toHaveProperty('skillGapAnalysis');
      expect(comparison.career1Score).toBeGreaterThan(comparison.career2Score);
    });

    it('should identify skill gaps between paths', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.INTERMEDIATE, yearsOfExperience: 2 }
        ]
      };

      const currentCareer: Career = {
        id: 'current',
        title: 'Junior Developer',
        requiredSkills: [
          { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.BEGINNER, importance: 'high' }
        ],
        description: 'Entry level',
        industryCode: 'IT',
        salaryRange: { min: 40000, max: 60000 }
      };

      const targetCareer: Career = {
        id: 'target',
        title: 'Senior Developer',
        requiredSkills: [
          { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.EXPERT, importance: 'critical' },
          { id: 'skill2', name: 'System Design', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill3', name: 'Leadership', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
        ],
        description: 'Senior role',
        industryCode: 'IT',
        salaryRange: { min: 100000, max: 150000 }
      };

      const comparison = calculator.compareCareerPaths(userSkills, currentCareer, targetCareer);

      expect(comparison.skillGapAnalysis).toBeDefined();
      expect(comparison.skillGapAnalysis.missingSkills).toHaveLength(2); // System Design and Leadership
      expect(comparison.skillGapAnalysis.skillsToImprove).toHaveLength(1); // JavaScript needs improvement
    });

    it('should calculate transition difficulty', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'Marketing', level: SkillLevel.ADVANCED, yearsOfExperience: 5 }
        ]
      };

      const currentCareer: Career = {
        id: 'current',
        title: 'Marketing Manager',
        requiredSkills: [
          { id: 'skill1', name: 'Marketing', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' }
        ],
        description: 'Marketing role',
        industryCode: 'MARKETING',
        salaryRange: { min: 60000, max: 90000 }
      };

      const targetCareer: Career = {
        id: 'target',
        title: 'Software Developer',
        requiredSkills: [
          { id: 'skill2', name: 'Programming', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'critical' },
          { id: 'skill3', name: 'Algorithms', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
        ],
        description: 'Tech role',
        industryCode: 'IT',
        salaryRange: { min: 70000, max: 110000 }
      };

      const comparison = calculator.compareCareerPaths(userSkills, currentCareer, targetCareer);

      expect(comparison.transitionDifficulty).toBe('high');
      expect(comparison.estimatedTimeToTransition).toBeGreaterThan(12); // months
    });

    it('should suggest learning priorities', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'Python', level: SkillLevel.BEGINNER, yearsOfExperience: 1 }
        ]
      };

      const currentCareer: Career = {
        id: 'current',
        title: 'Junior Analyst',
        requiredSkills: [
          { id: 'skill1', name: 'Python', requiredLevel: SkillLevel.BEGINNER, importance: 'medium' }
        ],
        description: 'Analyst role',
        industryCode: 'FINANCE',
        salaryRange: { min: 50000, max: 70000 }
      };

      const targetCareer: Career = {
        id: 'target',
        title: 'Data Scientist',
        requiredSkills: [
          { id: 'skill1', name: 'Python', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill2', name: 'Machine Learning', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' },
          { id: 'skill3', name: 'Statistics', requiredLevel: SkillLevel.ADVANCED, importance: 'high' },
          { id: 'skill4', name: 'SQL', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'medium' }
        ],
        description: 'Data Science role',
        industryCode: 'IT',
        salaryRange: { min: 90000, max: 140000 }
      };

      const comparison = calculator.compareCareerPaths(userSkills, currentCareer, targetCareer);

      expect(comparison.learningPriorities).toBeDefined();
      expect(comparison.learningPriorities[0].skill).toBe('Python'); // Improve existing skill first
      expect(comparison.learningPriorities[1].skill).toBe('Machine Learning'); // Critical skill
      expect(comparison.learningPriorities[2].skill).toBe('Statistics'); // High importance
      expect(comparison.learningPriorities[3].skill).toBe('SQL'); // Medium importance
    });
  });

  describe('rankCareerMatches', () => {
    it('should rank careers by fit score', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.ADVANCED, yearsOfExperience: 5 },
          { id: 'skill2', name: 'React', level: SkillLevel.ADVANCED, yearsOfExperience: 4 }
        ]
      };

      const careers: Career[] = [
        {
          id: 'career1',
          title: 'React Developer',
          requiredSkills: [
            { id: 'skill2', name: 'React', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' }
          ],
          description: 'React specialist',
          industryCode: 'IT',
          salaryRange: { min: 80000, max: 120000 }
        },
        {
          id: 'career2',
          title: 'Full Stack Developer',
          requiredSkills: [
            { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.ADVANCED, importance: 'high' },
            { id: 'skill2', name: 'React', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
          ],
          description: 'Full stack role',
          industryCode: 'IT',
          salaryRange: { min: 70000, max: 110000 }
        },
        {
          id: 'career3',
          title: 'Python Developer',
          requiredSkills: [
            { id: 'skill3', name: 'Python', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' }
          ],
          description: 'Python specialist',
          industryCode: 'IT',
          salaryRange: { min: 75000, max: 115000 }
        }
      ];

      const rankedCareers = calculator.rankCareerMatches(userSkills, careers);

      expect(rankedCareers).toHaveLength(3);
      expect(rankedCareers[0].career.id).toBe('career2'); // Best match - both skills
      expect(rankedCareers[1].career.id).toBe('career1'); // Good match - one critical skill
      expect(rankedCareers[2].career.id).toBe('career3'); // Poor match - no skills
      expect(rankedCareers[0].fitScore).toBeGreaterThan(rankedCareers[1].fitScore);
      expect(rankedCareers[1].fitScore).toBeGreaterThan(rankedCareers[2].fitScore);
    });

    it('should apply user preferences to ranking', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.ADVANCED, yearsOfExperience: 5 }
        ],
        preferences: {
          preferredIndustries: ['FINANCE'],
          minSalary: 80000,
          maxCommute: 30,
          remotePreference: 'preferred'
        }
      };

      const careers: Career[] = [
        {
          id: 'career1',
          title: 'JavaScript Developer - Tech',
          requiredSkills: [
            { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' }
          ],
          description: 'Tech company role',
          industryCode: 'IT',
          salaryRange: { min: 70000, max: 100000 },
          remoteOptions: 'onsite'
        },
        {
          id: 'career2',
          title: 'JavaScript Developer - Finance',
          requiredSkills: [
            { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
          ],
          description: 'Finance tech role',
          industryCode: 'FINANCE',
          salaryRange: { min: 85000, max: 120000 },
          remoteOptions: 'hybrid'
        }
      ];

      const rankedCareers = calculator.rankCareerMatches(userSkills, careers);

      // Finance role should rank higher despite lower skill match due to preferences
      expect(rankedCareers[0].career.id).toBe('career2');
      expect(rankedCareers[0].preferenceBonus).toBeGreaterThan(0);
    });

    it('should filter by minimum requirements', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'HTML', level: SkillLevel.BEGINNER, yearsOfExperience: 1 }
        ]
      };

      const careers: Career[] = [
        {
          id: 'career1',
          title: 'Senior Developer',
          requiredSkills: [
            { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.EXPERT, importance: 'critical' },
            { id: 'skill2', name: 'Architecture', requiredLevel: SkillLevel.ADVANCED, importance: 'critical' }
          ],
          description: 'Senior role',
          industryCode: 'IT',
          salaryRange: { min: 120000, max: 180000 },
          yearsExperienceRequired: 8
        },
        {
          id: 'career2',
          title: 'Junior Web Developer',
          requiredSkills: [
            { id: 'skill1', name: 'HTML', requiredLevel: SkillLevel.BEGINNER, importance: 'high' }
          ],
          description: 'Entry level',
          industryCode: 'IT',
          salaryRange: { min: 40000, max: 60000 },
          yearsExperienceRequired: 0
        }
      ];

      const options = { minimumFitScore: 30 };
      const rankedCareers = calculator.rankCareerMatches(userSkills, careers, options);

      expect(rankedCareers).toHaveLength(1);
      expect(rankedCareers[0].career.id).toBe('career2');
    });

    it('should handle tie scores consistently', () => {
      const userSkills: UserSkills = {
        skills: [
          { id: 'skill1', name: 'JavaScript', level: SkillLevel.INTERMEDIATE, yearsOfExperience: 3 }
        ]
      };

      const careers: Career[] = [
        {
          id: 'career1',
          title: 'Developer A',
          requiredSkills: [
            { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
          ],
          description: 'Role A',
          industryCode: 'IT',
          salaryRange: { min: 70000, max: 90000 }
        },
        {
          id: 'career2',
          title: 'Developer B',
          requiredSkills: [
            { id: 'skill1', name: 'JavaScript', requiredLevel: SkillLevel.INTERMEDIATE, importance: 'high' }
          ],
          description: 'Role B',
          industryCode: 'IT',
          salaryRange: { min: 75000, max: 95000 } // Higher salary as tiebreaker
        }
      ];

      const rankedCareers = calculator.rankCareerMatches(userSkills, careers);

      expect(rankedCareers[0].fitScore).toBe(rankedCareers[1].fitScore);
      expect(rankedCareers[0].career.id).toBe('career2'); // Higher salary wins tie
    });
  });
});