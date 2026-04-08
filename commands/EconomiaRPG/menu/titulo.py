import discord
from discord import Embed
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import (
    active_hero_has_title,
    ensure_profile,
    get_active_hero_title,
    list_active_hero_titles,
    set_active_hero_title,
)
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR


class Titulos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="titulo",
        aliases=["tÃ­tulo", "titulos", "tÃ­tulos"],
        invoke_without_command=True,
        help="Gerencia seus tÃ­tulos do RPG (comprar/usar/listar).",
    )
    async def titulo(self, ctx: commands.Context, *, name: str | None = None):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        # Atalho: `titulo <nome>` equivale a `titulo usar <nome>`.
        if name:
            await self._use_title(inte, name)
            return

        current = get_active_hero_title(inte.user.id) or "Sem tÃ­tulo"
        owned = list_active_hero_titles(inte.user.id)
        owned_text = "\n".join(f"- {t}" for t in owned) if owned else "(nenhum)"

        embed = Embed(title="TÃ­tulos", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="TÃ­tulo equipado", value=current, inline=False)
        embed.add_field(name="Seus tÃ­tulos", value=owned_text, inline=False)
        embed.add_field(
            name="Como usar",
            value=(
                "`titulo usar <nome>`\n"
                "`titulo remover`\n"
                "Compre tÃ­tulos em `loja` e equipe com `titulo usar`."
            ),
            inline=False,
        )
        await inte.response.send_message(embed=embed)

    @titulo.command(name="lista", aliases=["list"])
    async def titulo_lista(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)

        current = get_active_hero_title(inte.user.id) or "Sem tÃ­tulo"
        owned = list_active_hero_titles(inte.user.id)
        owned_text = "\n".join(f"- {t}" for t in owned) if owned else "(nenhum)"

        embed = Embed(title="Seus TÃ­tulos", color=RPG_PRIMARY_COLOR)
        embed.add_field(name="Equipado", value=current, inline=False)
        embed.add_field(name="PossuÃ­dos", value=owned_text, inline=False)
        await inte.response.send_message(embed=embed)

    async def _use_title(self, inte: CommandContextAdapter, name: str):
        title_name = (name or "").strip()
        if not title_name:
            await inte.response.send_message("Informe o nome do tÃ­tulo. Ex: `titulo usar O pensador`")
            return

        if not active_hero_has_title(inte.user.id, title_name):
            await inte.response.send_message(
                "VocÃª nÃ£o possui esse tÃ­tulo. Use `titulo loja` para ver os tÃ­tulos disponÃ­veis para compra."
            )
            return

        ok = set_active_hero_title(inte.user.id, title_name)
        if not ok:
            await inte.response.send_message("NÃ£o consegui equipar esse tÃ­tulo agora.")
            return

        await inte.response.send_message(f"TÃ­tulo equipado: **{title_name}**")

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
            await inte.response.send_message("NÃ£o consegui remover o tÃ­tulo agora.")
            return

        await inte.response.send_message("TÃ­tulo removido. VocÃª estÃ¡ sem tÃ­tulo.")


async def setup(bot):
    await bot.add_cog(Titulos(bot))
