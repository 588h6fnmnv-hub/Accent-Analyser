'use client';

import React, { useEffect, useState } from 'react';
import { Navigation } from '../../components/Navigation';
import { HistoryTable } from '../../components/HistoryTable';
import { HistoryRecord } from '../../types/voicelens';
import { apiClient } from '../../lib/api';

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isDark, setIsDark] = useState<boolean>(true);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (typeof document !== 'undefined') {
      if (isDark) {
        document.documentElement.classList.remove('dark');
      } else {
        document.documentElement.classList.add('dark');
      }
    }
  };

  useEffect(() => {
    async function loadHistory() {
      try {
        const historyData = await apiClient.getHistory();
        setRecords(historyData);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg-surface)] text-[var(--text-primary)] transition-colors">
      <Navigation onThemeToggle={toggleTheme} isDark={isDark} />

      <main>
        {loading ? (
          <div className="mx-auto max-w-6xl px-4 py-20 text-center font-mono text-xs text-[var(--text-secondary)]">
            Loading analysis history...
          </div>
        ) : (
          <HistoryTable records={records} />
        )}
      </main>
    </div>
  );
}
