'use client';
import LandingPage from '@/components/landing/LandingPage';
import MainLayout from '@/components/layout/MainLayout';
import HealthCheck from '@/components/HealthCheck';

export default function Home() {
  return (
    <MainLayout showNav={false}>
      <HealthCheck />
      <LandingPage />
    </MainLayout>
  );
}