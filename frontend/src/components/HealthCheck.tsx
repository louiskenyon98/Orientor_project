import { useEffect, useState } from 'react';

export default function HealthCheck() {
  const [healthStatus, setHealthStatus] = useState<string>('checking...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
        const data = await response.json();
        console.log('Health check response:', data);
        setHealthStatus(data.status);
      } catch (err) {
        console.error('Health check failed:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setHealthStatus('error');
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h2 className="text-lg font-semibold mb-2">Backend Health Check</h2>
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${
          healthStatus === 'ok' ? 'bg-green-500' : 
          healthStatus === 'checking...' ? 'bg-yellow-500' : 
          'bg-red-500'
        }`} />
        <span>Status: {healthStatus}</span>
      </div>
      {error && (
        <div className="mt-2 text-red-500">
          Error: {error}
        </div>
      )}
      <div className="mt-2 text-sm text-gray-500">
        API URL: {process.env.NEXT_PUBLIC_API_URL}
      </div>
    </div>
  );
} 