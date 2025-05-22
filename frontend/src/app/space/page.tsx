'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts';
import {
  fetchSavedRecommendations,
  Recommendation as SpaceServiceRecommendation,
  Note,
  deleteRecommendation,
  generateLLMAnalysis,
  LLMAnalysisInput,
  UserSkills
} from '@/services/spaceService';
import NotesSection from '@/components/space/NotesSection';
import { extractChartData } from '@/utils/chartUtils';
import { toast } from 'react-hot-toast';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';

// Define a stricter type for our components that requires certain fields
interface Recommendation extends Omit<SpaceServiceRecommendation, 'id'> {
  id: number;
  saved_at: string;
  skill_comparison?: {
    creativity: { user_skill: number; role_skill: number };
    leadership: { user_skill: number; role_skill: number };
    digital_literacy: { user_skill: number; role_skill: number };
    critical_thinking: { user_skill: number; role_skill: number };
    problem_solving: { user_skill: number; role_skill: number };
  };
  notes?: Note[];
  all_fields?: Record<string, string>;
  personal_analysis?: string;
  entry_qualifications?: string;
  suggested_improvements?: string;
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

export default function SpacePage() {
  const [recommendations, setRecommendations] = useState<SpaceServiceRecommendation[]>([]);
  const [selectedRecommendation, setSelectedRecommendation] = useState<SpaceServiceRecommendation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingAnalysis, setIsGeneratingAnalysis] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    console.log('Space page mounted, pathname:', pathname);
  }, [pathname]);

  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchSavedRecommendations();
        console.log('Recommendations from API:', data);
        setRecommendations(data);
      } catch (err) {
        console.error('Error loading recommendations:', err);
        setError('Failed to load recommendations. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadRecommendations();
  }, []);

  const handleRecommendationSelect = (recommendation: SpaceServiceRecommendation) => {
    setSelectedRecommendation(recommendation);
  };

  // Fonction pour générer l'analyse LLM pour une recommandation
  const handleGenerateLLMAnalysis = async () => {
    if (!selectedRecommendation) return;

    try {
      setIsGeneratingAnalysis(true);
      
      // Exemple de profil utilisateur - dans une application réelle,
      // ces données viendraient du profil de l'utilisateur connecté
      const userProfile = {
        skills: {
          creativity: 3,
          leadership: 4,
          digital_literacy: 4,
          critical_thinking: 3,
          problem_solving: 4,
          analytical_thinking: 3,
          attention_to_detail: 4,
          collaboration: 3,
          adaptability: 4,
          independence: 3,
          evaluation: 3,
          decision_making: 4,
          stress_tolerance: 3
        } as UserSkills,
        experience: "5 ans d'expérience en développement web",
        education: "Master en informatique",
        interests: "Intelligence artificielle, développement web, UX/UI design"
      };

      // Préparer les données pour l'analyse LLM
      const analysisInput: LLMAnalysisInput = {
        oasis_code: selectedRecommendation.oasis_code,
        job_description: selectedRecommendation.description || '',
        user_profile: userProfile
      };

      // Générer l'analyse LLM
      const analysisResult = await generateLLMAnalysis(analysisInput);

      // Mettre à jour la recommandation sélectionnée avec les résultats de l'analyse
      const updatedRecommendation = {
        ...selectedRecommendation,
        personal_analysis: analysisResult.personal_analysis,
        entry_qualifications: analysisResult.entry_qualifications,
        suggested_improvements: analysisResult.suggested_improvements
      };

      setSelectedRecommendation(updatedRecommendation);

      // Mettre également à jour la recommandation dans la liste
      setRecommendations(prevRecommendations =>
        prevRecommendations.map(rec =>
          rec.id === selectedRecommendation.id ? updatedRecommendation : rec
        )
      );

      toast.success('Analyse LLM générée avec succès');
    } catch (error) {
      console.error('Erreur lors de la génération de l\'analyse LLM:', error);
      toast.error('Échec de la génération de l\'analyse LLM');
    } finally {
      setIsGeneratingAnalysis(false);
    }
  };

  const handleDeleteRecommendation = async (recommendationId: number) => {
    try {
      await deleteRecommendation(recommendationId);
      setRecommendations(prev => prev.filter(rec => rec.id !== recommendationId));
      if (selectedRecommendation?.id === recommendationId) {
        setSelectedRecommendation(null);
      }
      toast.success('Recommendation deleted successfully');
    } catch (err) {
      console.error('Error deleting recommendation:', err);
      toast.error('Failed to delete recommendation');
    }
  };

  return (
    <MainLayout>
      <div className="w-full">
        <h1 className="text-2xl font-bold mb-6 text-stitch-accent">My Space</h1>
        
        <div className="gap-1 flex flex-1 justify-center">
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-stitch-accent"></div>
            </div>
          ) : error ? (
            <div className="text-red-500 text-center">{error}</div>
          ) : recommendations.length === 0 ? (
            <div className="text-center text-stitch-sage">No saved recommendations yet.</div>
          ) : (
            <>
              {/* Sidebar avec liste des emplois */}
              <div className="flex flex-col w-80">
                <h2 className="text-xl font-semibold mb-4 text-stitch-accent">Saved Recommendations</h2>
                <div className="space-y-3">
                  {recommendations.map((rec) => (
                    <div
                      key={rec.id}
                      className={`p-4 rounded-lg cursor-pointer ${
                        selectedRecommendation?.id === rec.id
                          ? 'bg-stitch-primary/50 border border-stitch-border'
                          : 'bg-stitch-primary/30 border border-stitch-border hover:border-stitch-accent/50'
                      }`}
                    >
                      <div onClick={() => handleRecommendationSelect(rec)}>
                        <h3 className="font-medium text-stitch-accent">{rec.label}</h3>
                        <p className="text-sm text-stitch-sage">{rec.oasis_code}</p>
                      </div>
                      <button
                        onClick={() => rec.id && handleDeleteRecommendation(rec.id)}
                        className="mt-2 text-stitch-sage hover:text-red-400 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Contenu principal */}
              <div className="flex flex-col max-w-[960px] flex-1 ml-6">
                {selectedRecommendation ? (
                  <div className="bg-stitch-primary/30 p-6 rounded-lg border border-stitch-border">
                    <h2 className="text-2xl font-bold mb-4 text-stitch-accent">{selectedRecommendation.label}</h2>
                    <p className="text-stitch-sage mb-4">{selectedRecommendation.description}</p>
                    
                    {selectedRecommendation.main_duties && (
                      <div className="mb-6">
                        <h3 className="text-lg font-semibold mb-2 text-stitch-accent">Main Duties</h3>
                        <p className="text-stitch-sage">{selectedRecommendation.main_duties}</p>
                      </div>
                    )}

                    {selectedRecommendation.skill_comparison && (
                      <div className="mt-8">
                        <h3 className="text-lg font-semibold mb-2 text-stitch-accent">Skill Comparison</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <RadarChart data={extractSkillData(selectedRecommendation.skill_comparison)}>
                            <PolarGrid stroke="#374151" />
                            <PolarAngleAxis dataKey="subject" stroke="#6B7280" />
                            <PolarRadiusAxis angle={30} domain={[0, 5]} stroke="#6B7280" />
                            <Radar name="Job Skills" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                            <Radar name="My Skills" dataKey="B" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '0.375rem', color: '#F3F4F6' }} />
                            <Legend />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    <div className="mt-8">
                      <h3 className="text-lg font-semibold mb-2 text-stitch-accent">Cognitive Traits & Work Characteristics</h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                          data={extractChartData(selectedRecommendation)}
                          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                          <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6B7280' }} />
                          <YAxis domain={[0, 5]} tick={{ fill: '#6B7280' }} />
                          <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '0.375rem', color: '#F3F4F6' }} />
                          <Legend />
                          <Bar name="Role Requirements" dataKey="role" fill="#8884d8" />
                          <Bar name="Your Traits" dataKey="user" fill="#82ca9d" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Section d'analyse LLM */}
                    <div className="mt-8 border-t border-stitch-border pt-6">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold text-stitch-accent">AI Job Analysis</h3>
                        
                        {/* Bouton pour générer l'analyse LLM si elle n'existe pas */}
                        {!(selectedRecommendation.personal_analysis ||
                           selectedRecommendation.entry_qualifications ||
                           selectedRecommendation.suggested_improvements) && (
                          <button
                            onClick={handleGenerateLLMAnalysis}
                            disabled={isGeneratingAnalysis}
                            className={`px-4 py-2 rounded-md text-white transition-colors ${
                              isGeneratingAnalysis
                                ? 'bg-stitch-primary/70 cursor-not-allowed'
                                : 'bg-stitch-accent hover:bg-stitch-accent/80'
                            }`}
                          >
                            {isGeneratingAnalysis ? (
                              <span className="flex items-center">
                                <span className="animate-spin mr-2 h-4 w-4 border-t-2 border-b-2 border-white rounded-full"></span>
                                Génération en cours...
                              </span>
                            ) : (
                              'Générer l\'analyse LLM'
                            )}
                          </button>
                        )}
                      </div>
                      
                      {/* Affichage de l'analyse personnelle */}
                      {selectedRecommendation.personal_analysis ? (
                        <div className="mb-6 bg-stitch-primary/20 rounded-lg border border-stitch-border">
                          <h3 className="text-stitch-accent text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">
                            Personal Analysis
                          </h3>
                          <p className="text-stitch-sage text-base font-normal leading-normal pb-3 pt-1 px-4">
                            {selectedRecommendation.personal_analysis}
                          </p>
                        </div>
                      ) : isGeneratingAnalysis ? (
                        <div className="mb-6 bg-stitch-primary/20 rounded-lg border border-stitch-border p-4 flex justify-center">
                          <span className="animate-pulse text-stitch-sage">Génération de l'analyse personnelle...</span>
                        </div>
                      ) : null}
                      
                      {/* Affichage des qualifications requises */}
                      {selectedRecommendation.entry_qualifications ? (
                        <div className="mb-6 bg-stitch-primary/20 rounded-lg border border-stitch-border">
                          <h3 className="text-stitch-accent text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">
                            Entry Qualifications
                          </h3>
                          <p className="text-stitch-sage text-base font-normal leading-normal pb-3 pt-1 px-4">
                            {selectedRecommendation.entry_qualifications}
                          </p>
                        </div>
                      ) : isGeneratingAnalysis ? (
                        <div className="mb-6 bg-stitch-primary/20 rounded-lg border border-stitch-border p-4 flex justify-center">
                          <span className="animate-pulse text-stitch-sage">Génération des qualifications requises...</span>
                        </div>
                      ) : null}
                      
                      {/* Affichage des suggestions d'amélioration */}
                      {selectedRecommendation.suggested_improvements ? (
                        <div className="mb-6 bg-stitch-primary/20 rounded-lg border border-stitch-border">
                          <h3 className="text-stitch-accent text-lg font-bold leading-tight tracking-[-0.015em] px-4 pb-2 pt-4">
                            Suggested Improvements
                          </h3>
                          <p className="text-stitch-sage text-base font-normal leading-normal pb-3 pt-1 px-4">
                            {selectedRecommendation.suggested_improvements}
                          </p>
                        </div>
                      ) : isGeneratingAnalysis ? (
                        <div className="mb-6 bg-stitch-primary/20 rounded-lg border border-stitch-border p-4 flex justify-center">
                          <span className="animate-pulse text-stitch-sage">Génération des suggestions d'amélioration...</span>
                        </div>
                      ) : null}
                      
                      {/* Message si aucune analyse n'est disponible et qu'aucune génération n'est en cours */}
                      {!(selectedRecommendation.personal_analysis ||
                         selectedRecommendation.entry_qualifications ||
                         selectedRecommendation.suggested_improvements ||
                         isGeneratingAnalysis) && (
                        <div className="text-center text-stitch-sage py-8">
                          Aucune analyse LLM disponible pour cette recommandation.
                          Cliquez sur le bouton "Générer l'analyse LLM" pour en créer une.
                        </div>
                      )}
                    </div>

                    {selectedRecommendation.all_fields && (
                      <div className="mt-6">
                        <h3 className="text-lg font-semibold mb-2 text-stitch-accent">Additional Details</h3>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-stitch-sage">
                          {Object.entries(selectedRecommendation.all_fields).map(([key, value]) => (
                            <div key={key} className="flex gap-1">
                              <span className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</span>
                              <span>{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <NotesSection
                      recommendation={selectedRecommendation}
                    />
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-stitch-sage text-lg">Select a recommendation to view details</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </MainLayout>
  );
}