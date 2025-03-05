import pytest
import os
import numpy as np
import librosa
from src.database import AudioFingerprintDatabase
from src.core import RobustAudioFingerprinter

class TestAudioFingerprintDatabase:
    @pytest.fixture
    def database(self, tmp_path):
        # Create a temporary database for testing
        db_path = tmp_path / "test_fingerprints.db"
        return AudioFingerprintDatabase(str(db_path))

    @pytest.fixture
    def fingerprinter(self):
        return RobustAudioFingerprinter()

    def test_database_creation(self, database):
        # Check if tables are created
        assert os.path.exists(database.db_path)

    def test_insert_fingerprints(self, database, fingerprinter, tmp_path):
        # Create a dummy audio file
        test_file = tmp_path / "test_track.wav"
        audio = np.random.randn(44100)
        librosa.output.write_wav(str(test_file), audio, 16000)

        # Generate fingerprints
        track_id = "test_track"
        audio_data, _ = librosa.load(str(test_file), sr=16000)
        fingerprints = {track_id: fingerprinter.fingerprint_audio(audio_data, track_id)}

        # Insert fingerprints
        database.insert_fingerprints(fingerprints)

        # Verify insertion
        with database._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM fingerprints WHERE track_id = ?", (track_id,))
            count = cursor.fetchone()[0]
            assert count > 0

    def test_insert_track_metadata(self, database):
        track_id = "test_track"
        filename = "test.mp3"
        artist = "Test Artist"
        album = "Test Album"
        duration = 180.5

        database.insert_track_metadata(
            track_id, filename, artist, album, duration
        )

        # Verify metadata insertion
        metadata = database.get_track_metadata(track_id)
        assert metadata['track_id'] == track_id
        assert metadata['filename'] == filename
        assert metadata['artist'] == artist
        assert metadata['album'] == album
        assert metadata['duration'] == duration

    def test_match_fingerprint(self, database, fingerprinter, tmp_path):
        # Create test tracks
        test_files = [
            tmp_path / "track1.wav",
            tmp_path / "track2.wav"
        ]
        
        for test_file in test_files:
            audio = np.random.randn(44100)
            librosa.output.write_wav(str(test_file), audio, 16000)

        # Generate and insert fingerprints
        for i, file in enumerate(test_files, 1):
            track_id = f"track{i}"
            audio_data, _ = librosa.load(str(file), sr=16000)
            fingerprints = {track_id: fingerprinter.fingerprint_audio(audio_data, track_id)}
            database.insert_fingerprints(fingerprints)
            database.insert_track_metadata(track_id, os.path.basename(file))

        # Create a sample to match
        sample_audio, _ = librosa.load(str(test_files[0]), sr=16000)
        sample_fingerprints = fingerprinter.fingerprint_audio(sample_audio)

        # Perform matching
        matches = database.match_fingerprint(sample_fingerprints)

        # Verify matches
        assert len(matches) > 0
        assert all(len(match) == 2 for match in matches)  # track_id, confidence