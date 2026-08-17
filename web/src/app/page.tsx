'use client';

import React, { useState } from 'react';
import { Navigation } from '../components/Navigation';
import { AnalyzeView } from '../components/AnalyzeView';
import { RecordingView } from '../components/RecordingView';
import { AnalyzingView } from '../components/AnalyzingView';
import { ResultsDashboard } from '../components/ResultsDashboard';
import { AnalysisState, AnalysisResult } from '../types/voicelens';
import { apiClient } from '../lib/api';
import { AlertTriangle, RotateCcw } from 'lucide-react';

export default function HomePage() {
  const [state, setState] = useState<AnalysisState>('IDLE');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
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

  const handleStartRecording = () => {
    setState('RECORDING');
  };

  const handleRecordingError = (err: string) => {
    setErrorMessage(err);
    setState('ERROR');
  };

  const handleStopRecording = async (audioBlob: Blob) => {
    setState('ANALYZING');
    setErrorMessage(null);
    try {
      const res = await apiClient.analyzeAudio(audioBlob);
      setResult(res);
      setState('RESULTS');
    } catch (err: unknown) {
      console.error('Analysis failed:', err);
      setErrorMessage(
        err instanceof Error ? err.message : 'VoiceLens engine analysis error'
      );
      setState('ERROR');
    }
  };

  const handleReset = () => {
    setState('IDLE');
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-surface)] text-[var(--text-primary)] transition-colors">
      <Navigation onThemeToggle={toggleTheme} isDark={isDark} />

      <main>
        {state === 'IDLE' && <AnalyzeView onStartRecording={handleStartRecording} />}

        {state === 'RECORDING' && (
          <RecordingView
            onStopRecording={handleStopRecording}
            onError={handleRecordingError}
          />
        )}

        {state === 'ANALYZING' && <AnalyzingView />}

        {state === 'RESULTS' && result && (
          <ResultsDashboard result={result} onNewAnalysis={handleReset} />
        )}

        {state === 'ERROR' && (
          <div className="mx-auto max-w-md px-4 py-20 text-center">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full border border-red-500/30 bg-red-500/10 text-red-500">
              <AlertTriangle className="h-8 w-8" />
            </div>
            <h2 className="text-2xl font-bold text-[var(--text-primary)]">
              Analysis Engine Error
            </h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)] font-mono">
              {errorMessage || 'Failed to process audio recording.'}
            </p>
            <button
              onClick={handleReset}
              className="mt-6 inline-flex items-center gap-2 rounded border border-[var(--text-primary)] bg-[var(--text-primary)] px-4 py-2 font-mono text-xs uppercase tracking-wider text-[var(--bg-surface)] hover:bg-transparent hover:text-[var(--text-primary)] transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Try Again</span>
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
