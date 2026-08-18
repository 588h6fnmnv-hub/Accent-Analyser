/**
 * VoiceLens API Client Layer
 * Encapsulates communication with the Python VoiceLens analysis engine.
 * Posts real audio recordings to the VoiceLens FastAPI backend.
 */

import { AnalysisResult, HistoryRecord } from '../types/voicelens';

export class VoiceLensApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api') {
    this.baseUrl = baseUrl;
  }

  /**
   * Submits an audio recording Blob to the VoiceLens Python backend engine.
   * Sends multipart/form-data audio file to /api/analyze.
   */
  async analyzeAudio(audioBlob: Blob): Promise<AnalysisResult> {
    const formData = new FormData();
    const fileExtension = audioBlob.type.includes('webm') ? 'webm' : 'wav';
    formData.append('file', audioBlob, `recording.${fileExtension}`);

    let response: Response;
    try {
      response = await fetch(`${this.baseUrl}/analyze`, {
        method: 'POST',
        body: formData,
      });
    } catch {
      throw new Error(
        `Unable to connect to VoiceLens API at ${this.baseUrl}. Please ensure 'voicelens serve' is running.`
      );
    }

    if (!response.ok) {
      let errorDetail = 'VoiceLens engine error';
      try {
        const errJson = await response.json();
        if (errJson.detail) {
          errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch {
        // Fallback to text status
        errorDetail = `Server returned HTTP ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorDetail);
    }

    const data: AnalysisResult = await response.json();
    return data;
  }

  /**
   * Fetches stored analysis history records.
   */
  async getHistory(): Promise<HistoryRecord[]> {
    try {
      const response = await fetch(`${this.baseUrl}/history`);
      if (response.ok) {
        return await response.json();
      }
    } catch {
      // Return empty history if store is unavailable
    }
    return [];
  }
}

export const apiClient = new VoiceLensApiClient();
