import json
from datetime import date
from pathlib import Path

import discord
from discord.ext import commands


DB_PATH = Path("DataBase") / "quiz_diario.json"
QUESTIONS = [
    {
        "question": "Qual comando mostra a latencia atual do bot?",
        "options": ["ping", "uptime", "invite", "avatar"],
        "answer": "A",
    },
    {
        "question": "Qual recurso do RPG serve como moeda principal?",
        "options": ["Madeira", "Runas", "Nex", "Ferro"],
        "answer": "C",
    },
    {
        "question": "Qual comando de moderacao registra avisos?",
        "options": ["lock", "warn", "mute", "prefix"],
        "answer": "B",
    },
    {
        "question": "Qual comando do RPG mostra o inventario do heroi?",
        "options": ["equip", "inventory", "forge", "raid"],
        "answer": "B",
    },
    {
        "question": "Qual comando gera imagem estilo cartaz de procurado?",
        "options": ["wanted", "tweet", "ascii", "meme"],
        "answer": "A",
    },
]


def _load() -> dict:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        DB_PATH.write_text(json.dumps({"answers": {}, "scores": {}}, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        data = json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {"answers": {}, "scores": {}}
    data.setdefault("answers", {})
    data.setdefault("scores", {})
    return data


def _save(data: dict) -> None:
    tmp = DB_PATH.with_suffix(DB_PATH.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DB_PATH)


def _today_key() -> str:
    return date.today().isoformat()


def _get_today_question() -> dict:
    index = date.today().toordinal() % len(QUESTIONS)
    return QUESTIONS[index]


class QuizDiario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quizdiario", aliases=["dailyquiz"])
    async def quizdiario(self, ctx: commands.Context, acao: str | None = None):
        """Mostra a pergunta do dia ou responde ao quiz diario."""
        data = _load()
        today = _today_key()
        question = _get_today_question()
        action = (acao or "").strip().upper()

        if not action:
            embed = discord.Embed(title="Quiz diario", description=question["question"], color=discord.Color.blurple())
            letters = ["A", "B", "C", "D"]
            embed.add_field(
                name="Alternativas",
                value="\n".join(f"**{letter}.** {option}" for letter, option in zip(letters, question["options"])),
                inline=False,
            )
            embed.set_footer(text="Responda com quizdiario A, B, C ou D. Vale 1 ponto por dia.")
            return await ctx.reply(embed=embed, mention_author=False)

        if action not in {"A", "B", "C", "D"}:
            return await ctx.reply("Use quizdiario para ver a pergunta ou quizdiario <A|B|C|D> para responder.", mention_author=False)

        answers = data["answers"].setdefault(today, {})
        if str(ctx.author.id) in answers:
            return await ctx.reply("Voce ja respondeu o quiz de hoje.", mention_author=False)

        correct = action == question["answer"]
        answers[str(ctx.author.id)] = action
        if correct:
            data["scores"][str(ctx.author.id)] = int(data["scores"].get(str(ctx.author.id), 0)) + 1
        _save(data)

        if correct:
            score = data["scores"][str(ctx.author.id)]
            return await ctx.reply(f"Resposta correta. Sua pontuacao total no quiz diario agora e {score}.", mention_author=False)
        return await ctx.reply(f"Resposta errada. A resposta correta de hoje era {question['answer']}.", mention_author=False)


async def setup(bot):
    await bot.add_cog(QuizDiario(bot))