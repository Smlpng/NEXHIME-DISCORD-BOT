import discord
from discord import Embed
from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import (
    active_hero_has_title,
    ensure_profile,
    get_active_hero_title,
    list_active_hero_titles,
    set_active_hero_title,
)
from commands.RPG.utils.presentation import RPG_PRIMARY_COLOR


class Titulos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="titulo",
        aliases=["título", "titulos", "títulos"],
        invoke_without_command=True,
        help="Gerencia seus títulos do RPG (comprar/usar/listar).",
    )
    async def titulo(self, ctx: commands.Context, *, name: str | None = None):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        # Atalho: `titulo <nome>` equivale a `titulo usar <nome>`.
        if name:
            await self._use_title(inte, name)
            return

        current = get_active_hero_title(inte.user.id) or "Sem título"
        owned = list_active_hero_titles(inte.user.id)
        owned_text = "\n".join(f"- {t}" for t in owned) if owned else "(nenhum)"

        embed = Embed(title="Títulos", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Título equipado", value=current, inline=False)
        embed.add_field(name="Seus títulos", value=owned_text, inline=False)
        embed.add_field(
            name="Como usar",
            value=(
                "`titulo usar <nome>`\n"
                "`titulo remover`\n"
                "Compre títulos em `loja` e equipe com `titulo usar`."
            ),
            inline=False,
        )
        await inte.response.send_message(embed=embed)

    @titulo.command(name="lista", aliases=["list"])
    async def titulo_lista(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        current = get_active_hero_title(inte.user.id) or "Sem título"
        owned = list_active_hero_titles(inte.user.id)
        owned_text = "\n".join(f"- {t}" for t in owned) if owned else "(nenhum)"

        embed = Embed(title="Seus Títulos", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Equipado", value=current, inline=False)
        embed.add_field(name="Possuídos", value=owned_text, inline=False)
        await inte.response.send_message(embed=embed)

    async def _use_title(self, inte: CommandContextAdapter, name: str):
        title_name = (name or "").strip()
        if not title_name:
            await inte.response.send_message("Informe o nome do título. Ex: `titulo usar O pensador`")
            return

        if not active_hero_has_title(inte.user.id, title_name):
            await inte.response.send_message(
                "Você não possui esse título. Use `titulo loja` para ver os títulos disponíveis para compra."
            )
            return

        ok = set_active_hero_title(inte.user.id, title_name)
        if not ok:
            await inte.response.send_message("Não consegui equipar esse título agora.")
            return

        await inte.response.send_message(f"Título equipado: **{title_name}**")

    @titulo.command(name="usar", aliases=["equip", "set"])
    async def titulo_usar(self, ctx: commands.Context, *, name: str):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        await self._use_title(inte, name)

    @titulo.command(name="remover", aliases=["clear", "unequip"])
    async def titulo_remover(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        ok = set_active_hero_title(inte.user.id, None)
        if not ok:
            await inte.response.send_message("Não consegui remover o título agora.")
            return

        await inte.response.send_message("Título removido. Você está sem título.")


async def setup(bot):
    await bot.add_cog(Titulos(bot))
