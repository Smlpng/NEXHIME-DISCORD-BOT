import os
from pathlib import Path
import discord
from discord.ext import commands

from mongo import load_json_document, save_json_document

PREFIXES_FILE = Path("DataBase") / "prefixes.json"

def load_json(path: Path, default: dict) -> dict:
    data = load_json_document(path, default)
    return data if isinstance(data, dict) else default

def save_json(path: Path, data: dict) -> None:
    save_json_document(path, data)

class PrefixModeration(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="prefix", help="Gerenciar o prefixo do servidor.")
    @commands.has_permissions(administrator=True)
    async def prefix_view(self, ctx: commands.Context):
        """Sem subcomando: mostra o prefixo atual deste servidor."""
        if ctx.guild is None:
            return await ctx.reply("Este comando só pode ser usado em servidores.")
        prefixes = load_json(PREFIXES_FILE, {})
        default_prefix = getattr(self.bot, "default_prefix", "e!")
        current = prefixes.get(str(ctx.guild.id), default_prefix)
        # Exibe também o padrão entre colchetes, para consistência com o help
        label = f"[{default_prefix}]" if current == default_prefix else f"[{default_prefix}] {current}"
        await ctx.reply(f"Prefixos aceitos neste servidor: `{label}`")

    @commands.command(name="set", help="Define um novo prefixo para este servidor.")
    @commands.has_permissions(administrator=True)
    async def prefix_set(self, ctx: commands.Context, novo_prefixo: str):
        if ctx.guild is None:
            return await ctx.reply("Este comando só pode ser usado em servidores.")
        if not (1 <= len(novo_prefixo) <= 5):
            return await ctx.reply("Prefixo inválido. Use entre 1 e 5 caracteres.")
        prefixes = load_json(PREFIXES_FILE, {})
        prefixes[str(ctx.guild.id)] = novo_prefixo
        save_json(PREFIXES_FILE, prefixes)
        self.bot.prefix_cache = prefixes
        self.bot.prefixes_cache = self.bot.prefix_cache
        default_prefix = getattr(self.bot, "default_prefix", "e!")
        label = f"[{default_prefix}]" if novo_prefixo == default_prefix else f"[{default_prefix}] {novo_prefixo}"
        await ctx.reply(f"Prefixo atualizado. Agora aceitos: `{label}`")

    @commands.command(name="reset", help="Restaura o prefixo padrão (config.json) neste servidor.")
    @commands.has_permissions(administrator=True)
    async def prefix_reset(self, ctx: commands.Context):
        if ctx.guild is None:
            return await ctx.reply("Este comando só pode ser usado em servidores.")
        prefixes = load_json(PREFIXES_FILE, {})
        default_prefix = getattr(self.bot, "default_prefix", "e!")
        prefixes[str(ctx.guild.id)] = default_prefix
        save_json(PREFIXES_FILE, prefixes)
        self.bot.prefix_cache = prefixes
        self.bot.prefixes_cache = self.bot.prefix_cache
        await ctx.reply(f"Prefixo restaurado. Agora aceitos: `[{default_prefix}]`")

    @commands.command(name="show_prefix", help="Mostra o prefixo atual e o padrão.")
    @commands.has_permissions(administrator=True)
    async def prefix_show(self, ctx: commands.Context):
        if ctx.guild is None:
            return await ctx.reply("Este comando só pode ser usado em servidores.")
        prefixes = load_json(PREFIXES_FILE, {})
        default_prefix = getattr(self.bot, "default_prefix", "e!")
        current = prefixes.get(str(ctx.guild.id), default_prefix)
        label = f"[{default_prefix}]" if current == default_prefix else f"[{default_prefix}] {current}"
        await ctx.reply(f"Prefixos aceitos neste servidor: `{label}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(PrefixModeration(bot))
