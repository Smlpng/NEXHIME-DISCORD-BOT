import random

import discord
from discord.ext import commands


EMOJIS = ["🍌", "🐉", "👑", "⚔️", "🌙", "🔥"]


class MemoryButton(discord.ui.Button):
    def __init__(self, index: int):
        super().__init__(label="?", style=discord.ButtonStyle.secondary)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, MemoryView):
            await view.reveal(interaction, self.index)


class MemoryView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        cards = EMOJIS[:6] + EMOJIS[:6]
        random.shuffle(cards)
        self.user_id = user_id
        self.cards = cards
        self.revealed: set[int] = set()
        self.current_pair: list[int] = []
        self.message: discord.Message | None = None
        for index in range(12):
            self.add_item(MemoryButton(index))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Apenas quem abriu o jogo pode usar essa memoria.", ephemeral=True)
            return False
        return True

    async def reveal(self, interaction: discord.Interaction, index: int):
        if index in self.revealed or index in self.current_pair:
            return await interaction.response.defer()
        self.current_pair.append(index)
        await self._refresh(interaction)

        if len(self.current_pair) == 2:
            first, second = self.current_pair
            if self.cards[first] == self.cards[second]:
                self.revealed.update(self.current_pair)
            else:
                await interaction.message.edit(view=self)
                await discord.utils.sleep_until(discord.utils.utcnow())
            self.current_pair = []
            await self._refresh(None)

        if len(self.revealed) == len(self.cards):
            self.stop()
            if self.message is not None:
                await self.message.edit(content="Voce completou o jogo da memoria.", view=self)

    async def _refresh(self, interaction: discord.Interaction | None):
        for child in self.children:
            if not isinstance(child, MemoryButton):
                continue
            if child.index in self.revealed or child.index in self.current_pair:
                child.label = self.cards[child.index]
                child.disabled = child.index in self.revealed
                child.style = discord.ButtonStyle.success if child.index in self.revealed else discord.ButtonStyle.primary
            else:
                child.label = "?"
                child.disabled = False
                child.style = discord.ButtonStyle.secondary
        if interaction is not None:
            await interaction.response.edit_message(view=self)
        elif self.message is not None:
            await self.message.edit(view=self)


class Memoria(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="memoria", aliases=["memory"], help="Joga um pequeno jogo da memoria com emojis.")
    async def memoria(self, ctx: commands.Context):
        view = MemoryView(ctx.author.id)
        message = await ctx.reply("Combine os pares.", view=view)
        view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(Memoria(bot))