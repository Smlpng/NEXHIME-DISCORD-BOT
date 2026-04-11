import copy
import json
import logging
import os
from pathlib import Path
from typing import Any

try:
    import certifi
except ImportError:  # pragma: no cover - handled at runtime when certifi is unavailable
    certifi = None

try:
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    from pymongo.database import Database
except ImportError:  # pragma: no cover - handled at runtime when Mongo is enabled
    MongoClient = None
    ServerSelectionTimeoutError = Exception
    Database = Any


log = logging.getLogger("bot.mongo")

BASE_DIR = Path(__file__).resolve().parent
JSON_STORAGE_COLLECTION = "json_storage"

_client = None
_database = None


def _clone_default(default: Any) -> Any:
    return copy.deepcopy(default() if callable(default) else default)


def _normalize_document_key(document_key: str | os.PathLike[str]) -> str:
    path = Path(document_key)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    try:
        return path.relative_to(BASE_DIR).as_posix()
    except ValueError:
        return path.name


def load_json_document(
    document_key: str | os.PathLike[str],
    default: Any,
    *,
    legacy_path: str | os.PathLike[str] | None = None,
) -> Any:
    del legacy_path
    document_id = _normalize_document_key(document_key)

    database = get_mongodb_database()
    if database is None:
        raise RuntimeError("MongoDB nao esta conectado para leitura de documentos.")

    document = database[JSON_STORAGE_COLLECTION].find_one({"_id": document_id}, {"data": 1})
    if document and "data" in document:
        return copy.deepcopy(document["data"])

    return _clone_default(default)


def save_json_document(
    document_key: str | os.PathLike[str],
    data: Any,
    *,
    legacy_path: str | os.PathLike[str] | None = None,
) -> None:
    del legacy_path
    document_id = _normalize_document_key(document_key)

    database = get_mongodb_database()
    if database is None:
        raise RuntimeError("MongoDB nao esta conectado para escrita de documentos.")

    database[JSON_STORAGE_COLLECTION].replace_one(
        {"_id": document_id},
        {"_id": document_id, "data": copy.deepcopy(data)},
        upsert=True,
    )


def get_mongodb_settings(config: dict[str, Any]) -> tuple[str | None, str]:
    uri = os.getenv("MONGODB_URI") or config.get("MONGODB_URI")
    database_name = os.getenv("MONGODB_DATABASE") or config.get("MONGODB_DATABASE") or "nexhime_bot"
    return uri, database_name


def initialize_mongodb(config: dict[str, Any]) -> Any | None:
    global _client, _database

    uri, database_name = get_mongodb_settings(config)
    if not uri:
        log.info("MongoDB desabilitado: MONGODB_URI nao configurado.")
        return None

    if MongoClient is None:
        raise RuntimeError("MongoDB configurado, mas pymongo nao esta instalado. Instale a dependencia antes de iniciar o bot.")

    client_options: dict[str, Any] = {
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 20000,
        "socketTimeoutMS": 20000,
        "retryWrites": True,
    }
    if certifi is not None:
        client_options["tlsCAFile"] = certifi.where()

    try:
        _client = MongoClient(uri, **client_options)
        _client.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        close_mongodb()
        message = str(exc)
        if "SSL handshake failed" in message or "TLS" in message.upper():
            raise RuntimeError(
                "Falha no handshake TLS com o MongoDB Atlas. Verifique a URI, o IP liberado no Atlas, "
                "a senha com URL encoding e se a rede/antivirus nao esta interceptando SSL."
            ) from exc
        raise

    _database = _client[database_name]
    log.info(f"MongoDB conectado com sucesso ao banco '{database_name}'.")
    return _database


def get_mongodb_database() -> Any | None:
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