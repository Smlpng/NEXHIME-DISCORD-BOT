# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from datetime import datetime

class Roadmap(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="roadmap", help="Envia um embed com as atualizações do roadmap.")
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
            name="✅ ~~ Fase 1.1 (Moderação extra) ~~ `v0.1.1`| **Concluído**",
            value="• Novos comandos de moderação adicionados:\n"
                  "• `[n!]` **slowmode**\n"
                  "• `[n!]` **limpar_usuario**\n"
                  "• `[n!]` **nickname**\n"
                  "• `[n!]` **reset_nick**\n"
                  "• `[n!]` **modlog**\n"
                  "• `[n!]` **antilink**\n"
                  "• `[n!]` **lockdown**\n",
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
            name="✅ ~~ Fase 2.1 (Entretenimento extra) ~~ `v0.2.1`| **Concluído**",
            value="• Novos comandos de entretenimento adicionados:\n"
                  "• `[n!]` **cara_ou_coroa**\n"
                  "• `[n!]` **rps**\n"
                  "• `[n!]` **trivia**\n"
                  "• `[n!]` **rate**\n"
                  "• `[n!]` **meme_lista**\n",
            inline=False
        )

        embed.add_field(
            name="✅ ~~ Utilitários (Geral) ~~ `v0.2.2`| **Concluído**",
            value="• Novos comandos gerais adicionados:\n"
                  "• `[n!]` **uptime**\n"
                  "• `[n!]` **botinfo**\n"
                  "• `[n!]` **enquete**\n"
                  "• `[n!]` **afk**\n"
                  "• `[n!]` **timer**\n",
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
            value="• Alguns comandos principais do RPG:\n"
            "• `[n!]` **menu**\n"
            "• `[n!]` **escolher_classe**\n"
            "• `[n!]` **escolher_raca**\n"
            "• `[n!]` **quests**\n"
            "• `[n!]` **fight**\n"
            "• `[n!]` **zone**\n"
            "• `[n!]` **change_zone**\n"
            "• `[n!]` **inventory**\n"
            "• `[n!]` **loja**\n",
            inline=False
        )

        embed.add_field(
            name="🎯 Fase 4.1 (RPG extra) `v0.4.1`| **Em Andamento**",
            value="• Novos comandos do RPG adicionados:\n"
                  "• `[n!]` **explorar**\n"
                  "• `[n!]` **boss**\n"
                  "• `[n!]` **reset_classe**\n",
            inline=False
        )

        

        data_atual = datetime.now().strftime("%d de %B de %Y")
        embed.set_footer(text=f"Para saber dos demais comandos, use [n!] help | Última atualização: {data_atual}")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Roadmap(bot))