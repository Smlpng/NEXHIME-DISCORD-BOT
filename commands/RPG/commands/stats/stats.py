import discord
from discord import Embed, SelectOption
from discord.ext import commands
from discord.ui import Button, Select, View
from commands.RPG.utils.database import ensure_profile, get_active_hero, get_bank_balance, has_selected_class
from commands.RPG.utils.hero_actions import load_hero
from commands.RPG.game.characters.ability_info import abilities_embed
from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.create import create_hero

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        race = data.get("race") or "Não escolhida"
        tribe = data.get("tribe") or "Não escolhida"
        if not has_selected_class(inte.user.id):
            return self.load_profile_without_class(data, inte)

        hero = load_hero(inte.user.id, name=inte.user.name)

        xp_needed = round(6.5 * (1.5 ** hero.level))
        progress = data["xp"] / xp_needed if xp_needed else 0
        progress = min(max(progress, 0), 1)
        filled_length = int(20 * progress)
        bar = "█" * filled_length + "-" * (20 - filled_length)
        bar = f"[{bar}] {data['xp']}/{xp_needed} XP"

        bank_balance = get_bank_balance(inte.user.id)
        embed = Embed(title=f"Menu de {inte.user.name}", color=discord.Color.blue())
        embed.add_field(name="💰 Economia", value=f"**Carteira:** {data['gold']}\n**Banco:** {bank_balance}", inline=False)
        embed.add_field(name="🎭 Classe", value=hero.classname, inline=True)
        embed.add_field(name="🧬 Raça", value=race, inline=True)
        embed.add_field(name="🏕️ Tribo", value=tribe, inline=True)
        embed.add_field(name="📈 Nível", value=hero.level, inline=True)
        embed.add_field(name="🧪 XP", value=bar, inline=False)
        embed.add_field(name="🌲 Madeira", value=data["wood"], inline=True)
        embed.add_field(name="⛏️ Ferro", value=data["iron"], inline=True)
        embed.add_field(name="🧿 Runas", value=data["runes"], inline=True)
        embed.add_field(name="❤️ Vida", value=hero.hp, inline=True)
        embed.add_field(name="🔵 Mana", value=hero.mana, inline=True)
        embed.add_field(name="⚔️ Ataque", value=hero.attack, inline=True)
        embed.add_field(name="🔮 Magia", value=hero.magic, inline=True)
        embed.add_field(name="🛡️ Defesa", value=hero.defense, inline=True)
        embed.add_field(name="✨ Resistência mágica", value=hero.magic_resistance, inline=True)
        embed.add_field(name="🗡️ Arma", value=hero.weapon.name if hero.weapon else "Nenhuma", inline=True)
        embed.add_field(name="🛡️ Armadura", value=hero.armor.name if hero.armor else "Nenhuma", inline=True)

        embed.set_image(url=hero.image)
        embed.set_footer(text="Perfil do personagem")

        return embed


    def load_profile_without_class(self, data, inte):
        bank_balance = get_bank_balance(inte.user.id)
        race = data.get("race") or "Não escolhida"
        tribe = data.get("tribe") or "Não escolhida"
        embed = Embed(title=f"Menu de {inte.user.name}", color=discord.Color.blue())
        embed.add_field(name="Classe 🏹", value="Não escolhida", inline=True)
        embed.add_field(name="Raça 🧬", value=race, inline=True)
        embed.add_field(name="Tribo 🏕️", value=tribe, inline=True)
        embed.add_field(name="Nível 📈", value=data["level"], inline=True)
        embed.add_field(name="XP 🧪", value=f'{data["xp"]}/10', inline=False)
        embed.add_field(name="Ouro na carteira 💰", value=data["gold"], inline=True)
        embed.add_field(name="Ouro no banco 🏦", value=bank_balance, inline=True)
        embed.add_field(name="Madeira 🌲", value=data["wood"], inline=True)
        embed.add_field(name="Ferro ⛏️", value=data["iron"], inline=True)
        embed.add_field(name="Runas 🧿", value=data["runes"], inline=True)
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


