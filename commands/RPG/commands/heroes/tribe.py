import unicodedata
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from commands.RPG.utils.command_adapter import CommandContextAdapter
from commands.RPG.utils.database import ensure_profile, get_active_hero, set_active_hero_tribe


TRIBES = [
    "Tribo da Folhagem",
    "Tribo do Coracao Vulcanico",
    "Tribo do Vazio Estelar",
    "Tribo do Eco Primordial",
]

TRIBE_ROLE_IDS = {
    "Tribo da Folhagem": 1454489963151229080,
    "Tribo do Coracao Vulcanico": 1454489966070595877,
    "Tribo do Vazio Estelar": 1454489964325769413,
    "Tribo do Eco Primordial": 1454489970336071852,
}

TRIBE_ROLE_CHANNEL_IDS = {
    1456859390706716867,
}


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


class TribeSelect(discord.ui.Select):
    def __init__(self, placeholder: str):
        options = [discord.SelectOption(label=tribe, value=tribe) for tribe in TRIBES]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_value = self.values[0]
        await interaction.response.defer()
        self.view.stop()


class TribeView(discord.ui.View):
    def __init__(self, placeholder: str):
        super().__init__(timeout=60)
        self.selected_value: Optional[str] = None
        self.add_item(TribeSelect(placeholder))


