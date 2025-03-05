# Advanced Audio Fingerprinting System

## Overview
A robust, production-ready audio fingerprinting system inspired by the Shazam algorithm, capable of identifying music tracks with high accuracy and performance.

## Features
- Parallel audio fingerprinting
- Noise-resistant spectrogram analysis
- SQLite-based fingerprint database
- Command-line interface
- Performance monitoring
- Configurable through environment variables and YAML

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/audio-fingerprinting.git
cd audio-fingerprinting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Fingerprinting Audio Files
```bash
# Fingerprint all audio files in a directory
python -m audio_fingerprint fingerprint /path/to/music/directory

# Recursive directory search
python -m audio_fingerprint fingerprint /path/to/music/directory --recursive
```

### Matching Audio Files
```bash
# Match a single audio file
python -m audio_fingerprint match /path/to/sample.mp3
```

### Performance Statistics
```bash
# View system performance metrics
python -m audio_fingerprint stats
```

## Configuration

### Environment Variables
- `DB_PATH`: Database file path
- `SAMPLE_RATE`: Audio sampling rate
- `LOG_LEVEL`: Logging verbosity
- `MATCH_THRESHOLD`: Matching confidence threshold

### YAML Configuration
Create `config.yaml` in project root:
```yaml
database:
  path: 'audio_fingerprints.db'
  max_connections: 10

fingerprinting:
  sample_rate: 16000
  n_fft: 2048
  hop_length: 512
  max_peaks: 100

matching:
  threshold: 5.0
  max_results: 10