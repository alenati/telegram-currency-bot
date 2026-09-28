from config import Config
from pathlib import Path

def test_config_edge_cases():
    assert Config.LANGUAGE in {"ru", "sk", "en", None}
    assert Config.LOGS in {"true", "false", None}

def test_db_config_has_required_fields():
    assert Config.PG_HOST
    assert Config.PG_USER
    assert Config.PG_DB_NAME
    assert Config.PG_PASSWORD

def test_telegram_token_is_non_empty_string():
    assert isinstance(Config.TG_API_KEY, str)

def test_default_translation_file_exists():
    assert Path("messages/ru/welcome.json").exists()
    assert Path("messages/en/welcome.json").exists()
    assert Path("messages/sk/welcome.json").exists()