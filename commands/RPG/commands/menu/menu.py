import discord
from discord import Embed, SelectOption
from discord.ext import commands
from discord.ui import Button, Select, View
from commands.RPG.utils.database import ensure_profile, get_active_hero, get_bank_balance, has_selected_class
from commands.RPG.utils.hero_actions import load_hero
from commands.RPG.game.characters.ability_info import abilities_embed
from commands.RPG.game.zones.embeds import zones_data
from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.create import create_hero

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _format_timestamp(value):
        if value is None:
            return "Desconhecida"
        return f"<t:{int(value.timestamp())}:F> (<t:{int(value.timestamp())}:R>)"

    @staticmethod
    def _resolve_zone_name(zone_id):
        if isinstance(zone_id, int) and 0 <= zone_id < len(zones_data):
            zone_name = zones_data[zone_id].get("name")
            if zone_name:
                return zone_name
        return "Não definida"

    @staticmethod
    def _build_progress_bar(current: int, total: int, size: int = 10):
        if total <= 0:
            total = 1
        progress = min(max(current / total, 0), 1)
        filled = round(size * progress)
        return "█" * filled + "░" * (size - filled)

    def _build_status_embed(self, inte, *, data, class_name, level, xp_value, xp_needed, hp_text, energy_text, image_url,
                            attack, defense, magic, magic_resistance, weapon_name, armor_name):
        bank_balance = get_bank_balance(inte.user.id)
        zone_name = self._resolve_zone_name(data.get("zone_id"))
        created_at = self._format_timestamp(getattr(inte.user, "created_at", None))
        joined_at = self._format_timestamp(getattr(inte.user, "joined_at", None))
        progress_bar = self._build_progress_bar(xp_value, xp_needed)

        embed = Embed(
            title=f"Status de {inte.user.display_name}",
            color=discord.Color.from_rgb(155, 89, 182),
        )
        embed.add_field(
            name="💰 Economia",
            value=f"**Carteira:** {data['nex']}\n**Banco:** {bank_balance}",
            inline=False,
        )
        embed.add_field(name="🛡️ Classe", value=class_name, inline=True)
        embed.add_field(name="🗺️ Local", value=zone_name, inline=True)
        embed.add_field(
            name="📈 Progresso",
            value=f"**Nível:** {level}\n**XP:** {xp_value}/{xp_needed}\n`{progress_bar}`\n",
            inline=False,
        )
        embed.add_field(name="❤️ HP", value=hp_text, inline=True)
        embed.add_field(name="⚡ Energia", value=energy_text, inline=True)
        embed.add_field(
            name="📊 Atributos",
            value=(
                f"💪 **Força:** {attack}\u2003\u2003\u2003\u2003🛡️ **Defesa:** {defense}\n"
                f"🔮 **Inteligência:** {magic}\u2003\u2003✨ **Res. mágica:** {magic_resistance}\n"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎒 Recursos",
            value=(
                f"🌲 **Madeira:** {data['wood']}\n"
                f"⛏️ **Ferro:** {data['iron']}\n"
                f"🧿 **Runas:** {data['runes']}"
            ),
            inline=True,
        )
        embed.add_field(
            name="🧪 Equipamentos",
            value=(
                f"**Arma:** {weapon_name}\n"
                f"**Armadura:** {armor_name}\n"
                "**Acessório:** --"
            ),
            inline=True,
        )
        embed.add_field(
            name="📅 Datas",
            value=(
                f"**Conta criada:** {created_at}\n"
                f"**Entrou no servidor:** {joined_at}"
            ),
            inline=False,
        )

        thumbnail_url = image_url or getattr(inte.user.display_avatar, "url", None)
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=f"Perfil de {inte.user.display_name}")
        return embed

    @commands.hybrid_command(
        name="escolher_classe",
        aliases=["choose_class"],
        description="Escolha a classe do seu herói no RPG.",
    )
    async def escolher_classe(self, ctx: commands.Context):
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        await create_hero(inte)
        
    @commands.hybrid_command(name="menu")
    async def menu(self, ctx):
        """Mostra o menu do perfil e do heroi."""
        inte = CommandContextAdapter(ctx)
        ensure_profile(inte.user.id)
        data = get_active_hero(inte.user.id)
        
        class Dropdown(Select):
            def __init__(self,stats_obj):
                
                self.stats_obj = stats_obj
                
                options = [
                    SelectOption(value=1, label="Perfil", emoji='🧪'),
                    SelectOption(value=2, label="Habilidades", emoji='🌀')
                ]
                
                    
                super().__init__(placeholder='Selecione uma pagina', min_values=1, max_values=1, options=options)
        
        
            async def callback(self, interaction):
                if interaction.user.id != inte.user.id:
                    return
                if self.values[0] == "1":
                    embed = self.stats_obj.load_stats(data, inte)
                elif self.values[0] == "2":
                    embed = self.stats_obj.load_ability_info(inte)
                message = await inte.original_response()
                await message.edit(embed=embed)
                await interaction.response.defer()
        
        
        view = View()
        view.add_item(Dropdown(self))

        if not has_selected_class(inte.user.id):
            async def escolher_classe_callback(interaction: discord.Interaction):
                if interaction.user.id != inte.user.id:
                    return
                await interaction.response.defer(ephemeral=True)
                await create_hero(inte)

            escolher_classe_button = Button(label="Escolher classe", style=discord.ButtonStyle.primary)
            escolher_classe_button.callback = escolher_classe_callback
            view.add_item(escolher_classe_button)
        
        embed = self.load_stats(data, inte)

        await inte.response.send_message(embed=embed, view=view)
        
        
        
    def load_stats(self, data, inte):
        if not has_selected_class(inte.user.id):
            return self.load_profile_without_class(data, inte)

        hero = load_hero(inte.user.id, name=inte.user.name)

        xp_needed = round(6.5 * (1.5 ** hero.level))
        max_hp = getattr(hero, "max_hp", hero.hp)
        max_mana = getattr(hero, "max_mana", hero.mana)
        return self._build_status_embed(
            inte,
            data=data,
            class_name=hero.classname,
            level=hero.level,
            xp_value=data["xp"],
            xp_needed=xp_needed,
            hp_text=f"{hero.hp}/{max_hp}",
            energy_text=f"{hero.mana}/{max_mana}",
            image_url=getattr(hero, "image", None),
            attack=hero.attack,
            defense=hero.defense,
            magic=hero.magic,
            magic_resistance=hero.magic_resistance,
            weapon_name=hero.weapon.name if hero.weapon else "--",
            armor_name=hero.armor.name if hero.armor else "--",
        )


    def load_profile_without_class(self, data, inte):
        embed = self._build_status_embed(
            inte,
            data=data,
            class_name="Não escolhida",
            level=data["level"],
            xp_value=data["xp"],
            xp_needed=10,
            hp_text="--",
            energy_text="--",
            image_url=None,
            attack="--",
            defense="--",
            magic="--",
            magic_resistance="--",
            weapon_name="--",
            armor_name="--",
        )
        embed.add_field(
            name="Próximo passo",
            value="Escolher uma classe é opcional. Quando quiser, use o comando de escolher classe para definir como seu herói vai lutar.",
            inline=False,
        )
        embed.set_footer(text="Seu perfil já foi criado. A classe fica a seu critério.")
        return embed
    
    
    def load_ability_info(self, inte):
        if not has_selected_class(inte.user.id):
            embed = Embed(title=f"Menu de {inte.user.name}", color=discord.Color.blue())
            embed.add_field(name="Habilidades 🌀", value="Você ainda não escolheu uma classe.", inline=False)
            embed.add_field(
                name="Dica",
                value="A classe é opcional. Escolha quando quiser para liberar as habilidades do herói.",
                inline=False,
            )
            return embed

        hero = load_hero(inte.user.id, name=inte.user.name)
        embed = abilities_embed(hero, inte)
        
        return embed
        
async def setup(bot):
    await bot.add_cog(Stats(bot))


