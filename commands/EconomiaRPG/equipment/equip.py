import discord
from discord import Embed, SelectOption
from discord.ui import Select, View
from discord.ext import commands
from commands.EconomiaRPG.utils.database import equip_item, get_active_hero, list_active_inventory
from commands.EconomiaRPG.utils.hero_check import hero_created
from commands.EconomiaRPG.utils.command_adapter import CommandContextAdapter
from commands.EconomiaRPG.utils.presentation import RPG_PRIMARY_COLOR, build_item_instance, get_rarity_label

class Equip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _build_selector_embed(display_name: str, slot_name: str, inventory_rows: list[dict], equipped_item_id: int | None):
        embed = Embed(title=f"Equipar {slot_name}", color=RPG_PRIMARY_COLOR)
        embed.description = f"Selecione abaixo qual {slot_name.lower()} ficarÃ¡ ativa no herÃ³i de {display_name}."
        equipped_name = "Nenhuma"
        if equipped_item_id is not None:
            equipped_row = next((row for row in inventory_rows if row["item_id"] == equipped_item_id), None)
            if equipped_row is not None:
                equipped_item = build_item_instance(equipped_row["type"], equipped_row["item_id"], equipped_row["level"])
                if equipped_item is not None:
                    equipped_name = f"{equipped_item.name} (nÃ­vel {equipped_row['level']})"
        embed.add_field(name="Atualmente equipado", value=equipped_name, inline=False)
        embed.add_field(name="Itens disponÃ­veis", value=str(len(inventory_rows)), inline=True)
        embed.add_field(name="Dica", value="Priorize itens com nÃ­vel e bÃ´nus melhores para aumentar o poder do herÃ³i.", inline=True)
        return embed

    async def _send_equip_selector(self, inte, *, item_type_id: int, item_type_name: str, slot_name: str):
        if not await hero_created(inte):
            return

        inventory_rows = list_active_inventory(inte.user.id, item_type_id=item_type_id)
        if not inventory_rows:
            return await inte.response.send_message(f"Voce nao possui {slot_name.lower()} para equipar.")

        hero_data = get_active_hero(inte.user.id) or {}
        equipped_item_id = hero_data.get("weapon_id") if item_type_id == 1 else hero_data.get("armor_id")

        class Dropdown(Select):
            def __init__(self, rows):
                options = []
                for row in rows[:25]:
                    item_obj = build_item_instance(row["type"], row["item_id"], row["level"])
                    if item_obj is None:
                        continue
                    options.append(
                        SelectOption(
                            value=str(row["item_id"]),
                            label=item_obj.name,
                            description=f"Nivel {row['level']} | {get_rarity_label(getattr(item_obj, 'rarity', None))}",
                            emoji="âš”ï¸" if item_type_id == 1 else "ðŸ›¡ï¸",
                        )
                    )
                super().__init__(placeholder=f"Escolha uma {slot_name.lower()} para equipar", min_values=1, max_values=1, options=options)

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != inte.user.id:
                    await interaction.response.send_message("Apenas quem abriu este menu pode equipar itens aqui.", ephemeral=True)
                    return

                selected_item_id = int(self.values[0])
                equip_item(inte.user.id, item_type_name, selected_item_id)
                refreshed_rows = list_active_inventory(inte.user.id, item_type_id=item_type_id)
                selected_row = next((row for row in refreshed_rows if row["item_id"] == selected_item_id), None)
                selected_item = None if selected_row is None else build_item_instance(selected_row["type"], selected_row["item_id"], selected_row["level"])
                embed = Equip._build_selector_embed(
                    inte.user.display_name,
                    slot_name,
                    refreshed_rows,
                    selected_item_id,
                )
                if selected_item is not None:
                    embed.add_field(
                        name="Equipado agora",
                        value=f"{selected_item.name} | Nivel {selected_row['level']}\n{selected_item.boosts}",
                        inline=False,
                    )
                await interaction.response.edit_message(embed=embed, view=None)

        view = View()
        view.add_item(Dropdown(inventory_rows))
        embed = self._build_selector_embed(inte.user.display_name, slot_name, inventory_rows, equipped_item_id)
        await inte.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.command(name='equip_weapon')
    async def equip_weapon(self, ctx):
        """Equipa uma arma."""
        inte = CommandContextAdapter(ctx)
        await self._send_equip_selector(inte, item_type_id=1, item_type_name="weapon", slot_name="Arma")
        
        
        
    @commands.command(name='equip_armor')
    async def equip_armor(self, ctx):
        """Equipa uma armadura."""
        inte = CommandContextAdapter(ctx)
        await self._send_equip_selector(inte, item_type_id=2, item_type_name="armor", slot_name="Armadura")



    

async def setup(bot):
    await bot.add_cog(Equip(bot))
