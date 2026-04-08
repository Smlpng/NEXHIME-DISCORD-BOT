from typing import Optional

import discord
from discord.ext import commands

from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.database import ensure_profile, get_active_hero, set_active_hero_race


RACES = [
    "Macaco-prego",
    "Bugio",
    "Mandril",
    "Orangotango",
    "Gorila",
]


class RaceSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=race, value=race) for race in RACES]
        super().__init__(placeholder="Selecione sua raÃ§a", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_value = self.values[0]
        await interaction.response.defer()
        self.view.stop()


class RaceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.selected_value: Optional[str] = None
        self.add_item(RaceSelect())


class Race(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="escolher_raca")
    async def escolher_raca(self, ctx, *, raca: Optional[str] = None):
        """Define a raÃ§a do herÃ³i atual."""
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        hero = get_active_hero(inte.user.id)

        if hero is None:
            return await inte.response.send_message("Seu perfil ainda nao esta pronto para escolher uma raca.")

        if hero.get("race"):
            return await inte.response.send_message(f"Seu heroi ja tem uma raca definida: {hero['race']}.", ephemeral=True)

        if raca is None:
            view = RaceView()
            await inte.response.send_message("Escolha a raÃ§a do seu herÃ³i:", view=view, ephemeral=True)
            await view.wait()
            if view.selected_value is None:
                return await inte.followup.send("Tempo esgotado. Tente novamente quando quiser.", ephemeral=True)
            raca = view.selected_value

        if raca is None:
            options = ", ".join(RACES)
            return await inte.response.send_message(f"Informe uma raÃ§a valida. Opcoes: {options}")

        selected_race = next((item for item in RACES if item.lower() == raca.lower()), None)
        if selected_race is None:
            return await inte.response.send_message("Raca invalida. Use uma das opcoes mostradas pelo comando.", ephemeral=True)

        set_active_hero_race(inte.user.id, selected_race)

        embed = discord.Embed(title="RaÃ§a definida", color=discord.Color.blue())
        embed.add_field(name="HerÃ³i", value=inte.user.display_name, inline=True)
        embed.add_field(name="RaÃ§a", value=selected_race, inline=True)
        embed.set_footer(text="VocÃª pode ver essa informaÃ§Ã£o no menu do herÃ³i.")
        await inte.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Race(bot))