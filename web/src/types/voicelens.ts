/**
 * VoiceLens TypeScript Domain Models
 * Represents API response contracts for VoiceLens voice analysis engine.
 */

export type AnalysisState = 'IDLE' | 'RECORDING' | 'ANALYZING' | 'RESULTS' | 'ERROR';

export interface TranscriptResult {
  text: string;
  language: string;
  wordCount: number;
}

export interface AccentResult {
  predictedAccent: string;
  confidence: number; // 0.0 to 1.0
  top3Accents: Array<{ accent: string; confidence: number }>;
  notes: string[];
}

export interface PronunciationResult {
  overallScore: number; // 0.0 to 100.0
  pronunciationSimilarity: number; // 0.0 to 1.0
  confidence: number; // 0.0 to 1.0
  backend: string;
  notes: string[];
}

export interface SpeechMetrics {
  durationSeconds: number;
  wordCount: number;
  wordsPerMinute: number;
  pauseCount: number;
  averagePauseDuration: number;
  longestPause: number;
  fillerWordCount: number;
  fillerWords: string[];
  sentenceCount: number;
  averageWordsPerSentence: number;
}

export interface FillerWord {
  word: string;
  count: number;
  timestamps?: number[];
}

export interface DifficultWord {
  word: string;
  confidence: number; // 0.0 to 1.0
  score: number; // 0.0 to 100.0
  startTime: number;
  endTime: number;
}

export interface AnalysisResult {
  id: string;
  createdAt: string;
  audioDurationSeconds: number;
  transcript: TranscriptResult;
  accent: AccentResult;
  pronunciation: PronunciationResult;
  metrics: SpeechMetrics;
  fillerWordsList: FillerWord[];
  difficultWordsList: DifficultWord[];
  overallFeedback: string[];
}

export interface HistoryRecord {
  id: string;
  timestamp: string;
  durationSeconds: number;
  overallScore: number;
  wordsPerMinute: number;
  predictedAccent: string;
  transcriptSnippet: string;
  fillerWordCount: number;
}
