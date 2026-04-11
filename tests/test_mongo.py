import json

import pytest

import mongo
from mongo import get_mongodb_settings, initialize_mongodb, load_json_document, save_json_document


class FakeCollection:
    def __init__(self):
        self.documents = {}

    def find_one(self, query, projection=None):
        return self.documents.get(query["_id"])

    def replace_one(self, query, document, upsert=False):
        self.documents[query["_id"]] = document

    def count_documents(self, query, limit=0):
        return int(query["_id"] in self.documents)

    def insert_one(self, document):
        self.documents[document["_id"]] = document


class FakeDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = FakeCollection()
        return self.collections[name]


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


def test_load_json_document_requires_mongo_connection(monkeypatch):
    monkeypatch.setattr(mongo, "_database", None)

    with pytest.raises(RuntimeError, match="MongoDB nao esta conectado"):
        load_json_document("DataBase/afk.json", {})


def test_save_json_document_requires_mongo_connection(monkeypatch):
    monkeypatch.setattr(mongo, "_database", None)

    with pytest.raises(RuntimeError, match="MongoDB nao esta conectado"):
        save_json_document("DataBase/prefixes.json", {"1": "!"})


def test_load_json_document_returns_default_when_document_missing(monkeypatch):
    fake_db = FakeDatabase()
    monkeypatch.setattr(mongo, "_database", fake_db)

    loaded = load_json_document("DataBase/quotes_guild.json", {"guild": []})

    assert loaded == {"guild": []}


def test_save_then_load_json_document_roundtrip(monkeypatch):
    fake_db = FakeDatabase()
    monkeypatch.setattr(mongo, "_database", fake_db)

    save_json_document("DataBase/quotes_guild.json", {"guild": []})
    loaded = load_json_document("DataBase/quotes_guild.json", {})

    assert loaded == {"guild": []}
    stored = fake_db[mongo.JSON_STORAGE_COLLECTION].documents["DataBase/quotes_guild.json"]
    assert stored["data"] == {"guild": []}