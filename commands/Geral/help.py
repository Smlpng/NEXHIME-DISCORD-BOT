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

class HelpView(discord.ui.View):
    def __init__(self, ctx: commands.Context, grouped_commands: dict):
        super().__init__(timeout=120)
        self.ctx = ctx
        
        # Cria um botão para cada categoria detectada nas cogs
        for category_name, cmds in grouped_commands.items():
            # Define o emoji caso conheçamos a categoria, senão usa um emoji padrão
            emoji = EMOJIS_CATEGORIAS.get(category_name.capitalize(), "📁")
            
            btn = discord.ui.Button(
                label=f"{emoji} | {category_name}",
                style=discord.ButtonStyle.secondary
            )
            
            # Precisamos desse truque para isolar a variável no loop (closure)
            btn.callback = self.make_callback(category_name, cmds)
            self.add_item(btn)

    def make_callback(self, cat_name, cmds):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.ctx.author.id:
                await interaction.response.send_message("Apenas quem executou o comando pode usar estes botões.", ephemeral=True)
                return
            
            p_label = format_prefix_label(interaction.client, interaction.guild)

            emb = discord.Embed(
                title=f"Categoria: {cat_name}",
                description=f"Comandos da categoria **{cat_name}**.",
                color=discord.Color.blue(),
            )
            emb.add_field(name="Prefixo atual", value=p_label, inline=True)
            emb.add_field(name="Comandos", value=str(len(cmds)), inline=True)
            for command in cmds[:8]:
                emb.add_field(name=command.qualified_name, value=format_command_entry(command, p_label), inline=False)
            if len(cmds) > 8:
                emb.set_footer(text=f"Mostrando 8 de {len(cmds)} comandos desta categoria.")
            await interaction.response.edit_message(embed=emb, view=self)
        return callback


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
        prefix_label = format_prefix_label(self.bot, ctx.guild)

        embed = discord.Embed(
            title="Central de Comandos",
            description=(
                "Escolha uma categoria nos botões abaixo para ver detalhes de uso.\n"
                f"Prefixo atual neste servidor: **{prefix_label}**"
            ),
            color=discord.Color.green(),
        )
        embed.add_field(name="Prefixados", value=str(prefix_total), inline=True)
        embed.add_field(name="Categorias", value=str(len(sorted_grouped)), inline=True)
        categories_preview = "\n".join(
            f"{EMOJIS_CATEGORIAS.get(category.capitalize(), '📁')} **{category}**: {len(commands_list)}"
            for category, commands_list in sorted_grouped.items()
        )
        embed.add_field(name="Mapa rápido", value=categories_preview[:1024], inline=False)
        embed.set_footer(text="Dica: use o prefixo do servidor para executar comandos.")

        view = HelpView(ctx, sorted_grouped)

        await ctx.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    # O bot por padrão vem com um help. É bom remover pra podermos usar o nosso com o mesmo nome
    bot.remove_command("help")
    await bot.add_cog(Help(bot))
