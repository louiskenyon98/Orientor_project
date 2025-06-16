import React, { useState, useEffect } from 'react';
import { ProgramRecommendation, ProgramRecommendationsResponse, getProgramRecommendationsForGoal } from '@/services/programRecommendationsService';

interface ProgramRecommendationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  goalId: number;
  jobTitle: string;
}

const ProgramRecommendationsModal: React.FC<ProgramRecommendationsModalProps> = ({
  isOpen,
  onClose,
  goalId,
  jobTitle
}) => {
  const [recommendations, setRecommendations] = useState<ProgramRecommendation[]>([]);
  const [goalInfo, setGoalInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProgram, setSelectedProgram] = useState<ProgramRecommendation | null>(null);

  useEffect(() => {
    if (isOpen && goalId) {
      fetchRecommendations();
    }
  }, [isOpen, goalId]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response: ProgramRecommendationsResponse = await getProgramRecommendationsForGoal(goalId);
      setRecommendations(response.recommendations);
      setGoalInfo(response.goal_info);
    } catch (err: any) {
      setError(err.message || 'Failed to load program recommendations');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return '#10b981'; // Green
    if (score >= 0.6) return '#f59e0b'; // Amber
    return '#6b7280'; // Gray
  };

  const getMatchScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Moderate Match';
  };

  const formatCost = (cost?: number) => {
    if (!cost) return 'Cost varies';
    if (cost < 1000) return `$${cost}/semester`;
    return `$${cost.toLocaleString()}/year`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="border-b border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                🎓 Educational Pathways
              </h2>
              <p className="text-gray-600 mt-1">
                Programs for: <span className="font-semibold">{jobTitle}</span>
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
            </div>
          ) : error ? (
            <div className="p-6">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700">⚠️ {error}</p>
                <button
                  onClick={fetchRecommendations}
                  className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          ) : recommendations.length === 0 ? (
            <div className="p-6 text-center">
              <div className="text-gray-500 mb-4">
                <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <h3 className="text-lg font-semibold mb-2">No Programs Found</h3>
                <p>We couldn't find any educational programs matching this career goal at the moment.</p>
              </div>
            </div>
          ) : (
            <div className="p-6">
              {/* Goal Information */}
              {goalInfo && (
                <div className="bg-blue-50 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-blue-900 mb-2">Career Goal Details</h3>
                  <div className="text-sm text-blue-800">
                    <p><strong>Target Role:</strong> {goalInfo.job_title}</p>
                    {goalInfo.target_date && (
                      <p><strong>Target Date:</strong> {new Date(goalInfo.target_date).toLocaleDateString()}</p>
                    )}
                    {goalInfo.notes && (
                      <p><strong>Notes:</strong> {goalInfo.notes}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Program Recommendations */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Recommended Programs ({recommendations.length} found)
                </h3>
                
                {recommendations.map((program) => (
                  <div
                    key={program.id}
                    className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => setSelectedProgram(selectedProgram?.id === program.id ? null : program)}
                  >
                    {/* Program Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="text-lg font-semibold text-gray-900">
                            {program.program_name}
                          </h4>
                          <span
                            className="px-2 py-1 rounded-full text-xs font-medium text-white"
                            style={{ backgroundColor: getMatchScoreColor(program.match_score) }}
                          >
                            {Math.round(program.match_score * 100)}% - {getMatchScoreLabel(program.match_score)}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                          <span className="flex items-center gap-1">
                            🏛️ {program.institution}
                          </span>
                          <span className="flex items-center gap-1">
                            📍 {program.location.city}, {program.location.province}
                          </span>
                          <span className="flex items-center gap-1">
                            ⏱️ {program.duration}
                          </span>
                          <span className="flex items-center gap-1">
                            💰 {formatCost(program.cost_estimate)}
                          </span>
                        </div>

                        <p className="text-gray-700 text-sm leading-relaxed">
                          {program.relevance_explanation}
                        </p>
                      </div>
                      
                      <div className="ml-4">
                        <svg 
                          className={`w-5 h-5 text-gray-400 transition-transform ${
                            selectedProgram?.id === program.id ? 'rotate-180' : ''
                          }`} 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {selectedProgram?.id === program.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
                        {/* Program Code */}
                        {program.program_code && (
                          <div>
                            <h5 className="font-medium text-gray-900 mb-1">Program Code</h5>
                            <p className="text-sm text-gray-600">{program.program_code}</p>
                          </div>
                        )}

                        {/* Admission Requirements */}
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">Admission Requirements</h5>
                          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                            {program.admission_requirements.map((req, index) => (
                              <li key={index}>{req}</li>
                            ))}
                          </ul>
                        </div>

                        {/* Career Outcomes */}
                        <div>
                          <h5 className="font-medium text-gray-900 mb-2">Career Outcomes</h5>
                          <div className="flex flex-wrap gap-2">
                            {program.career_outcomes.map((outcome, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs"
                              >
                                {outcome}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Intake Dates */}
                        {program.intake_dates.length > 0 && (
                          <div>
                            <h5 className="font-medium text-gray-900 mb-2">Next Intake Dates</h5>
                            <div className="flex flex-wrap gap-2">
                              {program.intake_dates.map((date, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                                >
                                  📅 {date}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Contact Information */}
                        <div className="flex gap-3 pt-3">
                          {program.website_url && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                window.open(program.website_url, '_blank');
                              }}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                            >
                              🌐 Visit Website
                            </button>
                          )}
                          
                          {program.contact_info.email && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                window.open(`mailto:${program.contact_info.email}`, '_blank');
                              }}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                            >
                              ✉️ Contact
                            </button>
                          )}
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              // TODO: Implement save functionality
                              alert('Save functionality coming soon!');
                            }}
                            className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm"
                          >
                            💾 Save Program
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              📍 Showing programs available in Quebec
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgramRecommendationsModal;