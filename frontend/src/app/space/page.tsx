'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import Sidebar from '@/components/space/Sidebar';
import RecommendationDetail from '@/components/space/RecommendationDetail';
import { fetchSavedRecommendations, deleteRecommendation, generateLLMAnalysisForRecommendation } from '@/services/spaceService';
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
    if (!selected || !selected.id) return;
    try {
      setGenerating(true);
      const updatedRecommendation = await generateLLMAnalysisForRecommendation(selected.id);
      setSelected(updatedRecommendation);
      setRecommendations(prev => prev.map(r => (r.id === updatedRecommendation.id ? updatedRecommendation : r)));
      toast.success('LLM analysis generated successfully');
    } catch (err) {
      console.error('Error generating LLM analysis:', err);
      toast.error('Failed to generate analysis');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <MainLayout>
      <div className="flex min-h-screen font-inter" style={{
        backgroundColor: 'var(--background)',
        color: 'var(--text)'
      }}>
        <aside className="w-52 shrink-0 border-r" style={{
          borderColor: 'var(--border)',
          backgroundColor: 'var(--background-secondary)'
        }}>
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
          <h1 className="text-xl font-semibold mb-6 tracking-tight" style={{ color: 'var(--text)' }}>
            Saved Recommendations
          </h1>
          {selected ? (
            <RecommendationDetail
              recommendation={selected}
              onGenerate={handleGenerate}
              generating={generating}
            />
          ) : (
            <div className="text-base text-center mt-20" style={{ color: 'var(--text-secondary)' }}>
              Select a recommendation to view details.
            </div>
          )}
        </main>
      </div>
    </MainLayout>  );
}
