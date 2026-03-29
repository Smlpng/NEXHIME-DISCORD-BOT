# status.py
import asyncio
import discord

async def initialize_status(bot):
    async def cycle():
        await bot.wait_until_ready()
        default_prefix = getattr(bot, "default_prefix", "n!")
        i = 0
        while not bot.is_closed():
            prefix_count = len({command.qualified_name for command in bot.walk_commands()})
            slash_count = len({command.qualified_name for command in bot.tree.walk_commands()})
            msgs = [
                "Desenvolvido por Sael[sael.py] 🧑‍💻",
                f"Ping atual: {round(bot.latency * 1000)} ms 📶",
                f"Cuidando de {sum(g.member_count or 0 for g in bot.guilds)} membros 👥",
                f"Online em {len(bot.guilds)} selvas diferentes 🌍",
                f"Use /help ou {default_prefix}help ⚙️",
                f"Tenho {prefix_count} comandos prefixados e {slash_count} slash commands 📚",
                f"Veja seu herói com {default_prefix}menu 📋",
                f"Entre em combate com {default_prefix}fight ⚔️",
                f"Explore zonas com {default_prefix}zone e {default_prefix}change_zone 🗺️",
                f"Gerencie o servidor com {default_prefix}warn, {default_prefix}mute e {default_prefix}lock 🛡️",
                f"Use {default_prefix}prefix para ajustar o prefixo do servidor 🔧",
                f"Crie imagens com {default_prefix}tweet e divirta-se com {default_prefix}tomatadas_rank 🎨",
            ]
            name = msgs[i % len(msgs)]
            await bot.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(type=discord.ActivityType.watching, name=name),
            )
            i += 1
            await asyncio.sleep(20)
    asyncio.create_task(cycle())
