import discord
from discord.ext import commands

class ModeracaoSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="setup_servidor", 
        aliases=["setupservidor", "gerarservidor"],
        help="Cria a estrutura de canais e categorias do RPG Primordial."
    )
    @commands.has_permissions(administrator=True)
    async def setup_servidor(self, ctx: commands.Context):
        guild = ctx.guild
        
        await ctx.send("🐒 *Iniciando o ritual de criação do mundo primata... Aguarde!*")

        try:
            # 1. CATEGORIA: ÁREA GERAL
            cat_geral = await guild.create_category("🌴 │ ÁREA GERAL")
            await cat_geral.create_text_channel("📜│regras-da-selva")
            await cat_geral.create_text_channel("💬│chat-dos-macacos")
            await cat_geral.create_voice_channel("🔊│Clube da Banana (Geral)")

            # 2. CATEGORIA: SISTEMA DE RPG
            cat_rpg = await guild.create_category("🎮 │ RPG PRIMORDIAL")
            await cat_rpg.create_text_channel("🤖│comandos-do-bot")
            await cat_rpg.create_text_channel("💼│escolha-de-trabalho")
            await cat_rpg.create_voice_channel("⛺│acampamento-de-aventuras")

            # 3. ESTRUTURA DAS TRIBOS
            tribos = [
                {
                    "categoria": "🍃 │ Tribo da Folhagem",
                    "chat": "🍃│clareira-da-folhagem",
                    "voz": "🍃│Copa das Árvores"
                },
                {
                    "categoria": "🌋 │ Tribo do Coração Vulcânico",
                    "chat": "🌋│forja-vulcanica",
                    "voz": "🌋│Cratera Ardente"
                },
                {
                    "categoria": "✨ │ Tribo do Vazio Estelar",
                    "chat": "✨│observatorio-estelar",
                    "voz": "✨│Cosmos Primordial"
                },
                {
                    "categoria": "🦴 │ Tribo do Eco Primordial",
                    "chat": "🦴│caverna-dos-ancestrais",
                    "voz": "🦴│Santuário dos Ecos"
                }
            ]

            for tribo in tribos:
                cat_tribo = await guild.create_category(tribo["categoria"])
                await cat_tribo.create_text_channel(tribo["chat"])
                await cat_tribo.create_voice_channel(tribo["voz"])

            await ctx.send("✅ **Servidor configurado com sucesso! A Era Primata começou!** 🍌")

        except Exception as e:
            print(f"Erro ao criar canais: {e}")
            await ctx.send(
                "🚨 Ocorreu um erro ao criar a estrutura. Verifique se o bot possui a permissão **Gerenciar Canais**!"
            )

    # Tratamento de erro caso alguém sem permissão execute
    @setup_servidor.error
    async def setup_servidor_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Apenas administradores do servidor podem executar este comando!")

async def setup(bot: commands.Bot):
    await bot.add_cog(ModeracaoSetup(bot))