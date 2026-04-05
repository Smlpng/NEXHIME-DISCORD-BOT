import discord
from discord.ext import commands
import re

def get_prefixes_from_client(client: commands.Bot, guild: discord.Guild | None):
    default_prefix = getattr(client, "default_prefix", "n!")
    prefixes = getattr(client, "prefix_cache", None)
    if prefixes is None:
        prefixes = getattr(client, "prefixes_cache", {}) or {}
    effective_prefix = prefixes.get(str(guild.id), default_prefix) if guild else default_prefix
    return default_prefix, effective_prefix

def format_prefix_label(client: commands.Bot, guild: discord.Guild | None) -> str:
    default_prefix, effective_prefix = get_prefixes_from_client(client, guild)
    if effective_prefix == default_prefix:
        return f"[{default_prefix}]"
    return f"[{default_prefix}] {effective_prefix}"

# Associa ícones (emojis) às categorias conhecidas
EMOJIS_CATEGORIAS = {
    "Geral": "📚",
    "Entretenimento": "🕹️",
    "Moderação": "👮",
    "Economia": "💰",
    "RPG": "⚔️",
}
PAGE_SIZE = 10

def get_command_category(cmd: commands.Command) -> str:
    if not cmd.cog:
        return "Outros"

    mod_parts = cmd.cog.__module__.split('.')

    if len(mod_parts) > 1 and len(mod_parts) > 2 and mod_parts[1].lower() == "rpg":
        return "RPG"

    if len(mod_parts) > 1:
        raw_cat = mod_parts[-2]
        clean_cat = re.sub(r'^\d+[\._]\s*', '', raw_cat)
        return clean_cat.replace('_', ' ')

    return "Outros"

def format_command_entry(cmd: commands.Command, prefix_label: str) -> str:
    prefix_example = f"{prefix_label} {cmd.qualified_name}"
    aliases = ", ".join(cmd.aliases[:3]) if getattr(cmd, "aliases", None) else "Sem aliases"
    description = cmd.description or getattr(cmd, "short_doc", "Sem descrição")
    return (
        f"**{cmd.qualified_name}**\n"
        f"Prefixo: `{prefix_example}`\n"
        f"Aliases: {aliases}\n"
        f"Descrição: {description}"
    )


def build_home_embed(bot: commands.Bot, guild: discord.Guild | None, grouped_commands: dict[str, list[commands.Command]], prefix_total: int) -> discord.Embed:
    prefix_label = format_prefix_label(bot, guild)
    embed = discord.Embed(
        title="Central de Comandos",
        description=(
            "Escolha uma categoria nos botões abaixo para ver detalhes de uso.\n"
            f"Prefixo atual neste servidor: **{prefix_label}**"
        ),
        color=discord.Color.green(),
    )
    embed.add_field(name="Prefixados", value=str(prefix_total), inline=True)
    embed.add_field(name="Categorias", value=str(len(grouped_commands)), inline=True)
    categories_preview = "\n".join(
        f"{EMOJIS_CATEGORIAS.get(category.capitalize(), '📁')} **{category}**: {len(commands_list)}"
        for category, commands_list in grouped_commands.items()
    )
    embed.add_field(name="Mapa rápido", value=categories_preview[:1024], inline=False)
    embed.set_footer(text="Dica: use o prefixo do servidor para executar comandos.")
    return embed


