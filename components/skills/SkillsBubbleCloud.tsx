import React, { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles } from 'lucide-react';

interface Skill {
  id: string;
  name: string;
  level: number;
  category: 'technical' | 'soft' | 'creative' | 'leadership' | 'analytical';
  growth: number;
}

interface SkillsBubbleCloudProps {
  skills?: Skill[];
  className?: string;
}

const defaultSkills: Skill[] = [
  { id: '1', name: 'Problem Solving', level: 85, category: 'analytical', growth: 12 },
  { id: '2', name: 'Leadership', level: 78, category: 'leadership', growth: 15 },
  { id: '3', name: 'Web Development', level: 92, category: 'technical', growth: 8 },
  { id: '4', name: 'Communication', level: 88, category: 'soft', growth: 10 },
  { id: '5', name: 'Creative Thinking', level: 75, category: 'creative', growth: 18 },
  { id: '6', name: 'Data Analysis', level: 82, category: 'analytical', growth: 20 },
  { id: '7', name: 'Team Management', level: 70, category: 'leadership', growth: 25 },
  { id: '8', name: 'JavaScript', level: 90, category: 'technical', growth: 5 },
  { id: '9', name: 'Design Thinking', level: 68, category: 'creative', growth: 22 },
  { id: '10', name: 'Public Speaking', level: 65, category: 'soft', growth: 30 }
];

const categoryColors = {
  technical: 'bg-blue-500 hover:bg-blue-600 text-white',
  soft: 'bg-green-500 hover:bg-green-600 text-white', 
  creative: 'bg-purple-500 hover:bg-purple-600 text-white',
  leadership: 'bg-red-500 hover:bg-red-600 text-white',
  analytical: 'bg-yellow-500 hover:bg-yellow-600 text-white'
};

const SkillsBubbleCloud: React.FC<SkillsBubbleCloudProps> = ({ 
  skills = defaultSkills, 
  className = '' 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate bubble size based on skill level
  const getBubbleSize = (level: number) => {
    const minSize = 60;
    const maxSize = 120;
    return minSize + (level / 100) * (maxSize - minSize);
  };

  // Get top 5 skills by level
  const topSkills = [...skills]
    .sort((a, b) => b.level - a.level)
    .slice(0, 5);

  // Generate random but deterministic positions for bubbles
  const generatePosition = (index: number, total: number) => {
    const angle = (index / total) * 2 * Math.PI;
    const radius = 80 + Math.sin(index * 1.5) * 40;
    const centerX = 50;
    const centerY = 50;
    
    return {
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius,
    };
  };

  // Animation positions for staggered entrance
  const positions = topSkills.map((_, index) => generatePosition(index, topSkills.length));

  return (
    <Card className={`hover:shadow-lg transition-all duration-300 ${className}`}>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center text-xl">
          <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
          Top Skills Cloud
        </CardTitle>
        <p className="text-sm text-gray-600">
          Your strongest competencies visualized
        </p>
      </CardHeader>
      <CardContent>
        <div 
          ref={containerRef}
          className="relative w-full h-80 overflow-hidden rounded-lg bg-gradient-to-br from-gray-50 to-gray-100"
          style={{ perspective: '1000px' }}
        >
          {topSkills.map((skill, index) => {
            const position = positions[index];
            const size = getBubbleSize(skill.level);
            
            return (
              <div
                key={skill.id}
                className={`absolute transform transition-all duration-700 ease-out cursor-pointer group ${
                  categoryColors[skill.category]
                }`}
                style={{
                  left: `${position.x}%`,
                  top: `${position.y}%`,
                  width: `${size}px`,
                  height: `${size}px`,
                  transform: `translate(-50%, -50%)`,
                  animationDelay: `${index * 200}ms`,
                  borderRadius: '50%',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                }}
              >
                <div className="w-full h-full rounded-full flex flex-col items-center justify-center p-2 group-hover:scale-110 transition-transform duration-300">
                  <div className="text-center">
                    <div className="font-bold text-xs sm:text-sm mb-1 leading-tight">
                      {skill.name}
                    </div>
                    <div className="text-xs opacity-90">
                      {skill.level}%
                    </div>
                    {skill.growth > 15 && (
                      <div className="text-xs mt-1 opacity-75 font-medium">
                        🚀 +{skill.growth}%
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Floating growth indicator for high-growth skills */}
                {skill.growth > 20 && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center text-xs font-bold text-white animate-pulse">
                    ↗
                  </div>
                )}
              </div>
            );
          })}
          
          {/* Connecting lines between related skills */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-30">
            {topSkills.map((skill, index) => {
              const nextIndex = (index + 1) % topSkills.length;
              const pos1 = positions[index];
              const pos2 = positions[nextIndex];
              
              return (
                <line
                  key={`line-${index}`}
                  x1={`${pos1.x}%`}
                  y1={`${pos1.y}%`}
                  x2={`${pos2.x}%`}
                  y2={`${pos2.y}%`}
                  stroke="#6B7280"
                  strokeWidth="1"
                  strokeDasharray="4,4"
                  className="animate-pulse"
                />
              );
            })}
          </svg>
        </div>
        
        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-2">
          {Object.entries(categoryColors).map(([category, colorClass]) => {
            const skillsInCategory = topSkills.filter(s => s.category === category);
            if (skillsInCategory.length === 0) return null;
            
            return (
              <Badge 
                key={category} 
                variant="outline" 
                className={`${colorClass} border-transparent text-xs`}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)} 
                ({skillsInCategory.length})
              </Badge>
            );
          })}
        </div>
        
        {/* Quick stats */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-blue-600">
              {Math.round(topSkills.reduce((sum, s) => sum + s.level, 0) / topSkills.length)}%
            </div>
            <div className="text-xs text-gray-600">Avg. Level</div>
          </div>
          <div>
            <div className="text-lg font-bold text-green-600">
              +{Math.round(topSkills.reduce((sum, s) => sum + s.growth, 0) / topSkills.length)}%
            </div>
            <div className="text-xs text-gray-600">Avg. Growth</div>
          </div>
          <div>
            <div className="text-lg font-bold text-purple-600">
              {topSkills.filter(s => s.level > 80).length}
            </div>
            <div className="text-xs text-gray-600">Mastered</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SkillsBubbleCloud;