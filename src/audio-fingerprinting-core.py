import numpy as np
import librosa
import hashlib
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import multiprocessing
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AudioFingerprint:
    """
    Structured representation of an audio fingerprint
    """
    hash_value: int
    track_id: str
    time_offset: int
    frequency_pair: Tuple[int, int]

class RobustAudioFingerprinter:
    """
    Advanced audio fingerprinting system with improved robustness
    """
    def __init__(
        self, 
        sample_rate: int = 16000, 
        n_fft: int = 2048, 
        hop_length: int = 512,
        max_peaks: int = 100
    ):
        """
        Initialize the fingerprinter with configurable parameters
        
        Args:
            sample_rate: Target sampling rate
            n_fft: FFT window size
            hop_length: Samples between successive frames
            max_peaks: Maximum number of peaks to consider
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.max_peaks = max_peaks
        
    def preprocess_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Preprocess audio for robust fingerprinting
        
        Args:
            audio: Raw audio time series
        
        Returns:
            Preprocessed audio
        """
        # Resample if needed
        if len(audio) == 0:
            raise ValueError("Empty audio input")
        
        # Normalize audio
        audio = librosa.util.normalize(audio)
        
        # Trim silence
        audio, _ = librosa.effects.trim(audio)
        
        return audio
    
    def generate_spectrogram(self, audio: np.ndarray) -> np.ndarray:
        """
        Generate robust spectrogram with multiple representations
        
        Args:
            audio: Preprocessed audio
        
        Returns:
            Magnitude spectrogram
        """
        # Compute multiple spectrogram representations
        stft = np.abs(librosa.stft(
            audio, 
            n_fft=self.n_fft, 
            hop_length=self.hop_length
        ))
        
        # Apply log scaling for better peak detection
        log_spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
        
        return log_spectrogram
    
    def find_peaks(self, spectrogram: np.ndarray) -> List[Tuple[int, int, float]]:
        """
        Find robust peaks in spectrogram
        
        Args:
            spectrogram: Log-scaled spectrogram
        
        Returns:
            List of (time_index, frequency_index, magnitude) peaks
        """
        peaks = []
        
        # Detect local peaks across time-frequency plane
        for t in range(spectrogram.shape[1]):
            frame = spectrogram[:, t]
            
            # Find local maxima
            local_peaks = []
            for f in range(len(frame)):
                # Check neighborhood
                is_peak = True
                neighborhood = frame[max(0, f-5):min(len(frame), f+6)]
                
                if len(neighborhood) > 0 and frame[f] != max(neighborhood):
                    is_peak = False
                
                if is_peak and frame[f] > -40:  # Threshold to ignore very low energy
                    local_peaks.append((f, frame[f]))
            
            # Sort and take top peaks
            local_peaks.sort(key=lambda x: x[1], reverse=True)
            for freq, mag in local_peaks[:self.max_peaks]:
                peaks.append((t, freq, mag))
        
        return peaks
    
    def generate_hashes(
        self, 
        peaks: List[Tuple[int, int, float]], 
        fan_out: int = 5
    ) -> List[AudioFingerprint]:
        """
        Generate combinatorial hashes with improved entropy
        
        Args:
            peaks: List of peaks
            fan_out: Number of target points to pair with anchor
        
        Returns:
            List of audio fingerprints
        """
        fingerprints = []
        
        for i, anchor in enumerate(peaks):
            for j in range(i + 1, min(i + fan_out + 1, len(peaks))):
                target = peaks[j]
                
                # Calculate features
                freq1, freq2 = anchor[1], target[1]
                time_diff = target[0] - anchor[0]
                
                # Generate hash
                hash_input = f"{freq1}|{freq2}|{time_diff}"
                hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16) % (2**32)
                
                fingerprint = AudioFingerprint(
                    hash_value=hash_value,
                    track_id=None,  # To be set during database creation
                    time_offset=anchor[0],
                    frequency_pair=(freq1, freq2)
                )
                
                fingerprints.append(fingerprint)
        
        return fingerprints
    
    def fingerprint_audio(
        self, 
        audio: np.ndarray, 
        track_id: Optional[str] = None
    ) -> List[AudioFingerprint]:
        """
        Generate complete audio fingerprint
        
        Args:
            audio: Audio time series
            track_id: Optional track identifier
        
        Returns:
            List of audio fingerprints
        """
        try:
            # Preprocess
            processed_audio = self.preprocess_audio(audio)
            
            # Generate spectrogram
            spectrogram = self.generate_spectrogram(processed_audio)
            
            # Find peaks
            peaks = self.find_peaks(spectrogram)
            
            # Generate hashes
            fingerprints = self.generate_hashes(peaks)
            
            # Set track ID if provided
            for fp in fingerprints:
                fp.track_id = track_id
            
            return fingerprints
        
        except Exception as e:
            logger.error(f"Fingerprinting failed: {e}")
            return []

def parallel_fingerprint(
    audio_files: List[str], 
    num_processes: Optional[int] = None
) -> Dict[str, List[AudioFingerprint]]:
    """
    Parallel audio fingerprinting
    
    Args:
        audio_files: List of audio file paths
        num_processes: Number of parallel processes
    
    Returns:
        Dictionary of track fingerprints
    """
    if num_processes is None:
        num_processes = max(1, multiprocessing.cpu_count() - 1)
    
    def process_file(file_path):
        try:
            # Extract track ID from filename
            track_id = os.path.splitext(os.path.basename(file_path))[0]
            
            # Load audio
            audio, _ = librosa.load(file_path, sr=16000)
            
            # Create fingerprinter
            fingerprinter = RobustAudioFingerprinter()
            
            # Generate fingerprints
            fingerprints = fingerprinter.fingerprint_audio(audio, track_id)
            
            return track_id, fingerprints
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            return None
    
    # Use multiprocessing
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(process_file, audio_files)
    
    # Filter out None results and convert to dictionary
    fingerprint_dict = {
        track_id: fingerprints 
        for result in results 
        if result is not None 
        for track_id, fingerprints in [result]
    }
    
    return fingerprint_dict

def main():
    # Example usage
    test_files = [
        'track1.mp3',
        'track2.wav',
        # Add more audio files
    ]
    
    fingerprints = parallel_fingerprint(test_files)
    print(f"Processed {len(fingerprints)} tracks")

if __name__ == "__main__":
    main()
