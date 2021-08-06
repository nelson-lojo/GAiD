from discord.ext.commands.context import Context
from utils.result import Result
from discord.ext import commands
from utils.engines import CSEImQuery, CSEQuery, WAlphaQuery, DuckQuery, KGraphQuery, JishoQuery
from utils.tools.chat import initNav


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.chargeableCheck = trackQueries(MAX_QUERIES)

    @commands.command(name='walpha', aliases=['wa', 'wolframalpha'], brief="query Wolfram Alpha", pass_context=True)
    async def walpha(self, context: Context, *queryTerms):
        
        result: Result = WAlphaQuery(queryTerms).fulfill()

        if result.success is False:
            await result.showFail(context)
            return

        await initNav(
            bot = self.bot,
            result = result,
            context = context,
            purpose = "walpha",
            timeout = 30
        )

    @commands.command(name='duck', aliases=['duckduckgo', 'd'], brief="query DuckDuckGo", pass_context=True)
    async def duckInstantAnswer(self, context, *queryTerms):
        
        result: Result = DuckQuery(queryTerms).fulfill()

        if result.success is False:
            await result.showFail(context)
            return

        await context.send(embed = result.getPage(0))

    @commands.command(name="kpanel", aliases=['knowledgegraph', 'kgraph', 'kg', 'kp'], brief="query Google's Knowledge Graph", pass_context=True)
    async def kgraph(self, context, *queryTerms):

        result: Result = KGraphQuery(queryTerms).fulfill()

        if result.success is False:
            await result.showFail(context)
            return

        await context.send(embed = result.getPage(0))

    @commands.command(name='image', aliases=['findimage', 'i'], brief='query Google Images (100 per day)', pass_context=True)
    async def imageSearch(self, context, *queryTerms):

        result: Result = CSEImQuery(queryTerms).fulfill()
        
        if result.success is False:
            await result.showFail(context)
            return

        await initNav(
            bot = self.bot,
            result = result,
            context = context,
            purpose = "image",
            timeout = 30
        )

    @commands.command(name="page", aliases=['findpage'], brief="query Google to list relevant pages (100 per day)", pass_context=True)
    async def findpage(self, context, *queryTerms):

        result: Result = CSEQuery(queryTerms).fulfill()

        if result.success is False:
            await result.showFail(context)
            return

        await context.send(embed = result.getPage(0))

    @commands.command(name="jisho", aliases=['j'], brief="query jisho.org to get japanese results", pass_context=True)
    async def jisho(self, context, *queryTerms):

        result: Result = JishoQuery(queryTerms).fulfill()

        if result.success is False:
            await result.showFail(context)
            return

        await initNav(
            bot = self.bot,
            result = result,
            context = context,
            purpose = "jisho",
            timeout = 300
        )


def setup(client):
    client.add_cog(Search(client))
