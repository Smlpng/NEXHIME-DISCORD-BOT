import asyncio
import random

import discord
from discord.ext import commands


class DuelView(discord.ui.View):
    def __init__(self, challenger_id: int, target_id: int):
        super().__init__(timeout=20)
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.winner_id: int | None = None
        self.started = False
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in {self.challenger_id, self.target_id}:
            await interaction.response.send_message("Apenas os duelistas podem interagir.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aceitar duelo", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("Somente o desafiado pode aceitar.", ephemeral=True)
            return
        if self.started:
            await interaction.response.send_message("O duelo ja foi iniciado.", ephemeral=True)
            return

        self.started = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="Preparar... aguardem o sinal.", view=self)
        await asyncio.sleep(random.uniform(2.5, 5.5))

        self.clear_items()
        fire_button = discord.ui.Button(label="ATIRAR", style=discord.ButtonStyle.danger)

        async def fire_callback(fire_interaction: discord.Interaction):
            if fire_interaction.user.id not in {self.challenger_id, self.target_id}:
                await fire_interaction.response.send_message("Apenas os duelistas podem atirar.", ephemeral=True)
                return
            if self.winner_id is not None:
                await fire_interaction.response.send_message("O duelo ja terminou.", ephemeral=True)
                return
            self.winner_id = fire_interaction.user.id
            self.stop()
            await fire_interaction.response.edit_message(content=f"{fire_interaction.user.mention} venceu no reflexo.", view=None)

        fire_button.callback = fire_callback
        self.add_item(fire_button)
        if self.message is not None:
            await self.message.edit(content="AGORA.", view=self)

    async def on_timeout(self):
        if self.message is not None and self.winner_id is None:
            try:
                await self.message.edit(content="O duelo expirou sem vencedor.", view=None)
            except discord.HTTPException:
                pass


class Duelo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="duelo", aliases=["draw"], help="Desafie outro usuario para um duelo de reflexo.")
    async def duelo(self, ctx: commands.Context, membro: discord.Member):
        if membro.bot:
            return await ctx.reply("Voce nao pode duelar com bots.")
        if membro.id == ctx.author.id:
            return await ctx.reply("Voce nao pode duelar consigo mesmo.")

        view = DuelView(ctx.author.id, membro.id)
        message = await ctx.reply(f"{membro.mention}, {ctx.author.mention} quer um duelo. Clique para aceitar.", view=view)
        view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(Duelo(bot))