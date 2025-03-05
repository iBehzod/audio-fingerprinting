# Import key classes and functions to make them easily accessible
from .core import RobustAudioFingerprinter, parallel_fingerprint
from .database import AudioFingerprintDatabase
from .config import ConfigManager

__all__ = [
    'RobustAudioFingerprinter',
    'parallel_fingerprint',
    'AudioFingerprintDatabase',
    'ConfigManager'
]