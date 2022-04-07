from discord.ext.commands.context import Context
from utils.result import Result
from discord.ext import commands
from utils.engines import CSEImQuery, CSEQuery, UDictQuery, WAlphaQuery, DuckQuery, KGraphQuery, JishoQuery
from utils.tools.chat import initNav


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.chargeableCheck = trackQueries(MAX_QUERIES)

    @commands.command(name='walpha', aliases=['wa', 'wolframalpha'], brief="query Wolfram Alpha", pass_context=True)
    async def walpha(self, context: Context, *queryTerms):
        
        result: Result = WAlphaQuery(queryTerms).fulfill()

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

        await context.send(embed = result.getPage(0))

    @commands.command(name="kpanel", aliases=['knowledgegraph', 'kgraph', 'kg', 'kp'], brief="query Google's Knowledge Graph", pass_context=True)
    async def kgraph(self, context, *queryTerms):

        result: Result = KGraphQuery(queryTerms).fulfill()

        await context.send(embed = result.getPage(0))

    @commands.command(name='image', aliases=['findimage', 'i'], brief='query Google Images (100 per day)', pass_context=True)
    async def imageSearch(self, context, *queryTerms):

        result: Result = CSEImQuery(queryTerms).fulfill()

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

        await context.send(embed = result.getPage(0))

    @commands.command(name="jisho", aliases=['j'], brief="query jisho.org to get japanese results", pass_context=True)
    async def jisho(self, context, *queryTerms):

        result: Result = JishoQuery(queryTerms).fulfill()

        await initNav(
            bot = self.bot,
            result = result,
            context = context,
            purpose = "jisho",
            timeout = 300
        )

    @commands.command(name="urban", aliases=['ud'], brief="search urban dictionary for definitions", pass_context=True)
    async def urban(self, context, *queryTerms):
        
        result: Result = UDictQuery(queryTerms).fulfill()

        await initNav(
            bot = self.bot,
            result = result,
            context = context,
            purpose = "urban dictionary",
            timeout = 300
        )

    @commands.command(name="search", aliases=['s'], brief="Search all engines", pass_context=True)
    async def search(self, context, *queryTerms):
        from utils.navigation import Navigator
        nav = Navigator(
            self.bot, [
                KGraphQuery(queryTerms),
                WAlphaQuery(queryTerms),
                DuckQuery(queryTerms),
                CSEQuery(queryTerms),
                CSEImQuery(queryTerms),
                JishoQuery(queryTerms),
                UDictQuery(queryTerms)
            ], "Search", 3000)
        
        await nav.send(context)

def setup(client):
    client.add_cog(Search(client))
