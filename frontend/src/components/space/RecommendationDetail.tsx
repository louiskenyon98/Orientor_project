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
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      <h2 className="text-lg font-semibold mb-3 text-gray-900">{recommendation.label}</h2>
      <p className="text-sm text-gray-600 mb-4">{recommendation.description}</p>
      
      {recommendation.main_duties && (
        <div className="mb-6">
          <h3 className="text-base font-medium mb-2 text-gray-900">Main Duties</h3>
          <p className="text-sm text-gray-600">{recommendation.main_duties}</p>
        </div>
      )}

      {recommendation.skill_comparison && (
        <div className="mt-6">
          <h3 className="text-base font-medium mb-2 text-gray-900">Skill Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={extractSkillData(recommendation.skill_comparison)}>
              <PolarGrid stroke="#E5E7EB" />
              <PolarAngleAxis dataKey="subject" stroke="#6B7280" />
              <PolarRadiusAxis angle={30} domain={[0, 5]} stroke="#6B7280" />
              <Radar name="Job Skills" dataKey="A" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
              <Radar name="My Skills" dataKey="B" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
              <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '0.375rem', color: '#374151' }} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="mt-6">
        <h3 className="text-base font-medium mb-2 text-gray-900">Cognitive Traits & Work Characteristics</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={extractChartData(recommendation)}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6B7280' }} />
            <YAxis domain={[0, 5]} tick={{ fill: '#6B7280' }} />
            <Tooltip contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '0.375rem', color: '#374151' }} />
            <Legend />
            <Bar name="Role Requirements" dataKey="role" fill="#3B82F6" />
            <Bar name="Your Traits" dataKey="user" fill="#10B981" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* AI Analysis Section */}
      <div className="mt-6 border-t border-gray-200 pt-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-base font-medium text-gray-900">AI Job Analysis</h3>
          
          {!(recommendation.personal_analysis ||
             recommendation.entry_qualifications ||
             recommendation.suggested_improvements) && (
            <button
              onClick={onGenerate}
              disabled={generating}
              className={`px-4 py-2 rounded-md text-white transition-colors ${
                generating
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600'
              }`}
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
          <div className="mb-6 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-base font-medium text-gray-900 px-4 pb-2 pt-4">
              Personal Analysis
            </h3>
            <p className="text-sm text-gray-600 pb-3 pt-1 px-4">
              {recommendation.personal_analysis}
            </p>
          </div>
        ) : generating ? (
          <div className="mb-6 bg-gray-50 rounded-lg border border-gray-200 p-4 flex justify-center">
            <span className="animate-pulse text-gray-600">Generating personal analysis...</span>
          </div>
        ) : null}
        
        {/* Entry Qualifications */}
        {recommendation.entry_qualifications ? (
          <div className="mb-6 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-base font-medium text-gray-900 px-4 pb-2 pt-4">
              Entry Qualifications
            </h3>
            <p className="text-sm text-gray-600 pb-3 pt-1 px-4">
              {recommendation.entry_qualifications}
            </p>
          </div>
        ) : generating ? (
          <div className="mb-6 bg-gray-50 rounded-lg border border-gray-200 p-4 flex justify-center">
            <span className="animate-pulse text-gray-600">Generating qualifications...</span>
          </div>
        ) : null}
        
        {/* Suggested Improvements */}
        {recommendation.suggested_improvements ? (
          <div className="mb-6 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-base font-medium text-gray-900 px-4 pb-2 pt-4">
              Suggested Improvements
            </h3>
            <p className="text-sm text-gray-600 pb-3 pt-1 px-4">
              {recommendation.suggested_improvements}
            </p>
          </div>
        ) : generating ? (
          <div className="mb-6 bg-gray-50 rounded-lg border border-gray-200 p-4 flex justify-center">
            <span className="animate-pulse text-gray-600">Generating improvements...</span>
          </div>
        ) : null}
        
        {/* No Analysis Message */}
        {!(recommendation.personal_analysis ||
           recommendation.entry_qualifications ||
           recommendation.suggested_improvements ||
           generating) && (
          <div className="text-center text-gray-600 py-8">
            No LLM analysis available for this recommendation.
            Click the "Generate Analysis" button to create one.
          </div>
        )}
      </div>

      {/* Additional Details */}
      {recommendation.all_fields && (
        <div className="mt-6">
          <h3 className="text-base font-medium mb-2 text-gray-900">Additional Details</h3>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-600">
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