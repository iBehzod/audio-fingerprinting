import sqlite3
import numpy as np
from typing import List, Dict, Tuple
import logging
from dataclasses import asdict

# Assuming previous AudioFingerprint and RobustAudioFingerprinter are imported

class AudioFingerprintDatabase:
    """
    Robust database for storing and matching audio fingerprints
    """
    def __init__(self, db_path: str = 'audio_fingerprints.db'):
        """
        Initialize SQLite database for fingerprints
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Fingerprint table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fingerprints (
                    hash_value INTEGER,
                    track_id TEXT,
                    time_offset INTEGER,
                    freq1 INTEGER,
                    freq2 INTEGER,
                    PRIMARY KEY (hash_value, track_id, time_offset)
                )
            ''')
            
            # Metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    filename TEXT,
                    artist TEXT,
                    album TEXT,
                    duration REAL
                )
            ''')
            
            conn.commit()
    
    def insert_fingerprints(
        self, 
        fingerprints_dict: Dict[str, List[AudioFingerprint]]
    ):
        """
        Insert fingerprints for multiple tracks
        
        Args:
            fingerprints_dict: Dictionary of track fingerprints
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for track_id, fingerprints in fingerprints_dict.items():
                for fp in fingerprints:
                    cursor.execute('''
                        INSERT OR IGNORE INTO fingerprints 
                        (hash_value, track_id, time_offset, freq1, freq2) 
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        fp.hash_value, 
                        track_id, 
                        fp.time_offset, 
                        fp.frequency_pair[0], 
                        fp.frequency_pair[1]
                    ))
            
            conn.commit()
    
    def insert_track_metadata(
        self, 
        track_id: str, 
        filename: str, 
        artist: str = None, 
        album: str = None, 
        duration: float = None
    ):
        """
        Insert track metadata
        
        Args:
            track_id: Unique track identifier
            filename: Original filename
            artist: Track artist
            album: Album name
            duration: Audio duration
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO tracks 
                (track_id, filename, artist, album, duration) 
                VALUES (?, ?, ?, ?, ?)
            ''', (track_id, filename, artist, album, duration))
            
            conn.commit()
    
    def match_fingerprint(
        self, 
        sample_fingerprints: List[AudioFingerprint], 
        threshold: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Match sample fingerprints against database
        
        Args:
            sample_fingerprints: Fingerprints to match
            threshold: Minimum number of matching hashes
        
        Returns:
            List of (track_id, confidence) sorted by confidence
        """
        # Group matches by track
        track_matches = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for fp in sample_fingerprints:
                cursor.execute('''
                    SELECT track_id, time_offset 
                    FROM fingerprints 
                    WHERE hash_value = ?
                ''', (fp.hash_value,))
                
                for track_id, db_time_offset in cursor.fetchall():
                    # Calculate time difference
                    time_diff = abs(fp.time_offset - db_time_offset)
                    
                    if track_id not in track_matches:
                        track_matches[track_id] = []
                    
                    track_matches[track_id].append(time_diff)
        
        # Calculate match confidence
        match_results = []
        for track_id, time_diffs in track_matches.items():
            # Count consistent matches
            unique_matches = len(set(time_diffs))
            total_matches = len(time_diffs)
            
            # Calculate confidence
            confidence = total_matches / max(1, unique_matches)
            
            if total_matches >= threshold:
                match_results.append((track_id, confidence))
        
        # Sort by confidence
        return sorted(match_results, key=lambda x: x[1], reverse=True)
    
    def get_track_metadata(self, track_id: str) -> Dict:
        """
        Retrieve track metadata
        
        Args:
            track_id: Track identifier
        
        Returns:
            Dictionary of track metadata
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM tracks WHERE track_id = ?
            ''', (track_id,))
            
            columns = [
                'track_id', 'filename', 'artist', 
                'album', 'duration'
            ]
            
            result = cursor.fetchone()
            return dict(zip(columns, result)) if result else {}

def main():
    # Example workflow
    fingerprinter = RobustAudioFingerprinter()
    database = AudioFingerprintDatabase()
    
    # Parallel fingerprinting
    audio_files = ['track1.mp3', 'track2.wav']
    fingerprints = parallel_fingerprint(audio_files)
    
    # Insert fingerprints
    database.insert_fingerprints(fingerprints)
    
    # Add metadata
    for track_id in fingerprints.keys():
        database.insert_track_metadata(
            track_id=track_id,
            filename=f"{track_id}.mp3",
            artist=f"Artist {track_id}",
            album=f"Album {track_id}"
        )
    
    # Match sample
    sample_audio, _ = librosa.load('sample.mp3', sr=16000)
    sample_fingerprints = fingerprinter.fingerprint_audio(sample_audio)
    
    matches = database.match_fingerprint(sample_fingerprints)
    
    for track_id, confidence in matches:
        metadata = database.get_track_metadata(track_id)
        print(f"Match: {metadata['artist']} - Confidence: {confidence}")

if __name__ == "__main__":
    main()