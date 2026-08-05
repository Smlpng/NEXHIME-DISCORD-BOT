import os
from dotenv import load_dotenv

# Carrega as variáveis definidas no arquivo .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip().strip('"').strip("'")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!").strip().strip('"').strip("'")
MONGO_URI = os.getenv("MONGO_URI", "").strip().strip('"').strip("'")
_raw_db_name = os.getenv("DB_NAME", "discord_bot_db").strip().strip('"').strip("'")

# Se DB_NAME contiver pontos ou barras (ex: se o usuário colou um domínio por engano), restaura para o padrão
if not _raw_db_name or "." in _raw_db_name or "/" in _raw_db_name:
    DB_NAME = "discord_bot_db"
else:
    DB_NAME = _raw_db_name

def validate_config():
    """Valida se os parâmetros essenciais estão configurados."""
    warnings = []
    if not DISCORD_TOKEN or DISCORD_TOKEN == "seu_token_do_discord_aqui":
        warnings.append("⚠️ DISCORD_TOKEN não foi configurado no arquivo .env!")
    if not MONGO_URI or "usuario:senha" in MONGO_URI:
        warnings.append("⚠️ MONGO_URI não foi configurada corretamente no arquivo .env!")
    if _raw_db_name != DB_NAME:
        warnings.append(f"⚠️ DB_NAME no .env contém caracteres inválidos ('{_raw_db_name}'). Usando '{DB_NAME}' como padrão.")
    return warnings

