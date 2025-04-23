import { useEffect, useState } from 'react';

const HealthCheck = () => {
  const [status, setStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'ok') {
            setStatus('healthy');
            setError(null);
          } else {
            setStatus('unhealthy');
            setError('Unexpected response format');
          }
        } else {
          setStatus('unhealthy');
          setError(`HTTP error! status: ${response.status}`);
        }
      } catch (err) {
        setStatus('unhealthy');
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
      }
    };

    checkHealth();
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Backend Health Status</h2>
      <div className="flex items-center space-x-2">
        <div
          className={`w-3 h-3 rounded-full ${
            status === 'checking'
              ? 'bg-yellow-500'
              : status === 'healthy'
              ? 'bg-green-500'
              : 'bg-red-500'
          }`}
        />
        <span className="font-medium">
          {status === 'checking'
            ? 'Checking...'
            : status === 'healthy'
            ? 'Healthy'
            : 'Unhealthy'}
        </span>
      </div>
      {error && (
        <div className="mt-2 text-red-500">
          <p className="text-sm">Error: {error}</p>
        </div>
      )}
    </div>
  );
};

export default HealthCheck; 