def build_category_embed(
    bot: commands.Bot,
    guild: discord.Guild | None,
    category_name: str,
    cmds: list[commands.Command],
    page_index: int,
) -> discord.Embed:
    prefix_label = format_prefix_label(bot, guild)
    total_pages = max(1, (len(cmds) + PAGE_SIZE - 1) // PAGE_SIZE)
    safe_page_index = max(0, min(page_index, total_pages - 1))
    start = safe_page_index * PAGE_SIZE
    end = start + PAGE_SIZE
    page_commands = cmds[start:end]

    embed = discord.Embed(
        title=f"Categoria: {category_name}",
        description=f"Comandos da categoria **{category_name}**.",
        color=discord.Color.blue(),
    )
    embed.add_field(name="Prefixo atual", value=prefix_label, inline=True)
    embed.add_field(name="Comandos", value=str(len(cmds)), inline=True)
    embed.add_field(name="Página", value=f"{safe_page_index + 1}/{total_pages}", inline=True)

    for command in page_commands:
        embed.add_field(name=command.qualified_name, value=format_command_entry(command, prefix_label), inline=False)

    shown_from = start + 1 if page_commands else 0
    shown_to = start + len(page_commands)
    embed.set_footer(text=f"Mostrando {shown_from}-{shown_to} de {len(cmds)} comandos.")
    return embed

class HelpView(discord.ui.View):
    def __init__(self, ctx: commands.Context, grouped_commands: dict[str, list[commands.Command]], prefix_total: int):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.grouped_commands = grouped_commands
        self.prefix_total = prefix_total
        self.current_category: str | None = None
        self.current_page = 0
        self._build_home_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Apenas quem executou o comando pode usar estes botões.", ephemeral=True)
            return False
        return True

    def _build_home_buttons(self) -> None:
        self.clear_items()
        for category_name in self.grouped_commands:
            emoji = EMOJIS_CATEGORIAS.get(category_name.capitalize(), "📁")
            btn = discord.ui.Button(
                label=f"{emoji} | {category_name}",
                style=discord.ButtonStyle.secondary
            )

            async def callback(interaction: discord.Interaction, category=category_name):
                await self.show_category(interaction, category, 0)

            btn.callback = callback
            self.add_item(btn)

    def _build_category_buttons(self, category_name: str, total_pages: int) -> None:
        self.clear_items()

        back_button = discord.ui.Button(label="Voltar", style=discord.ButtonStyle.primary, row=0)

        async def back_callback(interaction: discord.Interaction):
            await self.show_home(interaction)

        back_button.callback = back_callback
        self.add_item(back_button)

        for page_index in range(total_pages):
            page_button = discord.ui.Button(
                label=str(page_index + 1),
                style=discord.ButtonStyle.success if page_index == self.current_page else discord.ButtonStyle.secondary,
                disabled=page_index == self.current_page,
                row=1 + (page_index // 5),
            )

            async def page_callback(interaction: discord.Interaction, target_page=page_index):
                await self.show_category(interaction, category_name, target_page)

            page_button.callback = page_callback
            self.add_item(page_button)

    async def show_home(self, interaction: discord.Interaction) -> None:
        self.current_category = None
        self.current_page = 0
        self._build_home_buttons()
        embed = build_home_embed(self.ctx.bot, self.ctx.guild, self.grouped_commands, self.prefix_total)
        await interaction.response.edit_message(embed=embed, view=self)

    async def show_category(self, interaction: discord.Interaction, category_name: str, page_index: int) -> None:
        cmds = self.grouped_commands[category_name]
        self.current_category = category_name
        self.current_page = page_index
        total_pages = max(1, (len(cmds) + PAGE_SIZE - 1) // PAGE_SIZE)
        self._build_category_buttons(category_name, total_pages)
        embed = build_category_embed(self.ctx.bot, self.ctx.guild, category_name, cmds, page_index)
        await interaction.response.edit_message(embed=embed, view=self)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._seen_prefix_help_message_ids: set[int] = set()

    @commands.command(
        name="help",
        help="Exibe as categorias e comandos disponíveis (Dinâmico)."
    )
    async def help(self, ctx: commands.Context):
        # Guard: se o mesmo message.id disparar o comando mais de uma vez no mesmo processo,
        # evita enviar o embed repetido.
        if not ctx.interaction and getattr(ctx, "message", None) is not None:
            mid = getattr(ctx.message, "id", None)
            if isinstance(mid, int):
                if mid in self._seen_prefix_help_message_ids:
                    return
                self._seen_prefix_help_message_ids.add(mid)

        # Agrupa os comandos de acordo com a pasta (módulo) em que a Cog se encontra
        grouped_commands = {}
        unique_commands = {}

        for cmd in self.bot.walk_commands():
            if cmd.hidden:
                continue
            unique_commands.setdefault(cmd.qualified_name, cmd)

        for cmd in unique_commands.values():
            category = get_command_category(cmd)
            grouped_commands.setdefault(category, []).append(cmd)

        # Ordena em ordem alfabética as categorias e os comandos dentro delas
        sorted_grouped = {k: sorted(v, key=lambda c: c.name) for k, v in sorted(grouped_commands.items())}
        prefix_total = len(unique_commands)
        embed = build_home_embed(self.bot, ctx.guild, sorted_grouped, prefix_total)
        view = HelpView(ctx, sorted_grouped, prefix_total)

        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    # O bot por padrão vem com um help. É bom remover pra podermos usar o nosso com o mesmo nome
    bot.remove_command("help")
    await bot.add_cog(Help(bot))
