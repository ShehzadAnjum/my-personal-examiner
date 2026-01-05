'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Download, Upload, Trash2, CheckCircle, AlertTriangle, Database, HardDrive } from 'lucide-react';

interface BackupStats {
  totalKeys: number;
  explanationKeys: number;
  cachedKeys: number;
  totalSize: string;
}

export default function BackupPage() {
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [backupComplete, setBackupComplete] = useState(false);
  const [restoreComplete, setRestoreComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Calculate localStorage stats
  const calculateStats = (): BackupStats => {
    let totalSize = 0;
    let explanationKeys = 0;
    let cachedKeys = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        const value = localStorage.getItem(key) || '';
        totalSize += key.length + value.length;

        if (key.startsWith('explanation_')) {
          explanationKeys++;
        } else if (key.startsWith('cached_')) {
          cachedKeys++;
        }
      }
    }

    return {
      totalKeys: localStorage.length,
      explanationKeys,
      cachedKeys,
      totalSize: formatBytes(totalSize * 2), // UTF-16 = 2 bytes per char
    };
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Export localStorage to JSON
  const handleExport = () => {
    try {
      const backup: Record<string, string> = {};

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.startsWith('explanation_') || key.startsWith('cached_'))) {
          const value = localStorage.getItem(key);
          if (value) {
            backup[key] = value;
          }
        }
      }

      const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `localStorage_backup_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);

      setBackupComplete(true);
      setError(null);
      setStats(calculateStats());
    } catch (err) {
      setError(`Export failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  // Import from JSON file
  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = async (e) => {
      try {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (!file) return;

        const text = await file.text();
        const backup = JSON.parse(text);

        let restoredCount = 0;
        for (const [key, value] of Object.entries(backup)) {
          if (typeof value === 'string') {
            localStorage.setItem(key, value);
            restoredCount++;
          }
        }

        setRestoreComplete(true);
        setError(null);
        setStats(calculateStats());
      } catch (err) {
        setError(`Import failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
    };

    input.click();
  };

  // Clear explanation cache only
  const handleClearCache = () => {
    if (!confirm('This will clear all cached explanations from localStorage. Continue?')) {
      return;
    }

    try {
      const keysToRemove: string[] = [];

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.startsWith('explanation_') || key.startsWith('cached_'))) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key));

      setStats(calculateStats());
      setError(null);
    } catch (err) {
      setError(`Clear failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  // Load stats on mount (useEffect to avoid SSR issues with localStorage)
  useEffect(() => {
    setStats(calculateStats());
  }, []);

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Data Backup</h1>
        <p className="text-muted-foreground">
          Backup your browser cache before system reset. This page helps you export and restore
          cached explanations stored in your browser.
        </p>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {backupComplete && (
        <Alert className="mb-6 border-green-500 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-700">Backup Complete</AlertTitle>
          <AlertDescription className="text-green-600">
            Your localStorage backup has been downloaded. Save it to the backups folder.
          </AlertDescription>
        </Alert>
      )}

      {restoreComplete && (
        <Alert className="mb-6 border-blue-500 bg-blue-50">
          <CheckCircle className="h-4 w-4 text-blue-600" />
          <AlertTitle className="text-blue-700">Restore Complete</AlertTitle>
          <AlertDescription className="text-blue-600">
            Your localStorage has been restored from the backup file.
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HardDrive className="h-5 w-5" />
            Browser Storage Stats
          </CardTitle>
          <CardDescription>
            Current state of your browser&apos;s localStorage cache
          </CardDescription>
        </CardHeader>
        <CardContent>
          {stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-muted rounded-lg text-center">
                <div className="text-2xl font-bold">{stats.totalKeys}</div>
                <div className="text-sm text-muted-foreground">Total Keys</div>
              </div>
              <div className="p-4 bg-muted rounded-lg text-center">
                <div className="text-2xl font-bold">{stats.explanationKeys}</div>
                <div className="text-sm text-muted-foreground">Explanations</div>
              </div>
              <div className="p-4 bg-muted rounded-lg text-center">
                <div className="text-2xl font-bold">{stats.cachedKeys}</div>
                <div className="text-sm text-muted-foreground">Cached Items</div>
              </div>
              <div className="p-4 bg-muted rounded-lg text-center">
                <div className="text-2xl font-bold">{stats.totalSize}</div>
                <div className="text-sm text-muted-foreground">Storage Used</div>
              </div>
            </div>
          ) : (
            <div className="text-center py-4 text-muted-foreground">
              Loading stats...
            </div>
          )}
          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={() => setStats(calculateStats())}
          >
            Refresh Stats
          </Button>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Export */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Download className="h-5 w-5" />
              Export Backup
            </CardTitle>
            <CardDescription>
              Download all cached explanations as a JSON file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleExport} className="w-full">
              <Download className="h-4 w-4 mr-2" />
              Download Backup
            </Button>
          </CardContent>
        </Card>

        {/* Import */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Upload className="h-5 w-5" />
              Restore Backup
            </CardTitle>
            <CardDescription>
              Restore from a previously downloaded backup file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleImport} variant="outline" className="w-full">
              <Upload className="h-4 w-4 mr-2" />
              Upload Backup
            </Button>
          </CardContent>
        </Card>

        {/* Clear */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Trash2 className="h-5 w-5" />
              Clear Cache
            </CardTitle>
            <CardDescription>
              Remove all cached explanations (backup first!)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleClearCache} variant="destructive" className="w-full">
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Cache
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Instructions */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Before System Reset
          </CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <ol className="list-decimal list-inside space-y-2">
            <li>Click <strong>Download Backup</strong> to export your cached explanations</li>
            <li>Save the downloaded JSON file to the <code>backups/</code> folder</li>
            <li>Run the database backup script: <code>./scripts/backup_before_reset.sh</code></li>
            <li>Verify backups are complete before proceeding with reset</li>
          </ol>
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-yellow-800 font-medium">
              After reset, you can restore your cached explanations using the Upload Backup button.
              However, if topics have changed, some cache entries may become invalid.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
