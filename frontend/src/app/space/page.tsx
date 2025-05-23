'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import Sidebar from '@/components/space/Sidebar';
import RecommendationDetail from '@/components/space/RecommendationDetail';
import { fetchSavedRecommendations, deleteRecommendation, generateLLMAnalysis } from '@/services/spaceService';
import type { Recommendation } from '@/services/spaceService';
import { toast } from 'react-hot-toast';

export default function SpacePage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    console.log('Mounted at:', pathname);
  }, [pathname]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchSavedRecommendations();
        setRecommendations(data);
      } catch (err) {
        setError('Could not fetch data.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSelect = (rec: Recommendation) => setSelected(rec);

  const handleDelete = async (id: number) => {
    try {
      await deleteRecommendation(id);
      setRecommendations(prev => prev.filter(r => r.id !== id));
      if (selected?.id === id) setSelected(null);
      toast.success('Deleted');
    } catch {
      toast.error('Failed to delete');
    }
  };

  const handleGenerate = async () => {
    if (!selected) return;
    try {
      setGenerating(true);
      const analysis = await generateLLMAnalysis({
        oasis_code: selected.oasis_code,
        job_description: selected.description ?? '',
        user_profile: {
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
          },
          experience: "5 ans d'expérience en développement web",
          education: "Master en informatique",
          interests: 'IA, développement web, UX/UI'
        }
      });
      const updated = { ...selected, ...analysis };
      setSelected(updated);
      setRecommendations(prev => prev.map(r => (r.id === updated.id ? updated : r)));
      toast.success('LLM analysis ready');
    } catch (err) {
      toast.error('Failed to generate');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <MainLayout>
      <div className="flex min-h-screen bg-white text-gray-800 font-inter">
        <aside className="w-52 shrink-0 border-r border-gray-200 bg-white">
          <Sidebar
            items={recommendations}
            selectedId={selected?.id}
            onSelect={handleSelect}
            onDelete={handleDelete}
            loading={loading}
            error={error}
          />
        </aside>
        <main className="flex-1 px-10 py-6 overflow-y-auto">
          <h1 className="text-xl font-semibold mb-6 tracking-tight">Saved Recommendations</h1>
          {selected ? (
            <RecommendationDetail
              recommendation={selected}
              onGenerate={handleGenerate}
              generating={generating}
            />
          ) : (
            <div className="text-gray-600 text-base text-center mt-20">Select a recommendation to view details.</div>
          )}
        </main>
      </div>
    </MainLayout>  );
}
