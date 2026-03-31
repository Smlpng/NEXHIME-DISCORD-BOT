import discord
from discord.ext import commands
import random

class Fatos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fatos = fatos = [
    "As abelhas têm um tipo de cabelo nos olhos!",
    "O coração de uma camarão está localizado na cabeça.",
    "Os golfinhos têm nomes para os outros golfinhos.",
    "Você sabia que o maior animal terrestre é o elefante africano?",
    "O sol é 400 vezes maior que a lua, mas também está 400 vezes mais distante da Terra, por isso parecem ter o mesmo tamanho no céu.",
    "O som viaja quatro vezes mais rápido na água do que no ar.",
    "As girafas têm a língua roxa para evitar queimaduras ao comer folhas de árvores altas.",
    "A lua está se afastando da Terra cerca de 3,8 centímetros por ano.",
    "O polvo tem três corações, sendo dois para bombear sangue para as brânquias e um para o restante do corpo.",
    "O camelo pode beber até 200 litros de água em um curto espaço de tempo.",
    "Os flamingos não nascem com a cor rosa; eles são inicialmente brancos ou cinzentos e vão adquirindo a cor ao se alimentarem de algas e crustáceos.",
    "O chocolate era usado como moeda pelos povos antigos, como os astecas e os maias.",
    "O maior deserto do mundo não é o Saara, mas a Antártida, que é um deserto gelado.",
    "As abelhas têm 5 olhos: dois compostos e três simples no topo da cabeça.",
    "O corpo humano tem 206 ossos, mas ao nascer, o bebê tem cerca de 270 ossos, alguns dos quais se fundem conforme ele cresce.",
    "O maior animal do planeta, a baleia azul, pode pesar até 180 toneladas, o que equivale a cerca de 30 elefantes.",
    "Os morcegos são os únicos mamíferos que podem voar.",
    "A maior parte da poeira no ar vem de terras desérticas, mas também inclui células de pele humana morta.",
    "A primeira invenção do telefone foi feita por Alexander Graham Bell, mas ele também inventou o primeiro dispositivo para detectar fumaça.",
    "A torre de Pisa, famosa por sua inclinação, começou a se inclinar enquanto ainda estava sendo construída, devido a um solo instável.",
    "O cérebro humano é mais ativo enquanto estamos dormindo do que quando estamos acordados.",
    "As lulas gigantes podem alcançar até 13 metros de comprimento.",
    "Os pinguins são aves, mas não sabem voar; em vez disso, eles são excelentes nadadores.",
    "Existem mais árvores na Terra do que estrelas na Via Láctea.",
    "O sol libera mais energia em um segundo do que toda a humanidade usou em sua história até hoje."
]


    @commands.command(name="fato", aliases=["fact"], help="Envia um fato curioso ou engraçado.")
    async def fato(self, ctx: commands.Context):
        """Envia um fato curioso ou engraçado."""
        fato = random.choice(self.fatos)
        await ctx.reply(f"Fato curioso: {fato}", mention_author=False)

async def setup(bot):
    await bot.add_cog(Fatos(bot))
