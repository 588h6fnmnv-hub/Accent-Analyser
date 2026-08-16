'use client';

import React from 'react';
import { Loader2, Cpu, FileText, Globe, Volume2 } from 'lucide-react';

export const AnalyzingView: React.FC = () => {
  return (
    <div className="mx-auto max-w-2xl px-4 py-20 text-center">
      {/* Loading Icon Spinner */}
      <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full border border-[var(--border-strong)] bg-[var(--bg-panel)] text-[var(--text-primary)]">
        <Loader2 className="h-10 w-10 animate-spin" />
      </div>

      <h2 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
        Analyzing Speech Audio...
      </h2>
      <p className="mt-2 text-sm text-[var(--text-secondary)] font-mono">
        Executing concurrent VoiceLens intelligence pipelines. Please wait.
      </p>

      {/* Steps Pipeline Visualizer */}
      <div className="mt-10 rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 text-left">
        <div className="space-y-4 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
            <div className="flex items-center gap-3">
              <FileText className="h-4 w-4 text-[var(--text-primary)]" />
              <span>Faster-Whisper Speech Transcription</span>
            </div>
            <span className="text-emerald-500 font-semibold uppercase tracking-wider">Processing</span>
          </div>

          <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
            <div className="flex items-center gap-3">
              <Globe className="h-4 w-4 text-[var(--text-primary)]" />
              <span>SpeechBrain ECAPA Accent Vector Analysis</span>
            </div>
            <span className="text-emerald-500 font-semibold uppercase tracking-wider">Processing</span>
          </div>

          <div className="flex items-center justify-between border-b border-[var(--border-subtle)] pb-3">
            <div className="flex items-center gap-3">
              <Volume2 className="h-4 w-4 text-[var(--text-primary)]" />
              <span>Phonetic Forced Alignment & Mispronunciation</span>
            </div>
            <span className="text-[var(--text-muted)] uppercase tracking-wider">Queued</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Cpu className="h-4 w-4 text-[var(--text-primary)]" />
              <span>Speech Delivery & WPM Metrics Calculation</span>
            </div>
            <span className="text-[var(--text-muted)] uppercase tracking-wider">Queued</span>
          </div>
        </div>
      </div>
    </div>
  );
};
