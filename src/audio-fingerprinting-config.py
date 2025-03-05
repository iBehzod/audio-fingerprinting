import os
import yaml
import logging
from typing import Dict, Any
import argparse
from dotenv import load_dotenv

class ConfigManager:
    """
    Centralized configuration management for audio fingerprinting system
    """
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        Initialize configuration from multiple sources
        """
        # Load environment variables
        load_dotenv()
        
        # Default configuration
        self.config = {
            'database': {
                'path': os.getenv('DB_PATH', 'audio_fingerprints.db'),
                'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', 10))
            },
            'fingerprinting': {
                'sample_rate': int(os.getenv('SAMPLE_RATE', 16000)),
                'n_fft': int(os.getenv('N_FFT', 2048)),
                'hop_length': int(os.getenv('HOP_LENGTH', 512)),
                'max_peaks': int(os.getenv('MAX_PEAKS', 100))
            },
            'matching': {
                'threshold': float(os.getenv('MATCH_THRESHOLD', 5.0)),
                'max_results': int(os.getenv('MAX_MATCH_RESULTS', 10))
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file': os.getenv('LOG_FILE', 'audio_fingerprinting.log')
            }
        }
        
        # Try to load configuration from YAML
        self._load_yaml_config()
    
    def _load_yaml_config(self):
        """
        Load configuration from YAML file
        """
        config_paths = [
            './config.yaml',
            './config.yml',
            os.path.expanduser('~/.audio_fingerprint/config.yaml')
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as file:
                        yaml_config = yaml.safe_load(file)
                        self._merge_configs(yaml_config)
                    break
                except Exception as e:
                    logging.warning(f"Could not load config from {path}: {e}")
    
    def _merge_configs(self, yaml_config: Dict[str, Any]):
        """
        Merge YAML configuration with existing config
        
        Args:
            yaml_config: Configuration from YAML file
        """
        def deep_merge(base, update):
            for key, value in update.items():
                if isinstance(value, dict):
                    base[key] = deep_merge(base.get(key, {}), value)
                else:
                    base[key] = value
            return base
        
        self.config = deep_merge(self.config, yaml_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with nested key support
        
        Args:
            key: Dot-separated configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def setup_logging(self):
        """
        Configure logging based on configuration
        """
        log_level = getattr(logging, self.get('logging.level', 'INFO').upper())
        log_file = self.get('logging.file')
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file) if log_file else logging.NullHandler()
            ]
        )

class PerformanceMonitor:
    """
    Performance monitoring and metrics collection
    """
    def __init__(self):
        self.metrics = {
            'fingerprinting_time': [],
            'matching_time': [],
            'database_size': 0,
            'total_tracks': 0
        }
    
    def record_fingerprinting_time(self, time_taken: float):
        """
        Record time taken for fingerprinting
        
        Args:
            time_taken: Time in seconds
        """
        self.metrics['fingerprinting_time'].append(time_taken)
    
    def record_matching_time(self, time_taken: float):
        """
        Record time taken for matching
        
        Args:
            time_taken: Time in seconds
        """
        self.metrics['matching_time'].append(time_taken)
    
    def update_database_metrics(self, total_tracks: int, database_size: int):
        """
        Update database-related metrics
        
        Args:
            total_tracks: Number of tracks in database
            database_size: Size of database in bytes
        """
        self.metrics['total_tracks'] = total_tracks
        self.metrics['database_size'] = database_size
    
    def get_performance_summary(self):
        """
        Generate performance summary
        
        Returns:
            Dictionary of performance metrics
        """
        import statistics
        
        return {
            'avg_fingerprinting_time': (
                statistics.mean(self.metrics['fingerprinting_time']) 
                if self.metrics['fingerprinting_time'] else 0
            ),
            'avg_matching_time': (
                statistics.mean(self.metrics['matching_time']) 
                if self.metrics['matching_time'] else 0
            ),
            'total_tracks': self.metrics['total_tracks'],
            'database_size': self.metrics['database_size']
        }

def parse_cli_arguments():
    """
    Parse command-line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Audio Fingerprinting System')
    parser.add_argument(
        '--config', 
        type=str, 
        help='Path to custom configuration file'
    )
    parser.add_argument(
        '--database', 
        type=str, 
        help='Path to audio fingerprint database'
    )
    parser.add_argument(
        'action', 
        choices=['fingerprint', 'match', 'stats'], 
        help='Action to perform'
    )
    parser.add_argument(
        'files', 
        nargs='*', 
        help='Audio files to process'
    )
    
    return parser.parse_args()

def main():
    # Parse CLI arguments
    args = parse_cli_arguments()
    
    # Initialize configuration
    config = ConfigManager()
    
    # Setup logging
    config.setup_logging()
    
    # Initialize performance monitor
    monitor = PerformanceMonitor()
    
    # Log configuration details
    logging.info("Audio Fingerprinting System Initialized")
    logging.info(f"Database Path: {config.get('database.path')}")
    logging.info(f"Logging Level: {config.get('logging.level')}")
    
    # Perform specified action
    if args.action == 'fingerprint':
        # Fingerprinting logic
        pass
    elif args.action == 'match':
        # Matching logic
        pass
    elif args.action == 'stats':
        # Print performance stats
        print(monitor.get_performance_summary())

if __name__ == "__main__":
    main()
