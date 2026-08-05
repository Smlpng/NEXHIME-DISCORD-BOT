import discord
from discord.ext import commands

class SetupCargos(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="setup_cargos",
        aliases=["setupe cargo", "gerarcargos"],
        help="Cria automaticamente os cargos tematizados do RPG Primordial com cores personalizadas."
    )
    @commands.has_permissions(administrator=True)
    async def setup_cargos(self, ctx: commands.Context):
        guild = ctx.guild
        
        await ctx.send("🎨 *Iniciando a criação dos cargos da selva... Aguarde!*")

        # Lista de cargos estruturada: (Nome, Cor Hexadecimal, Exibir separadamente dos outros membros)
        cargos_para_criar = [
            # 👑 1. ADMINISTRAÇÃO E LÍDERES (MODERAÇÃO)
            {"nome": "👑 Ancestral Supremo", "cor": 0xFFD700, "hoist": True, "mentionable": True},     # Dourado
            {"nome": "⚙️ Xamã do Bot", "cor": 0x9B59B6, "hoist": True, "mentionable": False},          # Roxo
            {"nome": "🍃 Líder da Folhagem", "cor": 0x2ECC71, "hoist": True, "mentionable": True},     # Verde
            {"nome": "🌋 Líder Vulcânico", "cor": 0xE74C3C, "hoist": True, "mentionable": True},       # Vermelho
            {"nome": "✨ Líder do Vazio", "cor": 0x3498DB, "hoist": True, "mentionable": True},          # Azul Místico
            {"nome": "🦴 Líder do Eco", "cor": 0x95A5A6, "hoist": True, "mentionable": True},            # Cinza Osso
            {"nome": "🛡️ Guardião do Bando", "cor": 0x1ABC9C, "hoist": True, "mentionable": True},     # Turquesa

            # 🌟 2. STATUS ESPECIAL
            {"nome": "🏆 Rei dos Primatas", "cor": 0xF1C40F, "hoist": True, "mentionable": True},      # Amarelo Ouro

            # 🛡️ 3. TRIBOS (MEMBROS)
            {"nome": "🍃 Membro da Folhagem", "cor": 0x27AE60, "hoist": True, "mentionable": False},  # Verde Escuro
            {"nome": "🌋 Membro do Coração Vulcânico", "cor": 0xC0392B, "hoist": True, "mentionable": False}, # Vermelho Escuro
            {"nome": "✨ Membro do Vazio Estelar", "cor": 0x2980B9, "hoist": True, "mentionable": False}, # Azul Escuro
            {"nome": "🦴 Membro do Eco Primordial", "cor": 0x7F8C8D, "hoist": True, "mentionable": False}, # Cinza

            # 🐒 4. ESPÉCIES (RAÇAS)
            {"nome": "🦍 Gorila", "cor": 0x34495E, "hoist": False, "mentionable": False},
            {"nome": "🐒 Chimpanzé", "cor": 0xD35400, "hoist": False, "mentionable": False},
            {"nome": "🦧 Orangotango", "cor": 0xE67E22, "hoist": False, "mentionable": False},
            {"nome": "🐒 Lêmure / Mico", "cor": 0xF39C12, "hoist": False, "mentionable": False},

            # 💼 5. TRABALHOS & PROFISSÕES
            {"nome": "🍌 Coletor de Bananas", "cor": 0xF4D03F, "hoist": False, "mentionable": False},
            {"nome": "⚔️ Caçador de Feras", "cor": 0x8E44AD, "hoist": False, "mentionable": False},
            {"nome": "⚒️ Ferreiro de Pedra", "cor": 0x7E5109, "hoist": False, "mentionable": False},
            {"nome": "🧪 Alquimista de Frutas", "cor": 0x16A085, "hoist": False, "mentionable": False},
            {"nome": "🗺️ Explorador da Copa", "cor": 0x1F618D, "hoist": False, "mentionable": False}
        ]

        cargos_criados = 0
        cargos_existentes = 0

        try:
            for item in cargos_para_criar:
                # Verifica se o cargo já existe no servidor para não duplicar
                cargo_existente = discord.utils.get(guild.roles, name=item["nome"])
                
                if cargo_existente is None:
                    await guild.create_role(
                        name=item["nome"],
                        color=discord.Color(item["cor"]),
                        hoist=item["hoist"],
                        mentionable=item["mentionable"],
                        reason="Criação automática do setup do RPG Primordial"
                    )
                    cargos_criados += 1
                else:
                    cargos_existentes += 1

            msg = f"✅ **Operação concluída!**\n"
            msg += f"🔹 {cargos_criados} cargos criados com sucesso.\n"
            if cargos_existentes > 0:
                msg += f"⚠️ {cargos_existentes} cargos já existiam e foram mantidos sem duplicação."

            await ctx.send(msg)

        except Exception as e:
            print(f"Erro ao criar cargos: {e}")
            await ctx.send(
                "🚨 Ocorreu um erro ao criar os cargos! Verifique se o bot tem a permissão **Gerenciar Cargos** e se o cargo do bot está no topo da lista de cargos do servidor."
            )

    @setup_cargos.error
    async def setup_cargos_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Apenas administradores podem executar este comando!")

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCargos(bot))