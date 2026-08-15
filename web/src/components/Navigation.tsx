'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sun, Moon, Activity, Mic } from 'lucide-react';

interface NavigationProps {
  onThemeToggle?: () => void;
  isDark?: boolean;
}

export const Navigation: React.FC<NavigationProps> = ({
  onThemeToggle,
  isDark = true,
}) => {
  const pathname = usePathname();

  return (
    <header className="w-full border-b border-[var(--border-subtle)] bg-[var(--bg-surface)] px-6 py-4 transition-colors">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-[var(--text-primary)] text-[var(--bg-surface)] font-bold">
            <Mic className="h-4 w-4" />
          </div>
          <div>
            <span className="font-semibold text-lg tracking-tight text-[var(--text-primary)]">
              VoiceLens
            </span>
            <span className="ml-2 font-mono text-xs uppercase tracking-widest text-[var(--text-muted)]">
              v0.1.0
            </span>
          </div>
        </div>

        {/* Links */}
        <nav className="flex items-center gap-8 font-mono text-xs tracking-wider uppercase">
          <Link
            href="/"
            className={`pb-1 transition-colors ${
              pathname === '/'
                ? 'border-b-2 border-[var(--text-primary)] text-[var(--text-primary)] font-semibold'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            Analyze
          </Link>
          <Link
            href="/history"
            className={`pb-1 transition-colors ${
              pathname === '/history'
                ? 'border-b-2 border-[var(--text-primary)] text-[var(--text-primary)] font-semibold'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            History
          </Link>
        </nav>

        {/* Right Action */}
        <div className="flex items-center gap-4">
          <div className="hidden items-center gap-2 font-mono text-xs text-[var(--text-secondary)] sm:flex">
            <Activity className="h-3.5 w-3.5 text-emerald-500 animate-pulse" />
            <span>Engine Ready</span>
          </div>

          <button
            onClick={onThemeToggle}
            className="flex h-8 w-8 items-center justify-center rounded border border-[var(--border-strong)] bg-[var(--bg-panel)] text-[var(--text-primary)] hover:bg-[var(--bg-card)] transition-colors"
            title="Toggle theme"
            aria-label="Toggle theme"
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </header>
  );
};
