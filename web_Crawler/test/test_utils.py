from web_Crawler.utils.utils import load_config
from pathlib import Path
import pytest
@pytest.fixture
def config_path():
    # returns absolute path to your config YAML
    root = Path(__file__).resolve().parents[1]  # web_Crawler
    return str(root / "config" / "hiring_caffe_config.yaml")
def test_config(config_path):
    """Test loading configuration file."""
    config = load_config(config_path)
    import assertpy
    print("Configuration loaded successfully:")
    for key, value in config.items():
        print(f"{key}: {value}")
    assertpy.assert_that(config).is_instance_of(dict)
    assertpy.assert_that(config).is_not_empty()
    assertpy.assert_that(config).contains_key('BASE_URL')
    print(config['BASE_URL'])
