'use client';

import React from 'react';
import { Mic, Radio, ShieldCheck, Cpu } from 'lucide-react';

interface AnalyzeViewProps {
  onStartRecording: () => void;
}

export const AnalyzeView: React.FC<AnalyzeViewProps> = ({ onStartRecording }) => {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      {/* Title Header */}
      <div className="mb-12 text-center">
        <div className="mb-3 inline-flex items-center gap-2 rounded border border-[var(--border-strong)] bg-[var(--bg-panel)] px-3 py-1 font-mono text-xs uppercase tracking-widest text-[var(--text-secondary)]">
          <Radio className="h-3.5 w-3.5" />
          <span>Achromatic Precision Audio Engine</span>
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-[var(--text-primary)] sm:text-5xl">
          VoiceLens Intelligence
        </h1>
        <p className="mt-3 text-lg text-[var(--text-secondary)]">
          Record speech to extract metrics, accent profiles, pronunciation scores, and forced alignments.
        </p>
      </div>

      {/* Primary Recording Panel */}
      <div className="relative overflow-hidden rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-8 text-center sm:p-12">
        <div className="mx-auto flex max-w-md flex-col items-center">
          <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full border-2 border-[var(--border-strong)] bg-[var(--bg-card)] text-[var(--text-primary)]">
            <Mic className="h-10 w-10" />
          </div>

          <h2 className="text-2xl font-semibold tracking-tight text-[var(--text-primary)]">
            Ready to Analyze Speech
          </h2>
          <p className="mt-2 text-sm text-[var(--text-secondary)]">
            Ensure your microphone is connected. Speak clearly for 10-30 seconds for optimal scoring accuracy.
          </p>

          <button
            onClick={onStartRecording}
            className="mt-8 flex w-full items-center justify-center gap-3 rounded border border-[var(--text-primary)] bg-[var(--text-primary)] px-6 py-4 font-mono text-sm font-semibold uppercase tracking-wider text-[var(--bg-surface)] hover:bg-transparent hover:text-[var(--text-primary)] transition-all"
          >
            <Mic className="h-4 w-4" />
            <span>Start Microphone Recording</span>
          </button>
        </div>

        {/* Feature Specs Grid */}
        <div className="mt-12 grid grid-cols-1 gap-4 border-t border-[var(--border-subtle)] pt-8 text-left sm:grid-cols-3 font-mono text-xs text-[var(--text-secondary)]">
          <div className="flex items-start gap-2.5">
            <Cpu className="h-4 w-4 text-[var(--text-primary)] shrink-0 mt-0.5" />
            <div>
              <span className="block font-semibold text-[var(--text-primary)]">Whisper STT</span>
              <span>Sub-word timestamp forced alignment</span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <Radio className="h-4 w-4 text-[var(--text-primary)] shrink-0 mt-0.5" />
            <div>
              <span className="block font-semibold text-[var(--text-primary)]">SpeechBrain ECAPA</span>
              <span>Speech embedding accent vector classification</span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <ShieldCheck className="h-4 w-4 text-[var(--text-primary)] shrink-0 mt-0.5" />
            <div>
              <span className="block font-semibold text-[var(--text-primary)]">Delivery Metrics</span>
              <span>WPM, silent pauses & filler word detection</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
