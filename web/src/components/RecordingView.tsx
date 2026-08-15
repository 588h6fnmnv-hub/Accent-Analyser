'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Square } from 'lucide-react';

interface RecordingViewProps {
  onStopRecording: (blob: Blob) => void;
}

export const RecordingView: React.FC<RecordingViewProps> = ({ onStopRecording }) => {
  const [seconds, setSeconds] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    let timer: NodeJS.Timeout;

    async function startMediaRecorder() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Setup MediaRecorder
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          stream.getTracks().forEach((track) => track.stop());
          onStopRecording(audioBlob);
        };

        mediaRecorder.start();

        // Timer
        timer = setInterval(() => {
          setSeconds((prev) => prev + 1);
        }, 1000);

        // Audio Level Analyser
        const audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 64;
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const updateVolume = () => {
          analyser.getByteFrequencyData(dataArray);
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
          }
          const average = sum / dataArray.length;
          setAudioLevel(Math.min(100, Math.round((average / 128) * 100)));
          animationFrameRef.current = requestAnimationFrame(updateVolume);
        };

        updateVolume();
      } catch (err) {
        console.error('Error accessing microphone:', err);
      }
    }

    startMediaRecorder();

    return () => {
      if (timer) clearInterval(timer);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
    };
  }, [onStopRecording]);

  const handleStopClick = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      {/* Live Indicator Badge */}
      <div className="mb-8 flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 font-mono text-xs uppercase tracking-widest text-red-500">
        <span className="h-2 w-2 rounded-full bg-red-500 animate-ping" />
        <span>Live Recording</span>
      </div>

      {/* Timer */}
      <div className="mb-6 font-mono text-6xl font-bold tracking-tight text-[var(--text-primary)]">
        {formatTime(seconds)}
      </div>

      {/* Audio Wave / Level Meter Bars */}
      <div className="mb-10 flex items-center justify-center gap-1.5 h-16 w-full max-w-xs px-4">
        {Array.from({ length: 24 }).map((_, i) => {
          const heightPercent = Math.max(
            15,
            Math.min(100, audioLevel * (0.5 + Math.sin(i * 0.5) * 0.5))
          );
          return (
            <div
              key={i}
              className="w-1.5 rounded-full bg-[var(--text-primary)] transition-all duration-75"
              style={{ height: `${heightPercent}%` }}
            />
          );
        })}
      </div>

      {/* Controls */}
      <div className="flex flex-col items-center gap-4">
        <button
          onClick={handleStopClick}
          className="group flex h-20 w-20 items-center justify-center rounded-full border-2 border-[var(--text-primary)] bg-[var(--text-primary)] text-[var(--bg-surface)] hover:bg-[var(--bg-surface)] hover:text-[var(--text-primary)] transition-all"
          title="Stop Recording"
        >
          <Square className="h-8 w-8 fill-current" />
        </button>
        <span className="font-mono text-xs text-[var(--text-secondary)] uppercase tracking-wider">
          Click button or press Enter to Stop
        </span>
      </div>
    </div>
  );
};
