from discord.ext import commands
from utils.engines import JishoQuery, UDictQuery
from utils.navigation import Navigator

class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="jisho", aliases=['j'], brief="query jisho.org to get japanese results", pass_context=True)
    async def jisho(self, context, *queryTerms):
        nav = Navigator(self.bot, [JishoQuery(queryTerms)], "jisho", 180)
        await nav.send(context)

    @commands.command(name="urban", aliases=['ud'], brief="search urban dictionary for definitions", pass_context=True)
    async def urban(self, context, *queryTerms):
        nav = Navigator(self.bot, [UDictQuery(queryTerms)], "urban dictionary", 180)
        await nav.send(context)
    
    @commands.command(name="define", aliases=['d', 'def'], brief="Look up a definition using all dictionaries", pass_context=True)
    async def search(self, context, *queryTerms):
        nav = Navigator(
            self.bot, [
                JishoQuery(queryTerms),
                UDictQuery(queryTerms),
            ], "Definition", 180)
        
        await nav.send(context)

def setup(client):
    client.add_cog(Dictionary(client))