'use client';
import LandingPage from '@/components/landing/LandingPage';
import MainLayout from '@/components/layout/MainLayout';
import HealthCheck from '@/components/HealthCheck';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const navigateToSpace = () => {
    console.log('Navigating to /space from home');
    router.push('/space');
  };

  const navigateToTreePath = () => {
    console.log('Navigating to /tree-path from home');
    router.push('/tree-path');
  };

  return (
    <MainLayout showNav={false}>
      <HealthCheck />
      <LandingPage />
      <main className="flex min-h-screen flex-col items-center justify-between p-24">
        <div className="z-10 w-full max-w-5xl items-center justify-between text-sm lg:flex">
          <h1 className="text-4xl font-bold mb-8">Welcome to Navigo</h1>
          
          <div className="space-y-4">
            <button 
              onClick={navigateToSpace}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 mr-4"
            >
              Test Space Navigation
            </button>
            
            <button 
              onClick={navigateToTreePath}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Test Tree Path Navigation
            </button>
          </div>
        </div>
      </main>
    </MainLayout>
  );
}