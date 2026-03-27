# # mov_chat.py

# import asyncio
# import discord
# import json
# import random
# from datetime import datetime, timezone, timedelta

# async def initialize_mov_chat(
#     bot,
#     interval_minutes: int = 60,
#     channel_name: str = "geral",
#     channel_id: int | None = None
# ):
#     """
#     Agenda envio periódico de mensagens motivacionais no canal.
#     - Se 'channel_id' for informado, é priorizado.
#     - Caso contrário, usa 'channel_name' em cada guild.
#     """
#     async def cycle():
#         await bot.wait_until_ready()
#         msgs = [
#             "<@&1445084967972638865> | Lembre-se de conferir suas quests: n!quests 📜",
#             "<@&1445084967972638865> | Explore novos locais com n!explorar 🧭",
#             "<@&1445084967972638865> | Use n!loja para ver itens disponíveis 🛒",
#             "<@&1445084967972638865> | Você já trabalhou hoje? n!trabalhar 🛠️",
#             "<@&1445084967972638865> | Veja seu menu com n!menu 📋",
#             "<@&1445084967972638865> | Convide amigos para se juntar à aventura! 🎉",
#         ]
#         # Config path assumed at workspace root alongside this file
#         config_path = "config.json"

#         def load_last_sent():
#             try:
#                 with open(config_path, "r", encoding="utf-8") as f:
#                     data = json.load(f)
#                 ts_str = data.get("motivational_last_sent")
#                 if not ts_str:
#                     return None
#                 return datetime.fromisoformat(ts_str)
#             except Exception:
#                 return None

#         def save_last_sent(dt: datetime):
#             try:
#                 # Merge with existing config and update field
#                 data = {}
#                 try:
#                     with open(config_path, "r", encoding="utf-8") as f:
#                         data = json.load(f)
#                 except Exception:
#                     data = {}
#                 data["motivational_last_sent"] = dt.replace(tzinfo=timezone.utc).isoformat()
#                 with open(config_path, "w", encoding="utf-8") as f:
#                     json.dump(data, f, ensure_ascii=False, indent=2)
#             except Exception:
#                 # Non-fatal: if we cannot write, just skip persisting
#                 pass

#         last_sent = load_last_sent()
#         while not bot.is_closed():
#             try:
#                 now = datetime.now(timezone.utc)
#                 # Only send if full interval has elapsed
#                 send_allowed = False
#                 if last_sent is None:
#                     send_allowed = True
#                 else:
#                     elapsed = now - last_sent
#                     if elapsed >= timedelta(minutes=max(1, int(interval_minutes))):
#                         send_allowed = True

#                 if send_allowed:
#                     message_to_send = random.choice(msgs)
#                     formatted_message = "\n".join(f"# {line}" for line in message_to_send.splitlines())
#                     ch = None
#                     # Resolve um único canal alvo
#                     if channel_id:
#                         # Primeiro tenta resolver globalmente pelo bot
#                         ch = bot.get_channel(channel_id)
#                         # Se não encontrou, tenta em cada guild até achar
#                         if ch is None:
#                             for guild in bot.guilds:
#                                 ch = guild.get_channel(channel_id)
#                                 if ch:
#                                     break
#                     else:
#                         # Sem ID: procura por nome e para no primeiro encontrado
#                         for guild in bot.guilds:
#                             ch = discord.utils.get(guild.text_channels, name=channel_name)
#                             if ch:
#                                 break

#                     if ch:
#                         await ch.send(formatted_message)
#                         last_sent = now
#                         save_last_sent(last_sent)
#             except Exception:
#                 # Evita quebrar o loop em caso de erro pontual
#                 pass
#             # Sleep tick can be smaller (e.g., 60s) to check gate
#             # but sending is gated by full interval
#             await asyncio.sleep(60)

#     asyncio.create_task(cycle())