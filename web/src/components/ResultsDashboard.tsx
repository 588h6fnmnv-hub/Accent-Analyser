'use client';

import React from 'react';
import { AnalysisResult } from '../types/voicelens';
import { RotateCcw, Sparkles, Globe, Award, Mic } from 'lucide-react';

interface ResultsDashboardProps {
  result: AnalysisResult;
  onNewAnalysis: () => void;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({
  result,
  onNewAnalysis,
}) => {
  const {
    id,
    createdAt,
    transcript,
    accent,
    pronunciation,
    metrics,
    fillerWordsList,
    difficultWordsList,
    overallFeedback,
  } = result;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-8">
      {/* Top Header Bar */}
      <div className="flex flex-col gap-4 border-b border-[var(--border-subtle)] pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs uppercase tracking-widest text-[var(--text-muted)]">
              Analysis ID: {id}
            </span>
            <span className="font-mono text-xs text-[var(--text-muted)]">
              • {new Date(createdAt).toLocaleString()}
            </span>
          </div>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Speech Analysis Dashboard
          </h1>
        </div>

        <button
          onClick={onNewAnalysis}
          className="inline-flex items-center gap-2 rounded border border-[var(--border-strong)] bg-[var(--bg-panel)] px-4 py-2 font-mono text-xs uppercase tracking-wider text-[var(--text-primary)] hover:bg-[var(--bg-card)] transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>New Recording</span>
        </button>
      </div>

      {/* Top Row: Overall Score & Primary Profiles */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Overall Score Card */}
        <div className="flex flex-col justify-between rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6">
          <div>
            <div className="flex items-center justify-between font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
              <span>Overall Score</span>
              <Award className="h-4 w-4 text-[var(--text-primary)]" />
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="font-mono text-6xl font-bold tracking-tight text-[var(--text-primary)]">
                {pronunciation.overallScore.toFixed(1)}
              </span>
              <span className="font-mono text-xl text-[var(--text-muted)]">/ 100</span>
            </div>
          </div>

          <div className="mt-6">
            <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--border-subtle)]">
              <div
                className="h-full bg-[var(--text-primary)] transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, pronunciation.overallScore))}%` }}
              />
            </div>
            <p className="mt-2 font-mono text-xs text-[var(--text-secondary)]">
              Confidence: {(pronunciation.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Accent Profile Card */}
        <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-4">
          <div className="flex items-center justify-between font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
            <span>Estimated Accent</span>
            <Globe className="h-4 w-4 text-[var(--text-primary)]" />
          </div>

          <div>
            <span className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">
              {accent.predictedAccent}
            </span>
            <span className="ml-2 font-mono text-xs text-[var(--text-secondary)]">
              ({(accent.confidence * 100).toFixed(1)}%)
            </span>
          </div>

          <div className="space-y-2 border-t border-[var(--border-subtle)] pt-3 font-mono text-xs text-[var(--text-secondary)]">
            {accent.top3Accents.map((item, idx) => (
              <div key={idx} className="flex justify-between">
                <span>{item.accent}</span>
                <span className="text-[var(--text-primary)]">{(item.confidence * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Pronunciation & Similarity Card */}
        <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-4">
          <div className="flex items-center justify-between font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
            <span>Phonetic Similarity</span>
            <Mic className="h-4 w-4 text-[var(--text-primary)]" />
          </div>

          <div>
            <span className="font-mono text-4xl font-bold tracking-tight text-[var(--text-primary)]">
              {(pronunciation.pronunciationSimilarity * 100).toFixed(1)}%
            </span>
          </div>

          <p className="font-mono text-xs text-[var(--text-secondary)] border-t border-[var(--border-subtle)] pt-3">
            ECAPA-TDNN acoustic vector projection factor. Evaluated using {pronunciation.backend} engine.
          </p>
        </div>
      </div>

      {/* Speech Delivery Metrics Grid */}
      <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-4">
        <h3 className="font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
          Speech Delivery Metrics
        </h3>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 font-mono">
          <div className="rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
            <span className="text-xs text-[var(--text-muted)]">Pace (WPM)</span>
            <span className="block text-2xl font-bold text-[var(--text-primary)] mt-1">
              {metrics.wordsPerMinute.toFixed(1)}
            </span>
            <span className="text-[10px] text-[var(--text-secondary)]">Words / Min</span>
          </div>

          <div className="rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
            <span className="text-xs text-[var(--text-muted)]">Duration</span>
            <span className="block text-2xl font-bold text-[var(--text-primary)] mt-1">
              {metrics.durationSeconds.toFixed(2)}s
            </span>
            <span className="text-[10px] text-[var(--text-secondary)]">Total Recorded</span>
          </div>

          <div className="rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
            <span className="text-xs text-[var(--text-muted)]">Pauses</span>
            <span className="block text-2xl font-bold text-[var(--text-primary)] mt-1">
              {metrics.pauseCount}
            </span>
            <span className="text-[10px] text-[var(--text-secondary)]">
              Max {metrics.longestPause.toFixed(2)}s
            </span>
          </div>

          <div className="rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
            <span className="text-xs text-[var(--text-muted)]">Total Words</span>
            <span className="block text-2xl font-bold text-[var(--text-primary)] mt-1">
              {metrics.wordCount}
            </span>
            <span className="text-[10px] text-[var(--text-secondary)]">
              Avg {metrics.averageWordsPerSentence.toFixed(1)}/sent
            </span>
          </div>
        </div>
      </div>

      {/* Middle Grid: Filler Words & Difficult Words */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Filler Words Panel */}
        <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
              Detected Filler Words
            </h3>
            <span className="font-mono text-xs font-semibold text-[var(--text-primary)]">
              {metrics.fillerWordCount} Total
            </span>
          </div>

          {fillerWordsList.length > 0 ? (
            <div className="space-y-2">
              {fillerWordsList.map((fw, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] px-4 py-2 font-mono text-xs"
                >
                  <span className="font-semibold text-red-400">{fw.word}</span>
                  <span className="text-[var(--text-secondary)]">{fw.count} occurrence(s)</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 text-center font-mono text-xs text-[var(--text-secondary)]">
              ✓ No filler words detected.
            </div>
          )}
        </div>

        {/* Difficult / Mispronounced Words Panel */}
        <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-4">
          <h3 className="font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
            Difficult / Mispronounced Words
          </h3>

          {difficultWordsList.length > 0 ? (
            <div className="space-y-2">
              {difficultWordsList.map((dw, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] px-4 py-2 font-mono text-xs"
                >
                  <div>
                    <span className="font-semibold text-[var(--text-primary)]">{dw.word}</span>
                    <span className="ml-3 text-[var(--text-muted)]">
                      {dw.startTime.toFixed(2)}s - {dw.endTime.toFixed(2)}s
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="block text-amber-400 font-semibold">{dw.score.toFixed(1)} / 100</span>
                    <span className="text-[10px] text-[var(--text-muted)]">
                      {(dw.confidence * 100).toFixed(0)}% conf
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-4 text-center font-mono text-xs text-[var(--text-secondary)]">
              ✓ No major pronunciation difficulties detected.
            </div>
          )}
        </div>
      </div>

      {/* Transcript Section */}
      <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
            Whisper Audio Transcript
          </h3>
          <span className="font-mono text-xs text-[var(--text-secondary)]">
            Language: {transcript.language}
          </span>
        </div>
        <p className="rounded border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4 text-sm leading-relaxed text-[var(--text-primary)]">
          &ldquo;{transcript.text}&rdquo;
        </p>
      </div>

      {/* Overall Feedback Panel */}
      <div className="rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)] p-6 space-y-3">
        <div className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-[var(--text-muted)]">
          <Sparkles className="h-4 w-4 text-[var(--text-primary)]" />
          <span>VoiceLens Comprehensive Assessment Feedback</span>
        </div>
        <div className="space-y-2 text-sm text-[var(--text-secondary)] pt-2 border-t border-[var(--border-subtle)]">
          {overallFeedback.map((fb, idx) => (
            <p key={idx}>{fb}</p>
          ))}
        </div>
      </div>
    </div>
  );
};
