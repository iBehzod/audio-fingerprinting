# Audio Fingerprinting System

## Overview
An advanced, production-ready audio fingerprinting system inspired by the Shazam algorithm, capable of identifying music tracks with high accuracy and performance.

## Features
- Robust audio fingerprinting algorithm
- Parallel processing of audio files
- SQLite-based fingerprint database
- Configurable through YAML and environment variables
- Command-line interface
- Performance monitoring

## Prerequisites
- Python 3.8+
- pip

## Installation

### Clone the Repository
```bash
git clone https://github.com/iBehzod/audio-fingerprinting.git
cd audio-fingerprinting
```

### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies
```bash
pip install -e .
```

## Usage

### Fingerprinting Audio Files
```bash
# Fingerprint all audio files in a directory
audio-fingerprint fingerprint /path/to/music/directory

# Recursive directory search
audio-fingerprint fingerprint /path/to/music/directory --recursive
```

### Matching Audio Files
```bash
# Match a single audio file
audio-fingerprint match /path/to/sample.mp3
```

## Configuration

### Environment Variables
- `DB_PATH`: Database file path
- `SAMPLE_RATE`: Audio sampling rate
- `LOG_LEVEL`: Logging verbosity

### YAML Configuration
Modify `config/config.yaml` to customize system parameters:
```yaml
database:
  path: 'audio_fingerprints.db'
  max_connections: 10

fingerprinting:
  sample_rate: 16000
  n_fft: 2048
  hop_length: 512
  max_peaks: 100
```

## Running Tests
```bash
pytest tests/
```


## License
Distributed under the MIT License. See `LICENSE` for more information.

