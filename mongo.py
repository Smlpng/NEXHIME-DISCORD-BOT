import logging
import os
from typing import Any

try:
    from pymongo import MongoClient
    from pymongo.database import Database
except ImportError:  # pragma: no cover - handled at runtime when Mongo is enabled
    MongoClient = None
    Database = Any


log = logging.getLogger("bot.mongo")

_client = None
_database = None


def get_mongodb_settings(config: dict[str, Any]) -> tuple[str | None, str]:
    uri = os.getenv("MONGODB_URI") or config.get("MONGODB_URI")
    database_name = os.getenv("MONGODB_DATABASE") or config.get("MONGODB_DATABASE") or "nexhime_bot"
    return uri, database_name


def initialize_mongodb(config: dict[str, Any]) -> Database | None:
    global _client, _database

    uri, database_name = get_mongodb_settings(config)
    if not uri:
        log.info("MongoDB desabilitado: MONGODB_URI nao configurado.")
        return None

    if MongoClient is None:
        raise RuntimeError("MongoDB configurado, mas pymongo nao esta instalado. Instale a dependencia antes de iniciar o bot.")

    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    _client.admin.command("ping")
    _database = _client[database_name]
    log.info(f"MongoDB conectado com sucesso ao banco '{database_name}'.")
    return _database


def get_mongodb_database() -> Database | None:
    return _database


def is_mongodb_enabled() -> bool:
    return _database is not None


def close_mongodb() -> None:
    global _client, _database

    if _client is not None:
        _client.close()
        log.info("Conexao MongoDB encerrada.")
    _client = None
    _database = None