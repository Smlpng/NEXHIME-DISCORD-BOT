import discord
from discord.ext import commands
from discord import app_commands

# =========================
# CONFIGURAÇÃO
# =========================
# Cargos que os usuários PODEM receber por este comando (use IDs dos cargos)
ALLOWED_ROLE_IDS = [
    1454489947686830206,  # @⌈🦍⌋ Macaco Primordial 
    #234567890123456789,  # Ex.: Música
    #345678901234567890,  # Ex.: Anúncios
]

# (Opcional) Limite máximo de membros por cargo. Deixe {} para ignorar a capacidade.
# Ex.: { role_id: max_membros }
ROLE_CAPS = {
    1454489947686830206: 100,
    # 234567890123456789: 50,
    # 345678901234567890: 25,
}


class ReceberTag(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- Utilitário para enviar resposta (ephemeral no slash; normal no prefixo) ----------
    async def _smart_send(self, ctx: commands.Context, content: str, ephemeral: bool = False):
        interaction = getattr(ctx, "interaction", None)
        if interaction:
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(content, ephemeral=ephemeral)
                else:
                    await interaction.response.send_message(content, ephemeral=ephemeral)
            except discord.InteractionResponded:
                await interaction.followup.send(content, ephemeral=ephemeral)
        else:
            await ctx.send(content)

    # ------------------- Helpers -------------------
    def _get_allowed_roles(self, guild: discord.Guild):
        roles = []
        for rid in ALLOWED_ROLE_IDS:
            r = guild.get_role(rid)
            if r:
                roles.append(r)
        return roles

    @staticmethod
    def _count_role_members(role: discord.Role) -> int:
        """
        Conta membros no cargo (requer Server Members Intent ligado no portal e intents.members=True no código).
        """
        return len(role.members)

    # ------------------- Comando Híbrido -------------------
    @commands.hybrid_command(
        name="receber_tag",
        description="Receba uma ou mais tags permitidas. Se já tiver, o bot avisa; se não, o bot adiciona."
    )
    @app_commands.describe(
        tags="Mencione cargos (no prefixo) ou digite nomes separados por vírgula (no slash use o autocomplete)."
    )
    async def receber_tag(self, ctx: commands.Context, *, tags: str | None = None):
        """
        Uso:
        - Prefixo: !receber_tag @Gamer @Música
                   !receber_tag gamer, música
        - Slash:   /receber_tag   (use autocomplete; pode digitar 'Gamer, Música')
        Regras:
        - Só cargos listados em ALLOWED_ROLE_IDS.
        - Se ROLE_CAPS tiver limite para o cargo, respeita a capacidade.
        - Se o usuário já tiver o cargo, apenas informa que já possui.
        """
        if ctx.guild is None or not isinstance(ctx.author, discord.Member):
            return await self._smart_send(ctx, "❌ Este comando só pode ser usado dentro de um servidor.", ephemeral=True)

        guild: discord.Guild = ctx.guild
        member: discord.Member = ctx.author

        allowed_roles = self._get_allowed_roles(guild)
        if not allowed_roles:
            return await self._smart_send(ctx, "⚠️ Nenhum cargo permitido foi configurado.", ephemeral=True)

        allowed_ids = {r.id for r in allowed_roles}
        name_map = {r.name.lower(): r for r in allowed_roles}

        # 1) Roles mencionadas na mensagem (prefixo)
        mentioned_roles = list(getattr(ctx.message, "role_mentions", []))

        roles_requested = []

        # Menções válidas
        for r in mentioned_roles:
            if r.id in allowed_ids and r not in roles_requested:
                roles_requested.append(r)

        # 2) Nomes via texto (ex.: "gamer, música")
        if tags:
            parts = [p.strip().lower() for p in tags.split(",") if p.strip()]
            for p in parts:
                r = name_map.get(p)
                if r and r not in roles_requested:
                    roles_requested.append(r)

        if not roles_requested:
            lista = "\n".join(
                f"- {r.mention} (`{r.name}`)"
                + (f" — limite: {ROLE_CAPS.get(r.id)}" if r.id in ROLE_CAPS else "")
                for r in allowed_roles
            )
            return await self._smart_send(
                ctx,
                "ℹ️ Informe pelo menos um cargo permitido.\nCargos disponíveis:\n" + lista,
                ephemeral=True
            )

        # 3) Para cada cargo: se já possui → avisa; senão tenta dar (respeitando capacidade e hierarquia)
        me = guild.me
        responses = []

        for role in roles_requested:
            # Já possui?
            if role in member.roles:
                responses.append(f"ℹ️ Você **já possui** {role.mention}.")
                continue

            # Capacidade (se configurada para este cargo)
            cap = ROLE_CAPS.get(role.id)
            if cap is not None:
                current = self._count_role_members(role)
                if current >= cap:
                    responses.append(f"❌ {role.mention}: **capacidade cheia** ({current}/{cap}).")
                    continue

            # Hierarquia e permissão do bot
            if me is None or not me.guild_permissions.manage_roles:
                responses.append(f"❌ {role.mention}: o bot **não possui** a permissão `Gerenciar Cargos`.")
                continue
            if role >= me.top_role:
                responses.append(f"❌ {role.mention}: está **acima/igual** ao cargo mais alto do bot.")
                continue

            # Tenta adicionar
            try:
                await member.add_roles(role, reason=f"Receber tag solicitado por {member} (ID {member.id})")
                responses.append(f"✅ {role.mention} **atribuído com sucesso**.")
            except discord.Forbidden:
                responses.append(f"❌ {role.mention}: permissão **negada** (Forbidden).")
            except discord.HTTPException:
                responses.append(f"❌ {role.mention}: falha de API (**HTTPException**). Tente novamente.")

        # 4) Resposta final (ephemeral no slash)
        ephemeral = getattr(ctx, "interaction", None) is not None
        if not responses:
            responses = ["ℹ️ Nenhuma alteração realizada."]
        await self._smart_send(ctx, "\n".join(responses), ephemeral=ephemeral)

    # ---------------- Autocomplete para slash ----------------
    @receber_tag.autocomplete("tags")
    async def receber_tag_autocomplete(self, interaction: discord.Interaction, current: str):
        if not interaction.guild:
            return []
        allowed = self._get_allowed_roles(interaction.guild)
        nomes = [r.name for r in allowed]
        if current:
            c = current.lower()
            nomes = [n for n in nomes if c in n.lower()]
        return [app_commands.Choice(name=n, value=n) for n in nomes[:20]]


async def setup(bot: commands.Bot):
    await bot.add_cog(ReceberTag(bot))