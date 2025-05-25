'use client';
import { useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import SettingsPanel from '@/components/settings/SettingsPanel';

export default function SettingsPage() {
  useEffect(() => {
    document.title = 'Paramètres | Navigo';
  }, []);

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-stitch-sage mb-6">Paramètres</h1>
        <p className="text-stitch-sage mb-8">
          Personnalisez l'apparence de votre plateforme en modifiant la typographie et les couleurs.
          Vos préférences seront sauvegardées automatiquement.
        </p>
        
        <SettingsPanel className="mb-8" />
      </div>
    </MainLayout>
  );
}