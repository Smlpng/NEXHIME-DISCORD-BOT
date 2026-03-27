# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from datetime import datetime

class Roadmap(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="roadmap", help="Envia um embed com as atualizações do roadmap.")
    async def roadmap(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📌 Atualizações do Roadmap",
            description="Aqui estão as fases e status atuais do projeto NEXHIME:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="✅ ~~ Fase 1 (Moderação) ~~ `v0.1`| **Concluído**",
            value="• Comandos Básicos e Avançados, exemplos:\n"
                  "• `[n!]` ** add_sticker**\n"
                  "• `[n!]` **addrole**\n"
                  "• `[n!]` **kick**\n"
                  "• `[n!]` **set_prefix**\n"
                  "• `[n!]` **embed**\n",
            inline=False
        )

        embed.add_field(
            name="✅ ~~ Fase 2 (Entretenimento inicial) ~~ `v0.2`| **Concluído**",
            value="• Comandos Básicos e Avançados, exemplos:\n"
            "• `[n!]` **ascii** \n"
            "• `[n!]` **say** \n"
            "• `[n!]` **quote** \n"
            "• `[n!]` **showquote** ",
            inline=False
        )

        embed.add_field(
            name="✅ ~~ Fase 3 (Economia) ~~ `v0.3`| **Concluído**",
            value="• Comandos Básicos, exemplos:\n"
            "• `[n!]` **daily**\n"
            "• `[n!]` **banco**\n"
            "• `[n!]` **depositar**\n"
            "• `[n!]` **sacar**\n"
            "• `[n!]` **trabalhar**\n"
            "• `[n!]` **rank**\n"
            "• `[n!]` **glubglub**",
            inline=False
        )

        embed.add_field(
            name="🎯 Fase 4 (RPG) `v0.4`| **Em Andamento**",
            value="• Comandos Básicos, exemplos:\n"
            "• `[n!]` **menu**\n"
            "• `[n!]` **escolher_raça**\n"
            "• `[n!]` **escolher_tribo**\n"
            "• `[n!]` **mapa**\n"
            "• `[n!]` **quests**\n"
            "• `[n!]` **trocar_tribo**\n",
            inline=False
        )


        data_atual = datetime.now().strftime("%d de %B de %Y")
        embed.set_footer(text=f"Para saber dos demais comandos, use [n!] help | Última atualização: {data_atual}")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Roadmap(bot))