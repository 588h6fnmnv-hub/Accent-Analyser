"""Tests for the VoiceLens Forced Alignment module."""

import pytest

from voicelens.alignment import PhonemeAlignment, WhisperAligner, WordAlignment


class MockWord:
    """Mock for faster-whisper word object."""

    def __init__(self, word: str, start: float, end: float, probability: float):
        self.word = word
        self.start = start
        self.end = end
        self.probability = probability


class MockSegment:
    """Mock for faster-whisper segment object."""

    def __init__(self, words: list[MockWord]):
        self.words = words


class MockWhisperModel:
    """Mock for faster-whisper.WhisperModel."""

    def transcribe(self, _audio_path: str, word_timestamps: bool = True):
        # Reference argument to avoid unused variable warning
        assert word_timestamps is True

        words = [
            MockWord("hello", 0.1, 0.5, 0.98),
            MockWord("world", 0.6, 1.1, 0.92),
        ]
        return [MockSegment(words)], None


def test_alignment_structures():
    """Verify PhonemeAlignment and WordAlignment properties."""
    ph = PhonemeAlignment("H", 0.1, 0.2)
    assert ph.phoneme == "H"
    assert ph.start_time == 0.1
    assert ph.end_time == 0.2

    w = WordAlignment("test", 0.1, 0.5, 0.95, [ph])
    assert w.word == "test"
    assert w.start_time == 0.1
    assert w.end_time == 0.5
    assert w.confidence == 0.95
    assert len(w.phonemes) == 1


@pytest.mark.parametrize(
    "word, expected_ph_count",
    [
        ("hello", 5),  # H-E-L-L-O
        ("sh", 1),  # Digraph 'sh' mapped to 'SH'
        ("ck", 1),  # Digraph 'ck' mapped to 'K'
        ("", 0),  # Empty word
        (" th ", 1),  # Whitespace and th digraph
    ],
)
def test_g2p_digraph_rules(word, expected_ph_count):
    """Verify digraph mapping rules and phoneme counts."""
    from voicelens.alignment.aligner import convert_word_to_phonemes

    phonemes = convert_word_to_phonemes(word)
    assert len(phonemes) == expected_ph_count


def test_whisper_aligner_success():
    """Verify alignment process and word timestamp parses successfully."""
    from unittest.mock import MagicMock, patch

    mock_transcriber = MagicMock()
    mock_transcriber._get_model.return_value = MockWhisperModel()

    aligner = WhisperAligner(transcriber=mock_transcriber)

    with patch("pathlib.Path.exists", return_value=True):
        res = aligner.align("fake_path.wav", "hello world")

        assert len(res.words) == 2
        assert res.words[0].word == "hello"
        assert res.words[0].start_time == 0.1
        assert res.words[0].end_time == 0.5
        assert res.words[0].confidence == 0.98
        # check that phonemes are populated
        assert len(res.words[0].phonemes) > 0


def test_whisper_aligner_empty_transcript():
    """Verify alignment handles empty transcripts gracefully."""
    from unittest.mock import MagicMock, patch

    mock_transcriber = MagicMock()
    aligner = WhisperAligner(transcriber=mock_transcriber)

    with patch("pathlib.Path.exists", return_value=True):
        res = aligner.align("fake_path.wav", "   ")
        assert len(res.words) == 0
        assert "Empty transcript" in res.notes[0]
