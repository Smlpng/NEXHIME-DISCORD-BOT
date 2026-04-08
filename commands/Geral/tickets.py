import discord
from discord.ext import commands


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar ticket", style=discord.ButtonStyle.danger, custom_id="ticket_close_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel or not isinstance(interaction.channel, discord.TextChannel):
            return await interaction.response.send_message("Canal invalido.", ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Apenas a staff pode fechar tickets.", ephemeral=True)
            return
        await interaction.response.send_message("Fechando ticket...", ephemeral=True)
        await interaction.channel.delete(reason=f"Ticket fechado por {interaction.user}")


class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir ticket", style=discord.ButtonStyle.success, custom_id="ticket_open_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("Este comando so funciona em servidor.", ephemeral=True)

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing is not None:
            return await interaction.response.send_message(f"Voce ja possui um ticket aberto: {existing.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, read_message_history=True),
        }
        category = interaction.channel.category if isinstance(interaction.channel, discord.TextChannel) else None
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            category=category,
            overwrites=overwrites,
            reason=f"Ticket aberto por {interaction.user}",
        )
        await channel.send(
            f"{interaction.user.mention}, este e o seu ticket. Descreva o problema e aguarde a staff.",
            view=TicketCloseView(),
        )
        await interaction.response.send_message(f"Ticket criado em {channel.mention}.", ephemeral=True)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.add_view(TicketOpenView())
        self.bot.add_view(TicketCloseView())

    @staticmethod
    def _is_ticket_channel(channel: discord.abc.GuildChannel | None) -> bool:
        return isinstance(channel, discord.TextChannel) and channel.name.startswith("ticket-")

    @commands.command(name="tickets", aliases=["ticketspanel"], help="Posta um painel para abertura de tickets.")
    @commands.has_permissions(manage_channels=True)
    async def tickets(self, ctx: commands.Context):
        embed = discord.Embed(title="Atendimento", description="Clique no botao abaixo para abrir um ticket com a equipe.", color=discord.Color.blurple())
        await ctx.reply(embed=embed, view=TicketOpenView())

    @commands.command(name="fecharticket", aliases=["closeticket"], help="Fecha o ticket atual.")
    @commands.has_permissions(manage_channels=True)
    async def fecharticket(self, ctx: commands.Context):
        if not self._is_ticket_channel(ctx.channel):
            return await ctx.reply("Esse comando so pode ser usado dentro de um ticket.")
        await ctx.reply("Fechando ticket...")
        await ctx.channel.delete(reason=f"Ticket fechado por {ctx.author}")

    @commands.command(name="ticketadd", help="Adiciona um usuario ao ticket atual.")
    @commands.has_permissions(manage_channels=True)
    async def ticketadd(self, ctx: commands.Context, membro: discord.Member):
        if not self._is_ticket_channel(ctx.channel):
            return await ctx.reply("Esse comando so pode ser usado dentro de um ticket.")
        overwrite = ctx.channel.overwrites_for(membro)
        overwrite.view_channel = True
        overwrite.send_messages = True
        overwrite.read_message_history = True
        await ctx.channel.set_permissions(membro, overwrite=overwrite, reason=f"Ticket add por {ctx.author}")
        await ctx.reply(f"{membro.mention} foi adicionado ao ticket.")

    @commands.command(name="ticketremove", help="Remove um usuario do ticket atual.")
    @commands.has_permissions(manage_channels=True)
    async def ticketremove(self, ctx: commands.Context, membro: discord.Member):
        if not self._is_ticket_channel(ctx.channel):
            return await ctx.reply("Esse comando so pode ser usado dentro de um ticket.")
        overwrite = ctx.channel.overwrites_for(membro)
        overwrite.view_channel = False
        overwrite.send_messages = False
        await ctx.channel.set_permissions(membro, overwrite=overwrite, reason=f"Ticket remove por {ctx.author}")
        await ctx.reply(f"{membro.mention} foi removido do ticket.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))