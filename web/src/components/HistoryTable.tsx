'use client';

import React, { useState } from 'react';
import { HistoryRecord } from '../types/voicelens';
import { Search, ChevronRight } from 'lucide-react';

interface HistoryTableProps {
  records: HistoryRecord[];
  onSelectRecord?: (record: HistoryRecord) => void;
}

export const HistoryTable: React.FC<HistoryTableProps> = ({
  records,
  onSelectRecord,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRecords = records.filter(
    (r) =>
      r.transcriptSnippet.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.predictedAccent.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-6">
      {/* Search Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border-subtle)] pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Analysis History
          </h1>
          <p className="mt-1 text-sm text-[var(--text-secondary)] font-mono">
            {records.length} stored voice analysis sessions
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search transcripts or accents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded border border-[var(--border-strong)] bg-[var(--bg-panel)] py-2 pl-9 pr-4 font-mono text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--text-primary)] transition-colors"
          />
        </div>
      </div>

      {/* History Table */}
      <div className="overflow-x-auto rounded-lg border border-[var(--border-strong)] bg-[var(--bg-panel)]">
        <table className="w-full text-left font-mono text-xs">
          <thead className="border-b border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-muted)] uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3">Session ID & Date</th>
              <th className="px-6 py-3">Score</th>
              <th className="px-6 py-3">Pace (WPM)</th>
              <th className="px-6 py-3">Accent</th>
              <th className="px-6 py-3">Transcript Snippet</th>
              <th className="px-6 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-subtle)]">
            {filteredRecords.length > 0 ? (
              filteredRecords.map((record) => (
                <tr
                  key={record.id}
                  onClick={() => onSelectRecord?.(record)}
                  className="cursor-pointer hover:bg-[var(--bg-card)] transition-colors"
                >
                  <td className="px-6 py-4">
                    <span className="block font-semibold text-[var(--text-primary)]">
                      {record.id}
                    </span>
                    <span className="text-[10px] text-[var(--text-muted)]">
                      {record.timestamp} ({record.durationSeconds.toFixed(1)}s)
                    </span>
                  </td>

                  <td className="px-6 py-4">
                    <span className="font-bold text-[var(--text-primary)]">
                      {record.overallScore.toFixed(1)}
                    </span>
                    <span className="text-[var(--text-muted)]"> / 100</span>
                  </td>

                  <td className="px-6 py-4 text-[var(--text-secondary)]">
                    {record.wordsPerMinute.toFixed(1)} WPM
                  </td>

                  <td className="px-6 py-4 text-[var(--text-secondary)]">
                    {record.predictedAccent}
                  </td>

                  <td className="px-6 py-4 text-[var(--text-secondary)] max-w-xs truncate">
                    &ldquo;{record.transcriptSnippet}&rdquo;
                  </td>

                  <td className="px-6 py-4 text-right">
                    <ChevronRight className="inline-block h-4 w-4 text-[var(--text-muted)]" />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={6}
                  className="px-6 py-12 text-center text-[var(--text-muted)]"
                >
                  No history records match your query.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
