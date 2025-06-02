import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts';
import { Recommendation } from '@/services/spaceService';
import { extractChartData } from '@/utils/chartUtils';
import NotesSection from './NotesSection';

interface RecommendationDetailProps {
  recommendation: Recommendation;
  onGenerate: () => void;
  generating: boolean;
}

const extractSkillData = (comparison: any) => {
  if (!comparison) return [];
  
  return [
    { subject: 'Creativity', A: comparison.creativity?.role_skill || 0, B: comparison.creativity?.user_skill || 0 },
    { subject: 'Leadership', A: comparison.leadership?.role_skill || 0, B: comparison.leadership?.user_skill || 0 },
    { subject: 'Digital Literacy', A: comparison.digital_literacy?.role_skill || 0, B: comparison.digital_literacy?.user_skill || 0 },
    { subject: 'Critical Thinking', A: comparison.critical_thinking?.role_skill || 0, B: comparison.critical_thinking?.user_skill || 0 },
    { subject: 'Problem Solving', A: comparison.problem_solving?.role_skill || 0, B: comparison.problem_solving?.user_skill || 0 }
  ];
};

export default function RecommendationDetail({ recommendation, onGenerate, generating }: RecommendationDetailProps) {
  return (
    <div className="p-6 rounded-lg" style={{
      backgroundColor: 'var(--card)',
      border: '1px solid var(--border)'
    }}>
      <h2 className="text-lg font-semibold mb-3" style={{ color: 'var(--text)' }}>
        {recommendation.label}
      </h2>
      <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
        {recommendation.description}
      </p>
      
      {recommendation.main_duties && (
        <div className="mb-6">
          <h3 className="text-base font-medium mb-2" style={{ color: 'var(--text)' }}>
            Main Duties
          </h3>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {recommendation.main_duties}
          </p>
        </div>
      )}

      {recommendation.skill_comparison && (
        <div className="mt-6">
          <h3 className="text-base font-medium mb-2" style={{ color: 'var(--text)' }}>
            Skill Comparison
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={extractSkillData(recommendation.skill_comparison)}>
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis dataKey="subject" style={{ fill: 'var(--text-secondary)' }} />
              <PolarRadiusAxis angle={30} domain={[0, 5]} style={{ fill: 'var(--text-secondary)' }} />
              <Radar name="Job Skills" dataKey="A" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.6} />
              <Radar name="My Skills" dataKey="B" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
              <Tooltip contentStyle={{
                backgroundColor: 'var(--card)',
                border: '1px solid var(--border)',
                borderRadius: '0.375rem',
                color: 'var(--text)'
              }} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-6">
        <h3 className="text-base font-medium mb-2" style={{ color: 'var(--text)' }}>
          Cognitive Traits & Work Characteristics
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={extractChartData(recommendation)}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--text-secondary)' }} />
            <YAxis domain={[0, 5]} tick={{ fill: 'var(--text-secondary)' }} />
            <Tooltip contentStyle={{
              backgroundColor: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: '0.375rem',
              color: 'var(--text)'
            }} />
            <Legend />
            <Bar name="Role Requirements" dataKey="role" fill="var(--accent)" />
            <Bar name="Your Traits" dataKey="user" fill="#10B981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* AI Analysis Section */}
      <div className="mt-6 pt-6" style={{ borderTop: '1px solid var(--border)' }}>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-base font-medium" style={{ color: 'var(--text)' }}>
            AI Job Analysis
          </h3>
          
          {!(recommendation.personal_analysis ||
             recommendation.entry_qualifications ||
             recommendation.suggested_improvements) && (
            <button
              onClick={onGenerate}
              disabled={generating}
              className="px-4 py-2 rounded-md text-white transition-colors"
              style={{
                backgroundColor: generating ? 'var(--text-secondary)' : 'var(--accent)',
                cursor: generating ? 'not-allowed' : 'pointer'
              }}
              onMouseEnter={(e) => {
                if (!generating) {
                  e.currentTarget.style.opacity = '0.8';
                }
              }}
              onMouseLeave={(e) => {
                if (!generating) {
                  e.currentTarget.style.opacity = '1';
                }
              }}
            >
              {generating ? (
                <span className="flex items-center">
                  <span className="animate-spin mr-2 h-4 w-4 border-t-2 border-b-2 border-white rounded-full"></span>
                  Generating...
                </span>
              ) : (
                'Generate Analysis'
              )}
            </button>
          )}
        </div>
        
        {/* Personal Analysis */}
        {recommendation.personal_analysis ? (
          <div className="mb-6 rounded-lg" style={{
            backgroundColor: 'var(--background-secondary)',
            border: '1px solid var(--border)'
          }}>
            <h3 className="text-base font-medium px-4 pb-2 pt-4" style={{ color: 'var(--text)' }}>
              Personal Analysis
            </h3>
            <p className="text-sm pb-3 pt-1 px-4" style={{ color: 'var(--text-secondary)' }}>
              {recommendation.personal_analysis}
            </p>
          </div>
        ) : generating ? (
          <div className="mb-6 rounded-lg p-4 flex justify-center" style={{
            backgroundColor: 'var(--background-secondary)',
            border: '1px solid var(--border)'
          }}>
            <span className="animate-pulse" style={{ color: 'var(--text-secondary)' }}>
              Generating personal analysis...
            </span>
          </div>
        ) : null}
        
        {/* Entry Qualifications */}
        {recommendation.entry_qualifications ? (
          <div className="mb-6 rounded-lg" style={{
            backgroundColor: 'var(--background-secondary)',
            border: '1px solid var(--border)'
          }}>
            <h3 className="text-base font-medium px-4 pb-2 pt-4" style={{ color: 'var(--text)' }}>
              Entry Qualifications
            </h3>
            <p className="text-sm pb-3 pt-1 px-4" style={{ color: 'var(--text-secondary)' }}>
              {recommendation.entry_qualifications}
            </p>
          </div>
        ) : generating ? (
          <div className="mb-6 rounded-lg p-4 flex justify-center" style={{
            backgroundColor: 'var(--background-secondary)',
            border: '1px solid var(--border)'
          }}>
            <span className="animate-pulse" style={{ color: 'var(--text-secondary)' }}>
              Generating qualifications...
            </span>
          </div>
        ) : null}
        
        {/* Suggested Improvements */}
        {recommendation.suggested_improvements ? (
          <div className="mb-6 rounded-lg" style={{
            backgroundColor: 'var(--background-secondary)',
            border: '1px solid var(--border)'
          }}>
            <h3 className="text-base font-medium px-4 pb-2 pt-4" style={{ color: 'var(--text)' }}>
              Suggested Improvements
            </h3>
            <p className="text-sm pb-3 pt-1 px-4" style={{ color: 'var(--text-secondary)' }}>
              {recommendation.suggested_improvements}
            </p>
          </div>
        ) : generating ? (
          <div className="mb-6 rounded-lg p-4 flex justify-center" style={{
            backgroundColor: 'var(--background-secondary)',
            border: '1px solid var(--border)'
          }}>
            <span className="animate-pulse" style={{ color: 'var(--text-secondary)' }}>
              Generating improvements...
            </span>
          </div>
        ) : null}
        
        {/* No Analysis Message */}
        {!(recommendation.personal_analysis ||
           recommendation.entry_qualifications ||
           recommendation.suggested_improvements ||
           generating) && (
          <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
            No LLM analysis available for this recommendation.
            Click the "Generate Analysis" button to create one.
          </div>
        )}
      </div>

      {/* Additional Details */}
      {recommendation.all_fields && (
        <div className="mt-6">
          <h3 className="text-base font-medium mb-2" style={{ color: 'var(--text)' }}>
            Additional Details
          </h3>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
            {Object.entries(recommendation.all_fields).map(([key, value]) => (
              <div key={key} className="flex gap-1">
                <span className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</span>
                <span>{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <NotesSection recommendation={recommendation} />
    </div>
  );
} 