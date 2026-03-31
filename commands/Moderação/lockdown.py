import discord
from discord.ext import commands


class Lockdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="lockdown",
        help="Tranca/destranca vários canais. Uso: lockdown on|off [categoria]",
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx: commands.Context, acao: str, categoria: discord.CategoryChannel | None = None):
        if ctx.guild is None:
            return await ctx.reply("Este comando funciona em servidores.", mention_author=False)

        acao = (acao or "").strip().lower()
        if acao not in {"on", "off", "ativar", "desativar"}:
            return await ctx.reply("Use `lockdown on` ou `lockdown off`.", mention_author=False)

        channels = []
        if categoria is not None:
            channels = list(categoria.text_channels)
        else:
            channels = [ch for ch in ctx.guild.text_channels]

        enable = acao in {"on", "ativar"}
        updated = 0
        failed = 0
        for ch in channels:
            try:
                overwrites = ch.overwrites_for(ctx.guild.default_role)
                if enable:
                    overwrites.send_messages = False
                    overwrites.add_reactions = False
                else:
                    overwrites.send_messages = None
                    overwrites.add_reactions = None
                await ch.set_permissions(ctx.guild.default_role, overwrite=overwrites, reason=f"Lockdown por {ctx.author}")
                updated += 1
            except Exception:
                failed += 1

        scope = f"na categoria {categoria.name}" if categoria else "no servidor"
        if enable:
            await ctx.reply(f"🔒 Lockdown ativado {scope}. Canais atualizados: {updated}. Falhas: {failed}.", mention_author=False)
        else:
            await ctx.reply(f"🔓 Lockdown desativado {scope}. Canais atualizados: {updated}. Falhas: {failed}.", mention_author=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Lockdown(bot))
