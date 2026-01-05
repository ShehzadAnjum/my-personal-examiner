'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { clearStudentCache, getCachedStudentData, getStudentData } from '@/lib/auth/student-cache';

export default function DebugAuthPage() {
  const [cachedData, setCachedData] = useState<any>(null);
  const [apiData, setApiData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadData = () => {
    // Get cached data
    const cached = getCachedStudentData();
    setCachedData(cached);
  };

  const fetchFromApi = async () => {
    setLoading(true);
    try {
      const data = await getStudentData();
      setApiData(data);
    } catch (error) {
      setApiData({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      setLoading(false);
    }
  };

  const clearCache = () => {
    clearStudentCache();
    setCachedData(null);
    setApiData(null);
    alert('Cache cleared! Refresh the page to test.');
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Auth Debug Page</h1>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Cached Data */}
        <Card>
          <CardHeader>
            <CardTitle>Cached Data (localStorage)</CardTitle>
          </CardHeader>
          <CardContent>
            {cachedData ? (
              <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto">
                {JSON.stringify(cachedData, null, 2)}
              </pre>
            ) : (
              <p className="text-gray-600">No cached data</p>
            )}
          </CardContent>
        </Card>

        {/* API Data */}
        <Card>
          <CardHeader>
            <CardTitle>API Data (Fresh Fetch)</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={fetchFromApi} disabled={loading} className="mb-4">
              {loading ? 'Fetching...' : 'Fetch from API'}
            </Button>

            {apiData ? (
              <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto">
                {JSON.stringify(apiData, null, 2)}
              </pre>
            ) : (
              <p className="text-gray-600">Click "Fetch from API" to load</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-x-4">
          <Button onClick={loadData}>Refresh Cached Data</Button>
          <Button onClick={clearCache} variant="destructive">
            Clear Cache
          </Button>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm">
            <strong>Problem:</strong> If "is_admin" shows "true" for a regular student, the cache is corrupted.
          </p>
          <p className="text-sm">
            <strong>Solution:</strong> Click "Clear Cache" then refresh the page.
          </p>
          <p className="text-sm">
            <strong>Expected:</strong> Regular students should have "is_admin: false"
          </p>
          <p className="text-sm">
            <strong>Expected:</strong> Admin users should have "is_admin: true"
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
