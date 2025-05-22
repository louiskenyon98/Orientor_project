'use client';

import React from 'react';
import MainLayout from '@/components/layout/MainLayout';

export default function NotesPage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl md:text-4xl font-bold text-stitch-accent mb-6 font-departure">Notes</h1>
        
        <div className="bg-stitch-primary border border-stitch-border rounded-lg p-6 md:p-8 shadow-soft">
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="64px" height="64px" fill="currentColor" viewBox="0 0 256 256" className="text-stitch-sage mb-4">
              <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
            </svg>
            <h2 className="text-xl md:text-2xl font-bold text-stitch-accent mb-2 font-departure">Aucune note pour le moment</h2>
            <p className="text-stitch-sage mb-6">Prenez des notes pendant votre parcours d'apprentissage pour les consulter plus tard.</p>
            <button className="btn btn-primary">Créer une nouvelle note</button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}