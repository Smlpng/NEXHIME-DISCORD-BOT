
# welcome.py
import discord

def initialize_welcome(bot, channel_name: str = "〔💬〕main-chat"):
    """
    Inicializa o listener de boas-vindas no mesmo padrão do status.py.
    Registra dinamicamente o handler 'on_member_join' no bot.
    """

    async def on_member_join(member: discord.Member):
        guild = member.guild
        canal = discord.utils.get(guild.text_channels, name=channel_name)

        mensagem = f":wave: | Olá {member.mention}, seja bem-vindo(a) ao servidor {guild.name}!\n Espero que goste daqui e possa fazer daqui a sua segunda casa!\n\nAqui nós temos chats de voice para você se divertir e fazer novas amizades\n\nE o que torna aqui um lugar especial é eu hehe eu tenho varios comandos de economia e rpg também!"

        # Tenta enviar no canal configurado
        if canal and canal.permissions_for(guild.me).send_messages:
            await canal.send(mensagem)
        else:
            # Fallback: tenta enviar por DM caso não tenha canal ou permissão
            try:
                await member.send(mensagem)
            except discord.Forbidden:
                # Sem permissão para DM — silenciosamente ignora
                pass

    # Registra o listener no bot (igual ao add_listener usado em módulos utilitários)
    bot.add_listener(on_member_join, "on_member_join")


# welcome.py
import discord
from typing import Optional, Union

async def initialize_welcome(
    bot,
    channel: Optional[Union[int, str]] = "geral",
    dm_fallback: bool = True,
):
    """
    Registra um listener assíncrono para 'on_member_join' no bot.
    Pode buscar o canal por nome (str) ou por ID (int).
    
    Parâmetros:
      - bot: instância do commands.Bot ou discord.Client
      - channel: nome do canal (str) ou ID do canal (int). Padrão "geral".
      - dm_fallback: se True, envia DM caso não ache canal ou não tenha permissão.
    """

    async def _resolve_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
        # Por ID do canal (mais seguro)
        if isinstance(channel, int):
            ch = guild.get_channel(channel)
            if isinstance(ch, discord.TextChannel):
                return ch
            return None

        # Por nome do canal
        if isinstance(channel, str) and channel:
            ch = discord.utils.get(guild.text_channels, name=channel)
            if isinstance(ch, discord.TextChannel):
                return ch
        return None

    async def on_member_join(member: discord.Member):
        guild = member.guild
        canal = await _resolve_channel(guild)

        mensagem = (
            f":wave: | Olá {member.mention}, seja bem-vindo(a) ao servidor {guild.name}!\n" 
             "Espero que goste daqui e possa fazer daqui a sua segunda casa!\n\n"
             "Aqui nós temos chats de voice para você se divertir e fazer novas amizades\n\n"
             "E o que torna aqui um lugar especial é eu hehe eu tenho varios comandos de economia e rpg também!"

        )

        # Tenta enviar no canal configurado
        if canal and canal.permissions_for(guild.me).send_messages:
            try:
                await canal.send(mensagem)
                return
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

        # Fallback para DM (opcional)
        if dm_fallback:
            try:
                await member.send(mensagem)
            except discord.Forbidden:
                # Usuário bloqueou DMs / config do servidor
                pass
            except discord.HTTPException:
                pass

    # Registra o listener (não precisa ser await)
    bot.add_listener(on_member_join, "on_member_join")
