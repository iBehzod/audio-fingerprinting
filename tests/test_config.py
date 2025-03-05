import pytest
import os
import tempfile
import yaml
from src.config import ConfigManager

class TestConfigManager:
    @pytest.fixture
    def temp_yaml_config(self):
        # Create a temporary YAML config file
        test_config = {
            'database': {
                'path': '/tmp/test_database.db',
                'max_connections': 15
            },
            'fingerprinting': {
                'sample_rate': 22050,
                'n_fft': 1024,
                'hop_length': 256,
                'max_peaks': 50
            },
            'matching': {
                'threshold': 3.0,
                'max_results': 5
            },
            'logging': {
                'level': 'DEBUG',
                'file': '/tmp/test_log.log'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            yaml.dump(test_config, temp_file)
        
        yield temp_file.name
        os.unlink(temp_file.name)

    def test_singleton_instance(self):
        # Verify that ConfigManager is a singleton
        config1 = ConfigManager()
        config2 = ConfigManager()
        assert config1 is config2

    def test_default_configuration(self):
        config = ConfigManager()
        
        # Check some default values
        assert config.get('database.path') is not None
        assert config.get('fingerprinting.sample_rate') == 16000
        assert config.get('matching.threshold') == 5.0

    def test_yaml_config_loading(self, temp_yaml_config, monkeypatch):
        # Monkeypatch config paths to use our temporary config
        monkeypatch.setattr(ConfigManager, '_load_yaml_config', 
            lambda self: self._merge_configs(yaml.safe_load(open(temp_yaml_config, 'r'))))
        
        config = ConfigManager()
        
        # Verify YAML config values
        assert config.get('database.path') == '/tmp/test_database.db'
        assert config.get('database.max_connections') == 15
        assert config.get('fingerprinting.sample_rate') == 22050
        assert config.get('matching.threshold') == 3.0

    def test_nested_key_retrieval(self):
        config = ConfigManager()
        
        # Test nested key retrieval
        sample_rate = config.get('fingerprinting.sample_rate')
        assert sample_rate is not None
        assert isinstance(sample_rate, int)

    def test_default_value_retrieval(self):
        config = ConfigManager()
        
        # Test retrieving non-existent key with default
        value = config.get('non.existent.key', 'default_value')
        assert value == 'default_value'