import asyncio
import importlib.util
import logging
import pathlib
import re
import sys
import discord
from discord.ext import commands

import config
from database import db_manager

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot.main")

class MongoDiscordBot(commands.Bot):
    def __init__(self):
        # Intents padrão + message_content (necessário para comandos de texto)
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )

    async def setup_hook(self):
        """Executado antes de o bot se conectar ao Discord."""
        logger.info("Iniciando conexão com MongoDB Atlas...")
        db_connected = await db_manager.connect()
        if not db_connected:
            logger.warning("⚠️ Conexão com MongoDB falhou ou não configurada. O bot iniciará, mas recursos de BD estarão indisponíveis.")

        # Carrega automaticamente todos os comandos na pasta commands
        await self.load_all_command_extensions()

    async def load_all_command_extensions(self):
        commands_dir = pathlib.Path(__file__).parent / "commands"
        logger.info(f"Procurando comandos em: {commands_dir}")

        if not commands_dir.exists():
            logger.error(f"Diretório de comandos não encontrado: {commands_dir}")
            return

        module_paths = []
        for path in commands_dir.rglob("*.py"):
            if path.name == "__init__.py":
                continue

            relative_path = path.relative_to(pathlib.Path(__file__).parent)
            module_name = ".".join(relative_path.with_suffix("").parts)
            module_name = re.sub(r"[^0-9a-zA-Z_\.]+", "_", module_name)
            module_paths.append((path, module_name))

        for path, module_name in sorted(module_paths):
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Não foi possível criar spec para {path}")

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                if hasattr(module, "setup") and callable(module.setup):
                    await module.setup(self)
                    logger.info(f"Comando carregado: {module_name}")
                else:
                    logger.warning(f"Módulo sem função setup: {module_name}")
            except Exception as e:
                logger.error(f"Falha ao carregar comando '{module_name}' de {path}: {e}")

    async def on_ready(self):
        """Evento de quando o bot está online e conectado ao Discord."""
        logger.info(f"🤖 Bot online como {self.user} (ID: {self.user.id})")
        logger.info(f"Prefixo de comando: '{config.COMMAND_PREFIX}'")
        
        # Define o status do bot
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{config.COMMAND_PREFIX}help | MongoDB Atlas"
        )
        await self.change_presence(activity=activity)

    async def close(self):
        """Garante o encerramento correto do bot e da conexão com BD."""
        logger.info("Encerrando bot...")
        db_manager.close()
        await super().close()

async def main():
    # Valida configurações básicas
    warnings = config.validate_config()
    for warning in warnings:
        logger.warning(warning)

    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "seu_token_do_discord_aqui":
        logger.error("❌ Não é possível iniciar o bot sem um DISCORD_TOKEN válido no arquivo .env!")
        logger.info("Edite o arquivo .env e coloque o seu Token do Discord e a sua MONGO_URI.")
        return

    bot = MongoDiscordBot()
    async with bot:
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário.")
