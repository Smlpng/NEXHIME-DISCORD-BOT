from mongo import get_mongodb_settings, initialize_mongodb


def test_get_mongodb_settings_uses_config_defaults(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.delenv("MONGODB_DATABASE", raising=False)

    uri, database_name = get_mongodb_settings({"MONGODB_URI": "mongodb://example", "MONGODB_DATABASE": "nex"})

    assert uri == "mongodb://example"
    assert database_name == "nex"


def test_initialize_mongodb_returns_none_when_uri_missing(monkeypatch):
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.delenv("MONGODB_DATABASE", raising=False)

    assert initialize_mongodb({}) is None