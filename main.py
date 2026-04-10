# BOT/
# ├── commands/
# │   ├── 01_Moderação/
# │   ├── 02_Entretenimento/
# │   └── 03_RPG/                 ← todo o conteúdo desta pasta vai aqui
# │       ├── cogs/
# │       │   ├── __init__.py
# │       │   ├── comandos.py
# │       │   └── commands/
# │       │       ├── combat/     (dungeon.py, fight.py, pvp.py, raid.py)
# │       │       ├── equipment/  (equip.py, forge.py, inventory.py)
# │       │       ├── help/       (help.py)
# │       │       ├── heroes/
# │       │       ├── resources/  (bank.py, shop.py, trade.py)
# │       │       ├── stats/      (advancements.py, dex.py, stats.py)
# │       │       └── zones/      (change_zone.py, zone.py)
# │       ├── cogs/game/          (characters, items, zones)
# │       ├── cogs/utils/         (database, querys, hero_actions …)
# │       └── data/               (players.json)
# ├── DataBase/
# │   ├── bases.json
# │   └── prefixes.json
# └── main.py  (Arquivo principal do bot, responsável por carregar os cogs e iniciar o bot)


import os
import sys
import json
import ast
import asyncio
import logging
import time
from pathlib import Path
from typing import Any
import status

import discord
from discord.ext import commands

from mongo import close_mongodb, get_mongodb_settings, initialize_mongodb

# ==========================
# LOGGING
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

log = logging.getLogger("bot")

# Identidade desta instância (ajuda a detectar múltiplos processos rodando)
BOT_INSTANCE_ID = f"pid={os.getpid()}@{int(time.time())}"

# ==========================
# CAMINHOS
# ==========================

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

DB_DIR = BASE_DIR / "DataBase"
PREFIX_FILE = DB_DIR / "prefixes.json"

# ==========================
# CONFIG
# ==========================