class Tribe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_role_sync_channel(self, channel: discord.abc.GuildChannel | discord.Thread | None) -> bool:
        if channel is None:
            return False
        channel_id = getattr(channel, "id", None)
        if channel_id in TRIBE_ROLE_CHANNEL_IDS:
            return True
        parent = getattr(channel, "parent", None)
        return getattr(parent, "id", None) in TRIBE_ROLE_CHANNEL_IDS

    def _is_tribe_command_channel(self, channel: discord.abc.GuildChannel | discord.Thread | None) -> bool:
        return self._is_role_sync_channel(channel)

    async def _reject_wrong_channel(self, inte: CommandContextAdapter) -> bool:
        channel = inte.channel
        if self._is_tribe_command_channel(channel):
            return False

        allowed = ", ".join(f"<#{channel_id}>" for channel_id in sorted(TRIBE_ROLE_CHANNEL_IDS))
        message = f"Este comando so pode ser usado no canal configurado para tribos: {allowed}."
        await inte.response.send_message(message, ephemeral=True)
        return True

    def _get_role_for_tribe(self, guild: discord.Guild, tribe_name: str) -> discord.Role | None:
        role_id = TRIBE_ROLE_IDS.get(tribe_name)
        if role_id is None:
            return None
        return guild.get_role(role_id)

    async def _sync_tribe_role(
        self,
        ctx: commands.Context,
        selected_tribe: str,
        previous_tribe: str | None = None,
    ) -> str | None:
        if not self._is_role_sync_channel(ctx.channel):
            return None

        guild = ctx.guild
        if guild is None:
            return "A tribo foi salva, mas cargos so podem ser gerenciados dentro de um servidor."

        member = guild.get_member(ctx.author.id)
        if member is None:
            return "A tribo foi salva, mas nao consegui localizar seu membro no servidor para ajustar o cargo."

        desired_role = self._get_role_for_tribe(guild, selected_tribe)
        if desired_role is None:
            return f"A tribo foi salva, mas o cargo de **{selected_tribe}** nao esta configurado no servidor."

        me = guild.me
        if me is None or me.top_role <= desired_role:
            return f"A tribo foi salva, mas nao consigo entregar o cargo **{desired_role.name}** por causa da hierarquia."

        roles_to_remove = []
        for tribe_name, role_id in TRIBE_ROLE_IDS.items():
            if tribe_name == selected_tribe:
                continue
            if previous_tribe is not None and tribe_name != previous_tribe and guild.get_role(role_id) not in member.roles:
                continue
            role = guild.get_role(role_id)
            if role is not None and role in member.roles and me.top_role > role:
                roles_to_remove.append(role)

        try:
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason=f"Troca de tribo por {ctx.author}")
            if desired_role not in member.roles:
                await member.add_roles(desired_role, reason=f"Escolha de tribo por {ctx.author}")
        except discord.Forbidden:
            return f"A tribo foi salva, mas faltou permissao para ajustar o cargo **{desired_role.name}**."
        except discord.HTTPException:
            return "A tribo foi salva, mas ocorreu um erro ao atualizar seus cargos no Discord."

        return f"Parabéns! Você entrou para **{desired_role.name}**, agora vá, explore, conquiste e honre sua tribo!"

    async def _autocomplete(self, current: str):
        value = (current or "").strip().lower()
        options = [tribe for tribe in TRIBES if value in tribe.lower()] or TRIBES
        return [app_commands.Choice(name=tribe, value=tribe) for tribe in options[:20]]

    async def _resolve_tribe(self, value: str | None) -> str | None:
        if value is None:
            return None
        lowered = _normalize(value)
        return next((tribe for tribe in TRIBES if _normalize(tribe) == lowered), None)

    @commands.hybrid_command(name="escolher_tribo")
    @app_commands.describe(tribo="Nome da tribo ou deixe em branco para abrir o seletor")
    async def escolher_tribo(self, ctx, *, tribo: Optional[str] = None):
        """Define a tribo do herói atual."""
        inte = CommandContextAdapter(ctx)

        if await self._reject_wrong_channel(inte):
            return

        ensure_profile(inte.user.id)
        hero = get_active_hero(inte.user.id)

        if hero is None:
            return await inte.response.send_message("Seu perfil ainda nao esta pronto para escolher uma tribo.")

        if hero.get("tribe"):
            return await inte.response.send_message(f"Seu heroi ja pertence a {hero['tribe']}.", ephemeral=True)

        if tribo is None and inte.interaction is not None:
            view = TribeView("Selecione sua tribo")
            await inte.response.send_message("Escolha a tribo do seu herói:", view=view, ephemeral=True)
            await view.wait()
            if view.selected_value is None:
                return await inte.followup.send("Tempo esgotado. Tente novamente quando quiser.", ephemeral=True)
            tribo = view.selected_value

        selected_tribe = await self._resolve_tribe(tribo)
        if selected_tribe is None:
            options = ", ".join(TRIBES)
            return await inte.response.send_message(f"Informe uma tribo valida. Opcoes: {options}", ephemeral=True)

        set_active_hero_tribe(inte.user.id, selected_tribe)
        role_message = await self._sync_tribe_role(ctx, selected_tribe)
        response = f"Tribo definida com sucesso: {selected_tribe}."
        if role_message:
            response = f"{response}\n\n{role_message}"
        await inte.response.send_message(response, ephemeral=True)

    @commands.hybrid_command(name="trocar_tribo")
    @app_commands.describe(nova_tribo="Nome da nova tribo ou deixe em branco para abrir o seletor")
    async def trocar_tribo(self, ctx, *, nova_tribo: Optional[str] = None):
        """Troca a tribo do herói atual dentro do sistema novo."""
        inte = CommandContextAdapter(ctx)

        if await self._reject_wrong_channel(inte):
            return

        ensure_profile(inte.user.id)
        hero = get_active_hero(inte.user.id)

        if hero is None:
            return await inte.response.send_message("Seu perfil ainda nao esta pronto para trocar de tribo.")

        if not hero.get("tribe"):
            return await inte.response.send_message("Seu heroi ainda nao escolheu uma tribo. Use escolher_tribo primeiro.", ephemeral=True)

        if nova_tribo is None and inte.interaction is not None:
            view = TribeView("Selecione a nova tribo")
            await inte.response.send_message("Escolha a nova tribo do seu herói:", view=view, ephemeral=True)
            await view.wait()
            if view.selected_value is None:
                return await inte.followup.send("Tempo esgotado. Tente novamente quando quiser.", ephemeral=True)
            nova_tribo = view.selected_value

        selected_tribe = await self._resolve_tribe(nova_tribo)
        if selected_tribe is None:
            return await inte.response.send_message("Tribo invalida. Use uma das opcoes do seletor.", ephemeral=True)
        if selected_tribe == hero.get("tribe"):
            return await inte.response.send_message("Seu heroi ja esta nessa tribo.", ephemeral=True)

        old_tribe = hero.get("tribe")
        set_active_hero_tribe(inte.user.id, selected_tribe)
        role_message = await self._sync_tribe_role(ctx, selected_tribe, previous_tribe=old_tribe)

        embed = discord.Embed(title="Troca de tribo", color=discord.Color.blue())
        embed.add_field(name="Anterior", value=old_tribe, inline=True)
        embed.add_field(name="Nova", value=selected_tribe, inline=True)
        if role_message:
            embed.add_field(name="Cargo", value=role_message, inline=False)
        embed.set_footer(text="No canal configurado, a troca de tribo tambem sincroniza o cargo do Discord.")
        await inte.response.send_message(embed=embed, ephemeral=True)

    @escolher_tribo.autocomplete("tribo")
    async def escolher_tribo_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self._autocomplete(current)

    @trocar_tribo.autocomplete("nova_tribo")
    async def trocar_tribo_autocomplete(self, interaction: discord.Interaction, current: str):
        return await self._autocomplete(current)


async def setup(bot):
    await bot.add_cog(Tribe(bot))