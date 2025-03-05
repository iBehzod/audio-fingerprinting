import pytest
import numpy as np
import librosa
from src.core import RobustAudioFingerprinter, parallel_fingerprint
import os

class TestRobustAudioFingerprinter:
    @pytest.fixture
    def fingerprinter(self):
        return RobustAudioFingerprinter()

    def test_preprocess_audio(self, fingerprinter):
        # Generate test audio
        test_audio = np.random.randn(44100)  # 1 second of random noise
        
        preprocessed = fingerprinter.preprocess_audio(test_audio)
        
        assert len(preprocessed) > 0
        assert np.max(np.abs(preprocessed)) <= 1.0  # Normalized
        assert len(preprocessed) < len(test_audio)  # Trimmed

    def test_generate_spectrogram(self, fingerprinter):
        test_audio = np.random.randn(44100)
        preprocessed = fingerprinter.preprocess_audio(test_audio)
        
        spectrogram = fingerprinter.generate_spectrogram(preprocessed)
        
        assert spectrogram.ndim == 2
        assert spectrogram.shape[0] > 0
        assert spectrogram.shape[1] > 0

    def test_find_peaks(self, fingerprinter):
        test_audio = np.random.randn(44100)
        preprocessed = fingerprinter.preprocess_audio(test_audio)
        spectrogram = fingerprinter.generate_spectrogram(preprocessed)
        
        peaks = fingerprinter.find_peaks(spectrogram)
        
        assert len(peaks) > 0
        assert all(len(peak) == 3 for peak in peaks)  # time, freq, magnitude

    def test_generate_hashes(self, fingerprinter):
        test_audio = np.random.randn(44100)
        preprocessed = fingerprinter.preprocess_audio(test_audio)
        spectrogram = fingerprinter.generate_spectrogram(preprocessed)
        peaks = fingerprinter.find_peaks(spectrogram)
        
        fingerprints = fingerprinter.generate_hashes(peaks)
        
        assert len(fingerprints) > 0
        assert all(hasattr(fp, 'hash_value') for fp in fingerprints)

    def test_fingerprint_audio(self, fingerprinter):
        test_audio = np.random.randn(44100)
        
        fingerprints = fingerprinter.fingerprint_audio(test_audio, track_id='test_track')
        
        assert len(fingerprints) > 0
        assert all(fp.track_id == 'test_track' for fp in fingerprints)

def test_parallel_fingerprint(tmp_path):
    # Create some dummy audio files
    test_files = [
        tmp_path / "test1.wav",
        tmp_path / "test2.wav"
    ]
    
    for test_file in test_files:
        # Create a dummy audio file
        audio = np.random.randn(44100)
        librosa.output.write_wav(str(test_file), audio, 16000)
    
    # Test parallel fingerprinting
    fingerprints = parallel_fingerprint([str(f) for f in test_files])
    
    assert isinstance(fingerprints, dict)
    assert len(fingerprints) == len(test_files)
    for track_id, fp_list in fingerprints.items():
        assert len(fp_list) > 0