def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise RuntimeError(
            "config.json não encontrado. Crie o arquivo com ao menos {'TOKEN': 'seu_token', 'prefix': '!'}"
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()

DEFAULT_PREFIX = config.get("prefix", "!")
DEV_GUILD_ID   = config.get("dev_guild_id")
MONGODB_URI, MONGODB_DATABASE = get_mongodb_settings(config)

# ==========================
# PREFIXOS POR SERVIDOR
# ==========================

def load_prefixes() -> dict:
    if not PREFIX_FILE.exists():
        return {}
    try:
        with open(PREFIX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_prefixes(data: dict) -> None:
    DB_DIR.mkdir(exist_ok=True)
    with open(PREFIX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_prefix(bot: commands.Bot, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(bot.default_prefix)(bot, message)
    prefix = bot.prefix_cache.get(str(message.guild.id), bot.default_prefix)
    return commands.when_mentioned_or(prefix)(bot, message)

# ==========================
# INTENTS
# ==========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# ==========================
# BOT
# ==========================

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None
)

bot.default_prefix = DEFAULT_PREFIX
bot.prefix_cache   = load_prefixes()
bot.prefixes_cache = bot.prefix_cache

# ==========================
# CARREGAMENTO DE COGS
# ==========================

def is_extension_module(file_path: Path) -> bool:
    try:
        source = file_path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source, filename=str(file_path))
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        log.warning(f"[COG SKIP] Não foi possível analisar {file_path}: {exc}")
        return False

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "setup":
            return True
    return False

async def load_extensions() -> None:
    """
    Carrega recursivamente todos os .py dentro de commands/ usando
    o nome completo do módulo a partir da raiz do projeto.

    Exemplo:
      commands/RPG/commands/combat/dungeon.py
      → módulo carregado como commands.RPG.commands.combat.dungeon

    Isso mantém os imports internos consistentes, como
    `from commands.RPG.utils.database import ...`.
    """
    commands_dir = BASE_DIR / "commands"

    if not commands_dir.exists():
        log.warning("Pasta 'commands/' não encontrada. Nenhum cog carregado.")
        return

    base_dir_str = str(BASE_DIR)
    if base_dir_str not in sys.path:
        sys.path.insert(0, base_dir_str)

    loaded_modules: set[str] = set()

    for file in sorted(commands_dir.rglob("*.py")):
        if file.name.startswith("_"):
            continue
        if not is_extension_module(file):
            continue

        module = str(file.relative_to(BASE_DIR)).replace(os.sep, ".")[:-3]

        if module in loaded_modules or module in bot.extensions:
            log.warning(f"[COG SKIP] já carregado → {module}")
            continue

        try:
            await bot.load_extension(module)
            loaded_modules.add(module)
            log.info(f"[COG] carregado → {module}")
        except Exception as e:
            log.error(f"[COG FAIL] {module} → {e}")

# ==========================
# SETUP HOOK
# ==========================

@bot.event
async def setup_hook() -> None:
    try:
        bot.mongo_db = initialize_mongodb(config)
    except Exception as exc:
        log.error(f"Erro ao conectar no MongoDB: {exc}")
        raise

    await load_extensions()

    # Módulos opcionais do bot principal (status, welcome, etc.)
    # Descomente conforme necessário:
    try:
     await status.initialize_status(bot)
     log.info("Status iniciado.")
    except Exception as e:
     log.error(f"Erro no status: {e}")

    # try:
    #     await welcome.initialize_welcome(bot)
    #     log.info("Welcome carregado.")
    # except Exception as e:
    #     log.error(f"Erro no welcome: {e}")

    # Prefix-only: não sincroniza slash commands.

# ==========================
# ON READY
# ==========================

@bot.event
async def on_ready() -> None:
    log.info(f"[READY] instance={BOT_INSTANCE_ID} user={bot.user} latency={round(bot.latency * 1000)}ms")
    cmds = sorted(c.name for c in bot.commands)
    log.info(f"{len(cmds)} comandos de prefixo carregados: {', '.join(cmds)}")
    if MONGODB_URI:
        log.info(f"[READY] MongoDB ativo no banco '{MONGODB_DATABASE}'")
    else:
        log.info("[READY] MongoDB inativo; persistencia segue em JSON.")


@bot.event
async def on_command(ctx: commands.Context) -> None:
    # Loga toda execução de comando de prefixo/híbrido para detectar duplicidade.
    # Se aparecer 2x (ou 4x) com o mesmo message.id e a mesma instance, é re-disparo interno.
    mid = getattr(getattr(ctx, "message", None), "id", None)
    gid = getattr(getattr(ctx, "guild", None), "id", None)
    aid = getattr(getattr(ctx, "author", None), "id", None)
    log.info(f"[CMD] instance={BOT_INSTANCE_ID} name={ctx.command.qualified_name if ctx.command else None} mid={mid} gid={gid} aid={aid}")

# ==========================
# EVENTOS DE SERVIDOR
# ==========================

@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    gid = str(guild.id)
    if gid not in bot.prefix_cache:
        bot.prefix_cache[gid] = bot.default_prefix
        save_prefixes(bot.prefix_cache)
        bot.prefixes_cache = bot.prefix_cache


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    gid = str(guild.id)
    if gid in bot.prefix_cache:
        bot.prefix_cache.pop(gid)
        save_prefixes(bot.prefix_cache)
        bot.prefixes_cache = bot.prefix_cache

# ==========================
# HANDLER DE ERROS GLOBAL
# ==========================

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você não tem permissão para usar este comando.")
        return
    log.error(f"Erro no comando '{ctx.command}': {error}")

# ==========================
# COMANDOS DE ADMINISTRAÇÃO
# ==========================

@bot.command(hidden=True)
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def debug_cmds(ctx: commands.Context) -> None:
    """Lista todos os comandos de prefixo carregados."""
    cmds = sorted(c.name for c in bot.commands)
    await ctx.send(f"Comandos carregados ({len(cmds)}):\n" + ", ".join(cmds))


@bot.command()
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
async def setprefix(ctx: commands.Context, prefix: str) -> None:
    """Altera o prefixo do bot neste servidor."""
    bot.prefix_cache[str(ctx.guild.id)] = prefix
    save_prefixes(bot.prefix_cache)
    bot.prefixes_cache = bot.prefix_cache
    await ctx.send(f"Prefixo alterado para **{prefix}**")

# ==========================
# MAIN
# ==========================

async def main() -> None:
    token = config.get("TOKEN")
    if not token:
        raise RuntimeError(
            "TOKEN não encontrado no config.json. "
            "Adicione {'TOKEN': 'seu_token_aqui'} ao arquivo."
        )
    try:
        async with bot:
            await bot.start(token)
    finally:
        close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())
