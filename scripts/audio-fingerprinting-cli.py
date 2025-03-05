# import os
# import time
# import click
# import logging
# from typing import List, Optional

# # Import previous components
# from audio_fingerprinting_core import (
#     RobustAudioFingerprinter, 
#     parallel_fingerprint
# )
# from audio_fingerprinting_database import (
#     AudioFingerprintDatabase, 
#     AudioFingerprint
# )
# from audio_fingerprinting_config import (
#     ConfigManager, 
#     PerformanceMonitor
# )

# class AudioFingerprintService:
#     """
#     Comprehensive service for audio fingerprinting operations
#     """
#     def __init__(self):
#         """
#         Initialize service components
#         """
#         self.config = ConfigManager()
#         self.monitor = PerformanceMonitor()
#         self.fingerprinter = RobustAudioFingerprinter(
#             sample_rate=self.config.get('fingerprinting.sample_rate'),
#             n_fft=self.config.get('fingerprinting.n_fft'),
#             hop_length=self.config.get('fingerprinting.hop_length'),
#             max_peaks=self.config.get('fingerprinting.max_peaks')
#         )
#         self.database = AudioFingerprintDatabase(
#             self.config.get('database.path')
#         )
    
#     def process_directory(
#         self, 
#         directory: str, 
#         recursive: bool = False
#     ) -> dict:
#         """
#         Process all audio files in a directory
        
#         Args:
#             directory: Path to directory
#             recursive: Whether to search subdirectories
        
#         Returns:
#             Dictionary of processed tracks
#         """
#         audio_extensions = {'.mp3', '.wav', '.flac', '.ogg'}
#         audio_files = []
        
#         for root, _, files in os.walk(directory):
#             for file in files:
#                 if os.path.splitext(file)[1].lower() in audio_extensions:
#                     audio_files.append(os.path.join(root, file))
                
#                 if not recursive:
#                     break
        
#         logging.info(f"Found {len(audio_files)} audio files")
        
#         # Parallel fingerprinting
#         start_time = time.time()
#         fingerprints = parallel_fingerprint(audio_files)
#         processing_time = time.time() - start_time
        
#         # Record performance
#         self.monitor.record_fingerprinting_time(processing_time)
        
#         # Insert into database
#         self.database.insert_fingerprints(fingerprints)
        
#         # Add metadata
#         for track_id, fps in fingerprints.items():
#             file_path = next(f for f in audio_files if track_id in f)
#             self.database.insert_track_metadata(
#                 track_id=track_id,
#                 filename=os.path.basename(file_path)
#             )
        
#         return fingerprints
    
#     def match_audio(
#         self, 
#         audio_file: str, 
#         threshold: Optional[float] = None
#     ) -> List[tuple]:
#         """
#         Match an audio file against the database
        
#         Args:
#             audio_file: Path to audio file to match
#             threshold: Optional matching threshold
        
#         Returns:
#             List of matched tracks with confidence
#         """
#         import librosa
        
#         # Load audio
#         audio, _ = librosa.load(audio_file, sr=16000)
        
#         # Generate fingerprints
#         start_time = time.time()
#         sample_fingerprints = self.fingerprinter.fingerprint_audio(audio)
        
#         # Match against database
#         threshold = threshold or self.config.get('matching.threshold')
#         matches = self.database.match_fingerprint(
#             sample_fingerprints, 
#             threshold=threshold
#         )
        
#         matching_time = time.time() - start_time
#         self.monitor.record_matching_time(matching_time)
        
#         # Enrich matches with metadata
#         enriched_matches = []
#         for track_id, confidence in matches:
#             metadata = self.database.get_track_metadata(track_id)
#             enriched_matches.append((metadata, confidence))
        
#         return enriched_matches

# @click.group()
# def cli():
#     """
#     Audio Fingerprinting CLI
#     """
#     pass

# @cli.command()
# @click.argument('directory', type=click.Path(exists=True))
# @click.option('--recursive', is_flag=True, help='Search subdirectories')
# def fingerprint(directory, recursive):
#     """
#     Fingerprint audio files in a directory
#     """
#     service = AudioFingerprintService()
#     results = service.process_directory(directory, recursive)
#     click.echo(f"Processed {len(results)} tracks")

# @cli.command()
# @click.argument('audio_file', type=click.Path(exists=True))
# @click.option('--threshold', type=float, help='Matching threshold')
# def match(audio_file, threshold):
#     """
#     Match an audio file against the database
#     """
#     service = AudioFingerprintService()
#     matches = service.match_audio(audio_file, threshold)
    
#     if matches:
#         click.echo("Matches found:")
#         for metadata, confidence in matches:
#             click.echo(f"Track: {metadata.get('filename')} - Confidence: {confidence:.2f}")
#     else:
#         click.echo("No matches found")

# @cli.command()
# def stats():
#     """
#     Display system performance statistics
#     """
#     service = AudioFingerprintService()
#     performance = service.monitor.get_performance_summary()
    
#     click.echo("Performance Statistics:")
#     for key, value in performance.items():
#         click.echo(f"{key.replace('_', ' ').title()}: {value}")

# def main():
#     cli()

# if __name__ == "__main__":
#     main()


import click
import logging
from src.core import RobustAudioFingerprinter, parallel_fingerprint
from src.database import AudioFingerprintDatabase
from src.config import ConfigManager

@click.group()
def cli():
    """Audio Fingerprinting CLI"""
    logging.basicConfig(level=logging.INFO)

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', is_flag=True, help='Search subdirectories')
def fingerprint(directory, recursive):
    """Fingerprint audio files in a directory"""
    config = ConfigManager()
    database = AudioFingerprintDatabase(config.get('database.path'))
    fingerprinter = RobustAudioFingerprinter()

    # Process directory
    audio_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.flac', '.ogg')):
                audio_files.append(os.path.join(root, file))
                if not recursive:
                    break

    # Parallel fingerprinting
    fingerprints = parallel_fingerprint(audio_files)
    
    # Insert into database
    database.insert_fingerprints(fingerprints)
    
    click.echo(f"Processed {len(fingerprints)} tracks")

@cli.command()
@click.argument('audio_file', type=click.Path(exists=True))
def match(audio_file):
    """Match an audio file against the database"""
    config = ConfigManager()
    database = AudioFingerprintDatabase(config.get('database.path'))
    fingerprinter = RobustAudioFingerprinter()

    # Load and fingerprint sample
    sample_audio, _ = librosa.load(audio_file, sr=16000)
    sample_fingerprints = fingerprinter.fingerprint_audio(sample_audio)

    # Match against database
    matches = database.match_fingerprint(sample_fingerprints)

    if matches:
        click.echo("Matches found:")
        for track_id, confidence in matches:
            metadata = database.get_track_metadata(track_id)
            click.echo(f"Track: {metadata.get('filename', 'Unknown')} - Confidence: {confidence:.2f}")
    else:
        click.echo("No matches found")

def main():
    cli()

if __name__ == "__main__":
    main()