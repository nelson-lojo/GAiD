from discord.ext.commands.context import Context
from discord.ext import commands
from utils.engines import CSEImQuery, CSEQuery, UDictQuery, WAlphaQuery, DuckQuery, KGraphQuery, JishoQuery
from utils.navigation import Navigator

class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='walpha', aliases=['wa', 'wolframalpha'], brief="query Wolfram Alpha", pass_context=True)
    async def walpha(self, context: Context, *queryTerms):
        nav = Navigator(self.bot, [WAlphaQuery(queryTerms)], "walpha", 180)
        await nav.send(context)

    @commands.command(name='duck', aliases=['duckduckgo', 'd'], brief="query DuckDuckGo", pass_context=True)
    async def duckInstantAnswer(self, context, *queryTerms):
        nav = Navigator(self.bot, [DuckQuery(queryTerms)], "duckduckgo", 1)
        await nav.send(context)

    @commands.command(name="kpanel", aliases=['knowledgegraph', 'kgraph', 'kg', 'kp'], brief="query Google's Knowledge Graph", pass_context=True)
    async def kgraph(self, context, *queryTerms):
        nav = Navigator(self.bot, [KGraphQuery(queryTerms)], "kgraph", 1)
        await nav.send(context)

    @commands.command(name='image', aliases=['findimage', 'i'], brief='query Google Images (100 per day)', pass_context=True)
    async def imageSearch(self, context, *queryTerms):
        nav = Navigator(self.bot, [CSEImQuery(queryTerms)], "google image", 180)
        await nav.send(context)

    @commands.command(name="page", aliases=['findpage'], brief="query Google to list relevant pages (100 per day)", pass_context=True)
    async def findpage(self, context, *queryTerms):
        nav = Navigator(self.bot, [CSEQuery(queryTerms)], "google", 1)
        await nav.send(context)

    @commands.command(name="jisho", aliases=['j'], brief="query jisho.org to get japanese results", pass_context=True)
    async def jisho(self, context, *queryTerms):
        nav = Navigator(self.bot, [JishoQuery(queryTerms)], "jisho", 180)
        await nav.send(context)

    @commands.command(name="urban", aliases=['ud'], brief="search urban dictionary for definitions", pass_context=True)
    async def urban(self, context, *queryTerms):
        nav = Navigator(self.bot, [UDictQuery(queryTerms)], "urban dictionary", 180)
        await nav.send(context)

    @commands.command(name="search", aliases=['s'], brief="Search all engines", pass_context=True)
    async def search(self, context, *queryTerms):
        nav = Navigator(
            self.bot, [
                KGraphQuery(queryTerms),
                WAlphaQuery(queryTerms),
                DuckQuery(queryTerms),
                JishoQuery(queryTerms),
                UDictQuery(queryTerms),
                CSEImQuery(queryTerms),
                CSEQuery(queryTerms),
            ], "Search", 180)
        
        await nav.send(context)

async def setup(client):
    await client.add_cog(Search(client))
