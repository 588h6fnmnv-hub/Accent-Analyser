/**
 * VoiceLens API Client Layer
 * Encapsulates communication with the Python VoiceLens analysis engine.
 * Components use this abstraction rather than raw fetch calls.
 */

import { AnalysisResult, HistoryRecord } from '../types/voicelens';

export const MOCK_ANALYSIS_RESULT: AnalysisResult = {
  id: 'vl-20250815-8841',
  createdAt: '2025-08-15T10:45:00Z',
  audioDurationSeconds: 14.85,
  transcript: {
    text: "Actually, I think we should proceed with the new speech model architecture, like, as soon as possible because the performance gains are significant.",
    language: 'English (US)',
    wordCount: 24,
  },
  accent: {
    predictedAccent: 'American English',
    confidence: 0.924,
    top3Accents: [
      { accent: 'American English', confidence: 0.924 },
      { accent: 'Canadian English', confidence: 0.052 },
      { accent: 'British English', confidence: 0.018 },
    ],
    notes: [
      'Accent embeddings processed via ECAPA-TDNN.',
      'Disclaimer: This is an Estimated Accent based on heuristic similarity and is not clinically validated.',
    ],
  },
  pronunciation: {
    overallScore: 88.5,
    pronunciationSimilarity: 0.892,
    confidence: 0.941,
    backend: 'speechbrain',
    notes: [
      'Speech embeddings generated with shape [1, 192].',
      'Detected language profile: English',
    ],
  },
  metrics: {
    durationSeconds: 14.85,
    wordCount: 24,
    wordsPerMinute: 142.5,
    pauseCount: 2,
    averagePauseDuration: 0.42,
    longestPause: 0.68,
    fillerWordCount: 2,
    fillerWords: ['actually', 'like'],
    sentenceCount: 1,
    averageWordsPerSentence: 24.0,
  },
  fillerWordsList: [
    { word: 'actually', count: 1 },
    { word: 'like', count: 1 },
  ],
  difficultWordsList: [
    {
      word: 'architecture',
      confidence: 0.742,
      score: 66.18,
      startTime: 6.82,
      endTime: 7.54,
    },
    {
      word: 'significant',
      confidence: 0.810,
      score: 72.25,
      startTime: 12.10,
      endTime: 12.92,
    },
  ],
  overallFeedback: [
    "• Accent Profile: Detected accent is American English.",
    "• Pronunciation: Excellent clarity! Spoken acoustic features align closely with target standards.",
    "• Pace (Speed): Natural pace. Your 142.5 WPM rate is in the ideal conversational zone.",
    "• Filler Words: Low filler count detected (2 fillers). Good speech discipline.",
  ],
};

export const MOCK_HISTORY_RECORDS: HistoryRecord[] = [
  {
    id: 'vl-20250815-8841',
    timestamp: '2025-08-15 10:45:00',
    durationSeconds: 14.85,
    overallScore: 88.5,
    wordsPerMinute: 142.5,
    predictedAccent: 'American English',
    transcriptSnippet: "Actually, I think we should proceed with the new speech model architecture...",
    fillerWordCount: 2,
  },
  {
    id: 'vl-20250814-7210',
    timestamp: '2025-08-14 16:20:12',
    durationSeconds: 22.40,
    overallScore: 79.0,
    wordsPerMinute: 158.0,
    predictedAccent: 'British English',
    transcriptSnippet: "Um, we need to evaluate the alignment results before deploying the new version...",
    fillerWordCount: 5,
  },
  {
    id: 'vl-20250812-3109',
    timestamp: '2025-08-12 09:12:44',
    durationSeconds: 18.10,
    overallScore: 92.0,
    wordsPerMinute: 135.2,
    predictedAccent: 'American English',
    transcriptSnippet: "The VoiceLens analysis pipeline processes speech metrics and forced alignment concurrently...",
    fillerWordCount: 0,
  },
];

export class VoiceLensApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || '/api') {
    this.baseUrl = baseUrl;
  }

  /**
   * Submits an audio recording Blob to the VoiceLens Python backend engine.
   * Currently returns realistic mock data for prototype rendering.
   */
  async analyzeAudio(_audioBlob: Blob): Promise<AnalysisResult> {
    // Simulated network delay matching backend processing speed
    await new Promise((resolve) => setTimeout(resolve, 2500));
    return MOCK_ANALYSIS_RESULT;
  }

  /**
   * Fetches analysis history from VoiceLens store.
   */
  async getHistory(): Promise<HistoryRecord[]> {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return MOCK_HISTORY_RECORDS;
  }
}

export const apiClient = new VoiceLensApiClient();
